import sys
from time import sleep, time
from threading import Thread

from PySide6.QtWidgets import QApplication

from desktop.core.app import ApplicationWindow
from model.model_manager import ModelManager

def run_model(app, window):
    model_manager = ModelManager()
    
    # Инициализация переменных для управления FPS и проверки настроек
    target_fps = model_manager._current_runner.settings["fps"] if model_manager._current_runner else 5
    frame_delay = 1.0 / target_fps
    last_settings_check = time()
    settings_check_interval = 1.0  # Проверка настроек каждую секунду
    last_settings_hash = model_manager._current_settings_hash

    while app.instance() is not None:
        #if (window.runner_status == 1):
        #    model_manager.reconnect = True
        #    model_manager.__del__()
        
        #while (window.runner_status == 1):
        #    window.runner_status = 0
            
        print(frame_delay)
        start_time = time()
        # Проверка настроек каждую секунду
        current_time = time()

        if current_time - last_settings_check >= settings_check_interval:
            current_settings_hash = model_manager.check_settings_hash()
            
            # Если настройки изменились
            if current_settings_hash != last_settings_hash or model_manager.reconnect:
                model_manager.reconnect = False
                print("update")
                if (model_manager.error_msg is not None and model_manager.error_msg == "Данные из настроек не были загружены"):
                    window.update_frame(None, None, "Загрузка видео")
                model_manager.update_settings()
                print(model_manager.error_msg)
                last_settings_hash = current_settings_hash
                if model_manager._current_runner:
                    target_fps = model_manager._current_runner.settings["fps"]
                    frame_delay = 1.0 / target_fps
                    print(f"Settings updated. New FPS: {target_fps}")
            
            last_settings_check = current_time
        
        #if (window.runner_status == 1):
        #    model_manager.reconnect = True
        #    model_manager.__del__()
        
        #while (window.runner_status == 1):
        #    window.runner_status = 0
            
        # Основная работа с моделью
        model_manager.write_to_db()
        frame, boxes = model_manager.get_images()
        error_message = model_manager.get_error()
        window.update_frame(frame, boxes, error_message)
        
        # Управление FPS
        processing_time = time() - start_time
        remaining_time = frame_delay - processing_time
        print(remaining_time)
        if remaining_time > 0:
            sleep(remaining_time)
    
    model_manager.__del__()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()

    
    model_thread = Thread(target=run_model, args=(app, window), daemon=True)
    model_thread.start()
    
    sys.exit(app.exec())