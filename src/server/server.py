import json
import os
from typing import Any, Dict, Optional
import logging

import uvicorn
from fastapi import FastAPI, Response
from .models import ObjectPhoto, Receiver, Settings
from pydantic_core import from_json


from database.DatabaseManager import DatabaseManager
from server.image_util import show_boxes

app = FastAPI()
db_conn = None

logging.getLogger(__name__)
logging.basicConfig(
    filename="server_logs.txt",
    filemode='a',
    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)


@app.get("/settings/{rcv}")
async def get_settings(rcv: Receiver, response: Response) \
        -> Optional[Settings]:
    logging.info("Asked for settings")
    if not os.path.exists(f"settings/settings_{rcv}.json"):
        response.status_code = 422
        logging.debug("File with settings was not found")
        return None

    with open(f"settings/settings_{rcv}.json", "r") as settings_file:
        settings: Dict[Any, Any] = from_json(
            "\n".join(settings_file.readlines()))

    logging.debug("Opened settings file successfully")

    return Settings(**settings)


def check_rcv_type(x: Dict[str, Any], rcv: Receiver) -> bool:
    return x["receiver"] == rcv


@app.get("/object/{name}")
async def get_object(name: str) -> Optional[ObjectPhoto]:
    logging.info(f"Asked where {name} is")
    result = db_conn.get_latest_object_by_name(name)

    if result is None:
        logging.debug("DB query result was None")
        return None

    result = result["Object"]

    logging.debug(f"DB query result was {result}")

    return show_boxes([result["Name"]],
                      [result["PhotoPath"]],
                      [result["PositionCoord"]])


@app.get("/objects/")
async def get_objects() -> Optional[ObjectPhoto]:
    logging.info("Asked for the current state")

    result = db_conn.get_all_objects()

    if result is None:
        logging.debug("DB query result was None")
        return

    names = [r["Object"]["Name"] for r in result]
    paths = [r["Object"]["PhotoPath"] for r in result]
    coords = [r["Object"]["PositionCoord"] for r in result]

    logging.debug(
        f"DB query result was:\n\
            names: {names}\n\
            paths: {paths}\n\
            coords: {coords}")

    return show_boxes(names,
                      paths,
                      coords)


@app.post("/settings/")
async def change_settings(new_settings: Settings, response: Response):
    logging.info("Asked to change settings")
    with open(f"settings/settings_{new_settings.receiver}.json", "r") \
            as settings_file:
        cur_settings: Dict[Any, Any] = from_json(
            "\n".join(settings_file.readlines()))

    name_set = list(map(lambda x: x["key"], cur_settings["settings"]))
    print(name_set)

    for new_setting_pair in new_settings.settings:
        if new_setting_pair.key not in name_set:
            logging.debug(
                f"Setting {new_setting_pair.key} was not found in settings")
            response.status_code = 422
            return None

        setting_index: int = list(filter(  # type: ignore
            lambda i: cur_settings["settings"][i]["key"] ==
            new_setting_pair.key,
            range(len(cur_settings["settings"])))  # type: ignore
        )[0]

        cur_settings["settings"][setting_index]["value"] = \
            new_setting_pair.value

        logging.debug(
            f"Changed setting {new_setting_pair.key} \
                to {new_setting_pair.value}")

    with open(f"settings/settings_{new_settings.receiver}.json", "w") \
            as settings_file:
        settings_file.write(json.dumps(cur_settings))


def run_server(db_path: str = ""):
    global db_conn

    logging.info("Starting server...")

    db_conn = DatabaseManager(db_path)

    logging.info("Connected to db")

    uvicorn.run(app, host="127.0.0.1", port=19841)


if __name__ == "__main__":
    run_server("../data_db/database.db")
