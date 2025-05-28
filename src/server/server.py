import json
import os
from typing import Any, Dict, Optional
import logging

from utils.camera_settings_validator import CameraSettingsValidator
from utils.model_settings_validator import ModelSettingsValidator
import uvicorn
from fastapi import FastAPI, Response

from utils.logger import setup_logger
from .models import ObjectPhoto, Receiver, Settings
from pydantic_core import from_json


from database.DatabaseManager import DatabaseManager
from server.image_util import show_boxes

# Initialize the FastAPI app
app = FastAPI()

# Global variable to hold the database connection
db_conn = None

# Set up logging for the application
setup_logger(__name__)


@app.get("/settings/{rcv}")
async def get_settings(rcv: Receiver, response: Response) -> Optional[Settings]:
    """
    Retrieve the settings for the specified receiver.

    Args:
        rcv (Receiver): The type of receiver (either "camera" or "model").
        response (Response): The response object for setting the HTTP status code.

    Returns:
        Settings or None: The settings for the receiver if found, otherwise None.
    """
    logging.info("Requested settings for receiver: %s", rcv)

    settings_file_path = f"settings/{rcv.value}_settings.json"
    if not os.path.exists(settings_file_path):
        response.status_code = 422
        logging.debug(f"Settings file {settings_file_path} not found.")
        return None
    with open(settings_file_path, "r") as settings_file:
        settings: Dict[Any, Any] = from_json(
            "\n".join(settings_file.readlines()))

    logging.debug(f"Settings file opened successfully for receiver {rcv}")

    value_list = {}
    value_list["receiver"] = rcv
    settings_list = []

    for (key, value) in settings.items():
        settings_list.append({"key": key, "value": value})

    value_list["settings"] = settings_list

    return Settings(**value_list)


def check_rcv_type(x: Dict[str, Any], rcv: Receiver) -> bool:
    """
    Helper function to check if the receiver in a given dictionary matches the expected receiver.

    Args:
        x (Dict[str, Any]): The dictionary representing the settings.
        rcv (Receiver): The expected receiver type.

    Returns:
        bool: True if the receiver matches, False otherwise.
    """
    return x["receiver"] == rcv


@app.get("/object/{name}")
async def get_object(name: str) -> Optional[ObjectPhoto]:
    """
    Retrieve the object with the given name from the database and return the image with bounding boxes.

    Args:
        name (str): The name of the object.

    Returns:
        ObjectPhoto or None: The object image with bounding boxes if found, otherwise None.
    """
    logging.info(f"Requested object: {name}")
    result = db_conn.get_latest_object_by_name(name)

    if result is None:
        logging.debug("No object found in the database.")
        return None

    result = result["Object"]

    logging.debug(f"Object found: {result}")

    return show_boxes([result["Name"]],
                      [result["PhotoPath"]],
                      [result["PositionCoord"]])


@app.get("/objects/")
async def get_objects() -> Optional[ObjectPhoto]:
    """
    Retrieve all objects from the database and return the images with bounding boxes.

    Returns:
        ObjectPhoto or None: The images with bounding boxes for all objects if found, otherwise None.
    """
    logging.info("Requested all objects")
    result = db_conn.get_all_objects()

    if result is None:
        logging.debug("No objects found in the database.")
        return None

    names = [r["Object"]["Name"] for r in result]
    paths = [r["Object"]["PhotoPath"] for r in result]
    coords = [r["Object"]["PositionCoord"] for r in result]

    logging.debug(
        f"Objects found: names: {names}, paths: {paths}, coords: {coords}")

    return show_boxes(names, paths, coords)


@app.post("/settings/")
async def change_settings(new_settings: Settings, response: Response):
    """
    Update the settings for the specified receiver.

    Args:
        new_settings (Settings): The new settings to be applied.
        response (Response): The response object for setting the HTTP status code.

    Returns:
        None
    """
    logging.info("Requested to change settings")
    settings_file_path = f"settings/{new_settings.receiver.value}_settings.json"

    with open(settings_file_path, "r") as settings_file:
        cur_settings: Dict[Any, Any] = from_json(
            "\n".join(settings_file.readlines()))

    # Get the names of current settings
    name_set = list(map(lambda x: x, cur_settings))
    logging.debug(f"Current settings: {name_set}")
    
    # Validation
    old_rtsp = None
    if new_settings.receiver.value == "camera":
        validator = CameraSettingsValidator()
        old_rtsp = cur_settings["rtsp_url"]
    else:
        validator = ModelSettingsValidator()
        
    fields = {}
    
    for key, value in cur_settings.items():
        fields[key] = value

    for new_setting_pair in new_settings.settings:
        if new_setting_pair.key not in name_set:
            logging.debug(
                f"Setting {new_setting_pair.key} not found in current settings.")
            response.status_code = 422
            return None
        bar = getattr(validator, f'validate_{new_setting_pair.key}')
        valid_count, err = bar(new_setting_pair.value)
        
        if not valid_count:
            logging.debug(f"Error while validating settings: {err}")
            response.status_code = 421
            return None
        
        cur_settings[new_setting_pair.key] = new_setting_pair.value
        fields[new_setting_pair.key] = new_setting_pair.value

        logging.debug(
            f"Changed setting {new_setting_pair.key} \
                to {new_setting_pair.value}")
    if isinstance(validator, CameraSettingsValidator):
        new_rtsp_url = list(filter(lambda x: x.key == "rtsp_url", new_settings.settings))
        if new_rtsp_url == []:
            new_rtsp_url = None
        else:
            new_rtsp_url = new_rtsp_url[0]
        
        logging.info(fields)
        logging.info(new_rtsp_url)
        if new_rtsp_url is not None:
            fields = validator.update_fields_from_rtsp(fields)
        else:
            fields = validator.update_rtsp_from_fields(fields)
        
        logging.info(fields)

    with open(f"settings/{new_settings.receiver.value}_settings.json", "w") \
            as settings_file:
        settings_file.write(json.dumps(fields))
        logging.info(f"Settings updated for receiver {new_settings.receiver}")


def run_server(db_path: str = ""):
    """
    Start the FastAPI server and connect to the database.

    Args:
        db_path (str): Path to the database file.
    """
    global db_conn

    logging.info("Starting server...")

    db_conn = DatabaseManager(db_path)

    logging.info("Connected to the database.")

    uvicorn.run(app, host="127.0.0.1", port=19841)


if __name__ == "__main__":
    run_server("../data_db/database.db")
