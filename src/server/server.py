import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Response
from models import Settings, ObjectPhoto, Receiver
from pydantic_core import from_json
import uvicorn

app = FastAPI()


@app.get("/settings/{rcv}")
async def get_settings(rcv: Receiver, response: Response) \
        -> Optional[Settings]:
    with open("settings.json", "r") as settings_file:
        settings: Dict[str, List[Any]] = from_json(
            "\n".join(settings_file.readlines()))
    result = list(filter(lambda x: check_rcv_type(x, rcv),
                         settings["settings"]))

    if len(result) == 0:
        response.status_code = 422
        return None

    return result[0]


def check_rcv_type(x: Dict[str, Any], rcv: Receiver) -> bool:
    return x["receiver"] == rcv


@app.get("/object/{name}")
async def get_object(name: str):
    with open("test_image.txt", "r") as file_contents:
        test_image = file_contents.readline()
    return ObjectPhoto(height=224, width=224, image=test_image)


@app.get("/objects/")
async def get_objects():
    with open("test_image2.txt", "r") as file_contents:
        test_image = file_contents.readline()
    return ObjectPhoto(height=224, width=224, image=test_image)


@app.post("/settings/")
async def change_settings(new_settings: Settings, response: Response):
    with open("settings.json", "r") as settings_file:
        cur_settings = from_json(
            "\n".join(settings_file.readlines()))

    found_rcv = False

    for json_row in cur_settings["settings"]:
        if json_row["receiver"] != new_settings.receiver:
            continue

        found_rcv = True
        for set_row in new_settings.settings:
            key = set_row.key
            value = set_row.value

            if key not in list(map(lambda x: x["key"], json_row["settings"])):
                response.status_code = 401
                return

            for row in json_row["settings"]:
                if row["key"] == key:
                    row["value"] = value
                    break

    if not found_rcv:
        response.status_code = 422
        return

    with open("settings.json", "w") as settings_file:
        settings_file.write(json.dumps(cur_settings))


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=19841)


if __name__ == "__main__":
    run_server()
