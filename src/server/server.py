import json
import os
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, Response
from models import ObjectPhoto, Receiver, Settings
from pydantic_core import from_json

app = FastAPI()


@app.get("/settings/{rcv}")
async def get_settings(rcv: Receiver, response: Response) \
        -> Optional[Settings]:
    if not os.path.exists(f"settings/settings_{rcv}.json"):
        response.status_code = 422
        return None

    with open(f"settings/settings_{rcv}.json", "r") as settings_file:
        settings: Dict[Any, Any] = from_json(
            "\n".join(settings_file.readlines()))

    return Settings(**settings)


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
    with open(f"settings/settings_{new_settings.receiver}.json", "r") \
            as settings_file:
        cur_settings: Dict[Any, Any] = from_json(
            "\n".join(settings_file.readlines()))

    name_set = list(map(lambda x: x["key"], cur_settings["settings"]))
    print(name_set)

    for new_setting_pair in new_settings.settings:
        if new_setting_pair.key not in name_set:
            response.status_code = 422
            return None

        setting_index: int = list(filter(  # type: ignore
            lambda i: cur_settings["settings"][i]["key"] ==
            new_setting_pair.key,
            range(len(cur_settings["settings"])))  # type: ignore
        )[0]

        cur_settings["settings"][setting_index]["value"] = \
            new_setting_pair.value

    with open(f"settings/settings_{new_settings.receiver}.json", "w") \
            as settings_file:
        settings_file.write(json.dumps(cur_settings))


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=19841)


if __name__ == "__main__":
    run_server()
