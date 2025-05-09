# model_manager.py
import hashlib
import json
import threading
from pathlib import Path

from PySide6.QtGui import QImage

from model.model_runner import ModelRunner
from datetime import datetime
from database.tables.ObjectItem import ObjectItem


class ModelManager:
    REQUIRED_SETTINGS = [
        "rtsp_url",
        "fps",
        "nms_thresh",
        "score_thresh",
        "detections_per_image"
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
        with self._lock:
            settings_changed, new_settings, new_hash = self._check_settings_changed()

            if not settings_changed and not self.reconnect and self._current_runner is not None:
                return

            if self._current_runner is not None:
                self._current_runner.release()
                self._current_runner = None

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

            if camera_settings_path.exists():
                with open(camera_settings_path, "r") as f:
                    camera_settings = json.load(f)
                    settings.update(camera_settings)
            else:
                self.error_msg = "Файл настроек камеры не найден"
                return None

            if model_settings_path.exists():
                with open(model_settings_path, "r") as f:
                    model_settings = json.load(f)
                    settings.update(model_settings)
            else:
                self.error_msg = "Файл настроек модели не найден"
                return None

            try:
                settings["fps"] = int(settings.get("fps"))
                settings["nms_thresh"] = float(settings.get("threshold"))
                settings["score_thresh"] = float(settings.get("threshold"))
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
        if self._current_runner is None:
            if not self.error_msg:
                self.error_msg = "Не удалось подключиться к видеопотоку"
            return

        result = self._current_runner.predict_boxes()

        if self._current_runner.error_msg is not None:
            self.error_msg = f"Ошибка обработки видеопотока:\
                {self._current_runner.error_msg}"
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

        # Отправка данных обнаруженных объектов в базу данных
        print("write: \n")
        if boxes is not None and labels is not None:
            for box, label in zip(boxes, labels):
                print(label +"\n")
                # Создаем объект ObjectItem с данными обнаруженного объекта
                object_item = ObjectItem(
                    Name=label,  # Название объекта
                    Time=str(datetime.now()),  # Время обнаружения
                    PositionCoord=f"{box[0]},{box[1]},{box[2]},{box[3]}",  # Координаты bounding box
                    PhotoPath="path/to/saved/image.jpg",  # Путь к сохраненному изображению
                    ContID=1  # ID контейнера (можно получить из настроек или другим способом)
                )
                
                # Отправляем объект в базу данных через db_manager
                db_manager.push_objects(object_item)

    def get_error(self) -> str:
        return self.error_msg

    def get_images(self) -> tuple[QImage, QImage]:
        return self.image1, self.image2

    def __del__(self):
        if self._current_runner is not None:
            self._current_runner.release()
