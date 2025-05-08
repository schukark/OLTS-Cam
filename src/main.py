import sys
from time import sleep
from threading import Thread

from PySide6.QtWidgets import QApplication

from desktop.core.app import ApplicationWindow
from model.model_manager import ModelManager
from pathlib import Path

def run_model(app, window):
    model_manager = ModelManager()

    while app.instance() is not None:
        model_manager.write_to_db()

        #sleep(0.1)
        
        boxes, frame = model_manager.get_images()
        error_message = model_manager.get_error()

        window.update_frame(boxes, frame, error_message)
        
        #SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / "file.txt"
        #with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        #    f.write(error_message + "\n")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()

    model_thread = Thread(target=run_model, args=(app, window), daemon=True)
    model_thread.start()

    sys.exit(app.exec())
