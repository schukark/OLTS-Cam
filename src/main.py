import sys
from time import sleep, time
from threading import Thread

from PySide6.QtWidgets import QApplication

from desktop.core.app import ApplicationWindow
from model.model_manager import ModelManager
from pathlib import Path

def run_model(app, window):
    model_manager = ModelManager()
    
    # Получаем FPS из настроек
    try:
        fps = model_manager.model.settings["fps"]
        frame_delay = 1.0 / fps
    except:
        fps = 5  # значение по умолчанию
        frame_delay = 1.0 / fps

    while app.instance() is not None:
        start_time = time()
        
        model_manager.write_to_db()

        frame, boxes = model_manager.get_images()
        error_message = model_manager.get_error()

        window.update_frame(frame, boxes, error_message)
        
        # Рассчитываем время выполнения и компенсируем задержкой
        processing_time = time() - start_time
        if processing_time < frame_delay:
            sleep(frame_delay - processing_time)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()

    model_thread = Thread(target=run_model, args=(app, window), daemon=True)
    model_thread.start()

    sys.exit(app.exec())