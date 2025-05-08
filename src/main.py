import sys
from time import sleep
from threading import Thread

from PySide6.QtWidgets import QApplication

from desktop.core.app import ApplicationWindow
from model.model_runner import ModelRunner


def run_model(app, window, model_runner):
    while app.instance() is not None:
        boxes, frame = model_runner.show_boxes()
        window.update_frame(boxes, frame)
        sleep(10)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()

    model_runner = ModelRunner()

    Thread(target=run_model(app, window, model_runner))

    sys.exit(app.exec())
