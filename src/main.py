import logging
import sys
from time import sleep, time
from threading import Thread

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QTimer

from desktop.core.app import ApplicationWindow
from model.model_manager import ModelManager

from database.DatabaseManager import DatabaseManager
from server.server import run_server

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
root_logger.addHandler(console_handler)


class ModelThreadController(QObject):
    update_signal = Signal(object, object, object)
    finished = Signal()

    def __init__(self, app, window, db_manager):
        super().__init__()
        self.app = app
        self.window = window
        self.db_manager = db_manager
        self.model_manager = ModelManager()
        self._running = True

        # Таймер для периодического вызова connect_and_push
        self.push_timer = QTimer()
        self.push_timer.timeout.connect(self.push_to_db)
        self.push_timer.start(5000)  # 5000 мс = 5 секунд

    def push_to_db(self):
        """Метод для вызова connect_and_push"""
        if hasattr(self.db_manager, 'connect_and_push'):
            self.db_manager.connect_and_push()

    def run(self):
        st = self.model_manager._get_settings()
        target_fps = 20
        if (st and st["fps"]):
            target_fps = st["fps"]
        print(target_fps)

        last_settings_check = time()
        settings_check_interval = 1.0

        try:
            while self._running and self.app.instance() is not None:
                start_time = time()

                # Проверка настроек
                current_time = time()
                if current_time - last_settings_check >= settings_check_interval:
                    current_settings_hash = self.model_manager.check_settings_hash()
                    if (current_settings_hash != self.model_manager._current_settings_hash or
                            self.model_manager.reconnect):
                        self.model_manager.update_settings()
                        if self.model_manager._current_runner:
                            target_fps = self.model_manager._current_runner.settings["fps"]
                    last_settings_check = current_time

                # Обработка кадра
                self.model_manager.write_to_db(self.db_manager)
                frame, boxes = self.model_manager.get_images()
                error_message = self.model_manager.get_error()

                # Отправка сигнала в главный поток
                self.update_signal.emit(frame, boxes, error_message)

                # Контроль FPS
                processing_time = time() - start_time
                remaining_time = (1.0 / target_fps) - processing_time
                # print(remaining_time)
                if remaining_time > 0:
                    sleep(remaining_time)

        finally:
            self.push_timer.stop()  # Останавливаем таймер при завершении
            self.model_manager.__del__()
            self.finished.emit()

    def stop(self):
        self._running = False
        self.push_timer.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    db_manager = DatabaseManager()
    controller = ModelThreadController(app, window, db_manager)
    controller.update_signal.connect(window.update_frame)
    window.show()

    root_logger.info("Application started")

    model_thread = Thread(target=controller.run)
    model_thread.daemon = True
    model_thread.start()

    server_thread = Thread(target=run_server, args=["data_db/database.db"])
    server_thread.daemon = True
    server_thread.start()

    ret = app.exec()

    controller.stop()
    model_thread.join(1.0)
    server_thread.join(1.0)

    root_logger.info("Application exited")

    sys.exit(ret)
