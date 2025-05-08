import sys
from time import sleep

from PySide6.QtWidgets import QApplication

from desktop.core.app import ApplicationWindow
from model.model import ModelRunner


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()

    model_runner = ModelRunner()

    while app.instance() is not None:
        boxes, frame = model_runner.show_boxes()
        window.update_frame(boxes, frame)
        sleep(10)

    sys.exit(app.exec())
