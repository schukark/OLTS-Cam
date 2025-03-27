from fastapi import FastAPI
from models import Settings, ObjectPhoto, Receiver
from pydantic_core import from_json
import uvicorn

app = FastAPI()

@app.get("/settings/{rcv}")
async def get_settings(rcv: Receiver):
    with open("settings.json", "r") as settings_file:
        settings = from_json("\n".join(settings_file.readlines()))
    return settings


@app.get("/object/{name}")
async def get_object(name: str):
    return ObjectPhoto(height=224, width=224, image="aboba")


@app.post("/settings/")
async def change_settings(new_settings: Settings):
    with open("settings.json", "r") as settings_file:
        cur_settings = from_json("\n".join(settings_file.readlines())).dict()

    for i in range(len(cur_settings["settings"])):
        rcv_settings: Settings = cur_settings["settings"][i]

        if rcv_settings.receiver != new_settings.receiver:
            continue

        cur_settings["settings"][i] = new_settings.settings

    with open("settings.json", "w") as settings_file:
        settings_file.write(Settings(**cur_settings).model_dump_json)

uvicorn.run(app, host="127.0.0.1", port=19841)
