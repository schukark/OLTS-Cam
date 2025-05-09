import sys
from time import sleep, time
from threading import Thread

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal

from desktop.core.app import ApplicationWindow
from model.model_manager import ModelManager


class ModelThreadController(QObject):
    update_signal = Signal(object, object, object)
    finished = Signal()

    def __init__(self, app, window):
        super().__init__()
        self.app = app
        self.window = window
        self.model_manager = ModelManager()
        self._running = True

    def run(self):
        target_fps = 30
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
                self.model_manager.write_to_db()
                frame, boxes = self.model_manager.get_images()
                error_message = self.model_manager.get_error()
                
                # Отправка сигнала в главный поток
                self.update_signal.emit(frame, boxes, error_message)

                # Контроль FPS
                processing_time = time() - start_time
                remaining_time = (1.0 / target_fps) - processing_time
                if remaining_time > 0:
                    sleep(remaining_time)

        finally:
            self.model_manager.__del__()
            self.finished.emit()

    def stop(self):
        self._running = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()

    controller = ModelThreadController(app, window)
    controller.update_signal.connect(window.update_frame)

    model_thread = Thread(target=controller.run)
    model_thread.daemon = True
    model_thread.start()

    ret = app.exec()
    
    controller.stop()
    model_thread.join(1.0)
    
    sys.exit(ret)