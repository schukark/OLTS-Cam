import sys
from time import sleep
from threading import Thread

from PySide6.QtWidgets import QApplication

from desktop.core.app import ApplicationWindow
from model.model_manager import ModelManager


def run_model(app, window, model_manager: ModelManager):
    while app.instance() is not None:
        result = model_manager.write_to_db()

        sleep(10)
        if result is None:
            continue

        boxes, frame = result

        window.update_frame(boxes, frame)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()

    #model_manager = ModelManager()

    #Thread(target=run_model(app, window, model_manager))

    sys.exit(app.exec())
