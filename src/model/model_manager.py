# model_manager.py
import hashlib
import json
import logging
import threading
from pathlib import Path
from datetime import datetime

from PySide6.QtGui import QImage

from model.model_runner import ModelRunner
from database.tables.ObjectItem import ObjectItem

from utils.logger import setup_logger

setup_logger(__name__)


class ModelManager:
    """
    Manages the lifecycle of the model runner, including settings validation,
    initialization, frame processing, and database writing.

    Attributes:
        REQUIRED_SETTINGS (list): List of mandatory settings keys.
    """
    REQUIRED_SETTINGS = [
        "rtsp_url",
        "fps",
        "nms_thresh",
        "score_thresh",
        "detections_per_image",
        "save_folder"
    ]

    def __init__(self):
        """
        Initializes the ModelManager with default values and updates settings.
        """
        self._current_runner = None
        self.error_msg = None
        self.image1 = None
        self.image2 = None
        self._current_settings_hash = None
        self.reconnect = False
        self._lock = threading.Lock()
        self.update_settings()

    def _get_settings_hash(self, settings):
        """Creates a hash of the current settings for comparison."""
        settings_str = json.dumps(settings, sort_keys=True)
        return hashlib.md5(settings_str.encode()).hexdigest()

    def _check_settings_changed(self):
        """
        Checks if settings have changed.

        Returns:
            tuple: (bool: changed, dict: new_settings, str: new_hash)
        """
        new_settings = self._get_settings()
        if new_settings is None:
            return False, None, None
        new_hash = self._get_settings_hash(new_settings)
        return new_hash != self._current_settings_hash, new_settings, new_hash

    def _validate_settings(self, settings):
        """
        Validates if all required settings are present.

        Args:
            settings (dict): Settings to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not settings:
            self.error_msg = "Settings not found"
            return False

        missing = [key for key in self.REQUIRED_SETTINGS if key not in settings]
        if missing:
            self.error_msg = f"Missing required settings: {', '.join(missing)}"
            return False

        return True

    def _create_runner_with_timeout(self, settings):
        """
        Creates the ModelRunner with a timeout of 5 seconds.

        Args:
            settings (dict): The settings to initialize the runner.

        Returns:
            tuple: (ModelRunner instance or None, error message or None)
        """
        if not self._validate_settings(settings):
            return None, self.error_msg

        runner = None
        error = None

        def target():
            nonlocal runner, error
            try:
                runner = ModelRunner(settings)
                if runner.error_msg is not None:
                    error = runner.error_msg
                    runner.release()
                    runner = None
            except Exception as e:
                error = f"Model initialization error: {str(e)}"

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=5)

        if thread.is_alive():
            self.reconnect = True
            error = "Camera connection timed out (5 seconds)"
            if runner is not None:
                runner.release()
            return None, error

        if runner is None and error is None:
            self.reconnect = True
            error = "Failed to connect to the video stream"

        return runner, error

    def update_settings(self):
        """
        Updates the settings and recreates the ModelRunner if needed.
        """
        #logging.info("Update settings called")
        with self._lock:
            settings_changed, new_settings, new_hash = self._check_settings_changed()

            if not self.reconnect and not settings_changed and \
                    self._current_runner is not None:
                logging.debug("Nothing to update")
                return

            if self._current_runner is not None:
                self._current_runner.release()
                self._current_runner = None
                logging.debug("Released previous runner")

            if new_settings is None:
                return

            self._current_settings_hash = new_hash

            self._current_runner, error = self._create_runner_with_timeout(new_settings)

            if self._current_runner is None:
                rtsp_url = new_settings.get("rtsp_url", "unknown URL")
                self.error_msg = (f"Failed to connect to the camera at: {rtsp_url}\n"
                                  f"Reason: {error}")
                self.reconnect = True
                return

            logging.debug("Runner created successfully")
            self.error_msg = None

    def _get_settings(self):
        """
        Loads and combines camera and model settings from JSON files.

        Returns:
            dict or None: Combined settings or None if error occurs.
        """
        try:
            settings_dir = Path(__file__).parent.parent.parent / "settings"
            camera_settings_path = settings_dir / "camera_settings.json"
            model_settings_path = settings_dir / "model_settings.json"

            if not settings_dir.exists():
                self.error_msg = "Settings directory not found"
                return None

            settings = {}

            def read_json_utf8(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except UnicodeDecodeError:
                    with open(path, 'r', encoding='cp1251') as f:
                        return json.load(f)

            if camera_settings_path.exists():
                settings.update(read_json_utf8(camera_settings_path))
            else:
                self.error_msg = "Camera settings file not found"
                return None

            if model_settings_path.exists():
                settings.update(read_json_utf8(model_settings_path))
            else:
                self.error_msg = "Model settings file not found"
                return None

            try:
                settings["fps"] = int(settings.get("fps"))
                settings["nms_thresh"] = 0.3
                settings["score_thresh"] = float(settings.get("threshold"))

                save_folder = settings.get("save_folder", "detections")
                if isinstance(save_folder, str):
                    try:
                        settings["save_folder"] = save_folder.encode('utf-8').decode('utf-8')
                    except UnicodeError:
                        try:
                            settings["save_folder"] = save_folder.encode('latin1').decode('utf-8')
                        except:
                            settings["save_folder"] = "detections"
                else:
                    settings["save_folder"] = "detections"

                settings["detections_per_image"] = int(settings.get("object_count"))
            except (TypeError, ValueError):
                self.error_msg = "Failed to load data from settings"
                return None

            return settings

        except Exception as e:
            self.error_msg = f"Settings loading error: {str(e)}"
            return None

    def check_settings_hash(self):
        """
        Returns the hash of the current settings.

        Returns:
            str: Settings hash.
        """
        tmp_settings = self._get_settings()
        return self._get_settings_hash(tmp_settings)

    def write_to_db(self, db_manager):
        """
        Processes the current frame and writes detection results to the database.

        Args:
            db_manager: The database manager instance.
        """
        #logging.info("Attempting to process new incoming image")

        if self._current_runner is None:
            logging.debug("Current runner is None")
            if not self.error_msg:
                self.error_msg = "Failed to connect to the video stream"
            return

        result = self._current_runner.predict_boxes()

        if self._current_runner.error_msg == "Failed to read frame":
            logging.debug("Setting reconnect to True")
            self.reconnect = True

        if self._current_runner.error_msg is not None:
            self.error_msg = f"Video stream processing error: {self._current_runner.error_msg}"
            return

        if result is None:
            self.error_msg = "Failed to process frame from camera"
            return

        img, boxes, labels = result

        if boxes is None or labels is None:
            self.error_msg = "No objects detected in the frame"
            return

        self.image1, self.image2 = self._current_runner.show_boxes(img, boxes, labels)
        if self.image1 is None or self.image2 is None:
            self.error_msg = "Error while drawing bounding boxes"
        else:
            self.error_msg = None

        if boxes is not None and labels is not None:
            logging.debug("Boxes and labels found, proceeding to save")
            settings = self._get_settings()
            base_save_folder = Path(settings.get("save_folder", "detections"))
            for box, label in zip(boxes, labels):
                try:
                    label_folder = base_save_folder / label.strip()
                    label_folder.mkdir(parents=True, exist_ok=True)
                    logging.debug(f"Creating folder {label_folder}")

                    photo_path = label_folder / "latest.jpg"

                    if self.image1:
                        self.image1.save(str(photo_path))
                        logging.debug(f"Saving image to {photo_path}")

                    object_item = ObjectItem(
                        ObjrecID=0,
                        Name=label,
                        Time=str(datetime.now()),
                        PositionCoord=f"{box[0]},{box[1]},{box[2]},{box[3]}",
                        PhotoPath=str(photo_path),
                        ContID=1
                    )

                    db_manager.push_objects(object_item)
                    logging.info("Pushed objects to db manager")

                except Exception as e:
                    print(f"Error while saving {label}: {e}")
                    continue

    def get_error(self) -> str:
        """Returns the current error message."""
        return self.error_msg

    def get_images(self) -> tuple[QImage, QImage]:
        """Returns the current pair of images (original and processed)."""
        return self.image1, self.image2

    def __del__(self):
        if self._current_runner is not None:
            self._current_runner.release()
