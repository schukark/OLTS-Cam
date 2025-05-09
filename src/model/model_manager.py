# model_manager.py
import hashlib
import json
import logging
import threading
from pathlib import Path

from PySide6.QtGui import QImage

from model.model_runner import ModelRunner
from datetime import datetime
from database.tables.ObjectItem import ObjectItem

from utils.logger import setup_logger
setup_logger(__name__)


class ModelManager:
    REQUIRED_SETTINGS = [
        "rtsp_url",
        "fps",
        "nms_thresh",
        "score_thresh",
        "detections_per_image",
        "save_folder"
    ]

    def __init__(self):
        self._current_runner = None
        self.error_msg = None
        self.image1 = None
        self.image2 = None
        self._current_settings_hash = None
        self.reconnect = False
        self._lock = threading.Lock()
        self.update_settings()

    def _get_settings_hash(self, settings):
        """Создает хеш текущих настроек для сравнения"""
        settings_str = json.dumps(settings, sort_keys=True)
        return hashlib.md5(settings_str.encode()).hexdigest()

    def _check_settings_changed(self):
        """Проверяет, изменились ли настройки"""
        new_settings = self._get_settings()
        if new_settings is None:  # Если настройки невалидны
            return False, None, None
        new_hash = self._get_settings_hash(new_settings)
        return new_hash != self._current_settings_hash, new_settings, new_hash

    def _validate_settings(self, settings):
        """Проверяет наличие всех необходимых настроек"""
        if not settings:
            self.error_msg = "Настройки не найдены"
            return False

        missing = [key for key in self.REQUIRED_SETTINGS if key not in settings]
        if missing:
            self.error_msg = f"Отсутствуют обязательные настройки: {', '.join(missing)}"
            return False

        return True

    def _create_runner_with_timeout(self, settings):
        """Создает ModelRunner с таймаутом 5 секунд"""
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
                error = f"Ошибка инициализации модели: {str(e)}"

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=5)

        if thread.is_alive():
            self.reconnect = True
            error = "Превышено время ожидания подключения к камере (5 секунд)"
            if runner is not None:
                runner.release()
            return None, error

        if runner is None and error is None:
            self.reconnect = True
            error = "Не удалось подключиться к видеопотоку"

        return runner, error

    def update_settings(self):
        """Обновляет настройки и пересоздает ModelRunner при необходимости"""
        logging.info("Update settings called")
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

            self._current_runner, error = self._create_runner_with_timeout(
                new_settings)

            if self._current_runner is None:
                rtsp_url = new_settings.get("rtsp_url", "неизвестный URL")
                self.error_msg = (f"Не удалось подключиться к камере по адресу: {rtsp_url}\n"
                                  f"Причина: {error}")
                self.reconnect = True
                return

            logging.debug("Runner created successfully")

            self.error_msg = None

    def _get_settings(self):
        try:
            settings_dir = Path(__file__).parent.parent.parent / "settings"
            camera_settings_path = settings_dir / "camera_settings.json"
            model_settings_path = settings_dir / "model_settings.json"

            if not settings_dir.exists():
                self.error_msg = "Директория с настройками не найдена"
                return None

            settings = {}

            # Функция для безопасного чтения JSON с UTF-8
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
                self.error_msg = "Файл настроек камеры не найден"
                return None

            if model_settings_path.exists():
                settings.update(read_json_utf8(model_settings_path))
            else:
                self.error_msg = "Файл настроек модели не найден"
                return None

            try:
                settings["fps"] = int(settings.get("fps"))
                settings["nms_thresh"] = 0.3
                settings["score_thresh"] = float(settings.get("threshold"))

                # Гарантируем UTF-8 для save_folder
                save_folder = settings.get("save_folder", "detections")
                if isinstance(save_folder, str):
                    try:
                        settings["save_folder"] = save_folder.encode(
                            'utf-8').decode('utf-8')
                    except UnicodeError:
                        # Если не получается декодировать как UTF-8, пробуем другие кодировки
                        try:
                            settings["save_folder"] = save_folder.encode(
                                'latin1').decode('utf-8')
                        except:
                            settings["save_folder"] = "detections"
                else:
                    settings["save_folder"] = "detections"

                settings["detections_per_image"] = int(
                    settings.get("object_count"))
            except (TypeError, ValueError):
                self.error_msg = "Данные из настроек не были загружены"
                return None

            return settings

        except Exception as e:
            self.error_msg = f"Ошибка загрузки настроек: {str(e)}"
            return None

    def check_settings_hash(self):
        tmp_settings = self._get_settings()
        return self._get_settings_hash(tmp_settings)

    def write_to_db(self, db_manager):
        logging.info("Initiating write to db and screen")

        if self._current_runner is None:
            logging.debug("Current runner is None")

            if not self.error_msg:
                self.error_msg = "Не удалось подключиться к видеопотоку"
            return

        result = self._current_runner.predict_boxes()

        if self._current_runner.error_msg == "Failed to read frame":
            logging.debug("Setting reconnect to True")
            self.reconnect = True

        if self._current_runner.error_msg is not None:
            self.error_msg = f"Ошибка обработки видеопотока: {self._current_runner.error_msg}"
            return

        if result is None:
            self.error_msg = "Не удалось обработать кадр с камеры"
            return

        img, boxes, labels = result

        if boxes is None or labels is None:
            self.error_msg = "На кадре не обнаружено объектов"
            return

        self.image1, self.image2 = self._current_runner.show_boxes(
            img, boxes, labels)
        if self.image1 is None or self.image2 is None:
            self.error_msg = "Ошибка при отрисовке bounding boxes"
        else:
            self.error_msg = None

        if boxes is not None and labels is not None:
            logging.debug("Boxes and labels are not None, continuing")
            settings = self._get_settings()
            base_save_folder = Path(settings.get("save_folder", "detections"))
            for box, label in zip(boxes, labels):
                try:
                    # Создаем подпапку с именем метки
                    label_folder = base_save_folder / label.strip()
                    label_folder.mkdir(parents=True, exist_ok=True)
                    logging.debug("Creating folder {label_folder}")

                    # Путь к файлу
                    photo_path = label_folder / "latest.jpg"

                    # Сохраняем изображение
                    if self.image1:
                        self.image1.save(str(photo_path))
                        logging.debug("Saving image to {photo_path}")

                    # Создаем объект для базы данных
                    object_item = ObjectItem(
                        ObjrecID=0,
                        Name=label,
                        Time=str(datetime.now()),
                        PositionCoord=f"{box[0]},{box[1]},{box[2]},{box[3]}",
                        PhotoPath=str(photo_path),
                        ContID=1
                    )

                    db_manager.push_objects(object_item)
                    logging.info("Pushed pbjects to db manager")

                except Exception as e:
                    print(f"Ошибка при сохранении {label}: {e}")
                    continue

    def get_error(self) -> str:
        return self.error_msg

    def get_images(self) -> tuple[QImage, QImage]:
        return self.image1, self.image2

    def __del__(self):
        if self._current_runner is not None:
            self._current_runner.release()
