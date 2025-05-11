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

# Setting up the logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
root_logger.addHandler(console_handler)


class ModelThreadController(QObject):
    """Handles the model and database operations in a separate thread."""
    
    update_signal = Signal(object, object, object)
    finished = Signal()

    def __init__(self, app, window, db_manager):
        """Initialize the thread controller with application, window, and database manager."""
        super().__init__()
        self.app = app
        self.window = window
        self.db_manager = db_manager
        self.model_manager = ModelManager()
        self._running = True

        # Timer to periodically call the push_to_db method
        self.push_timer = QTimer()
        self.push_timer.timeout.connect(self.push_to_db)
        self.push_timer.start(5000)  # Trigger every 5 seconds
        
        self.update_settings_timer = QTimer()
        self.update_settings_timer.timeout.connect(self.update_settings)
        self.update_settings_timer.start(5000)
        
    def update_settings(self):
        """Push settings to screen."""
        self.window.screens["camera"].load_settings()
        self.window.screens["model"].load_settings()

    def push_to_db(self):
        """Push data to the database at regular intervals."""
        if hasattr(self.db_manager, 'connect_and_push'):
            try:
                self.db_manager.connect_and_push()
            except Exception as e:
                root_logger.error(f"Error pushing to database: {e}")

    def run(self):
        """Run the model processing loop, handle settings, and communicate with the main thread."""
        st = self.model_manager._get_settings()
        target_fps = 20
        if st and st.get("fps"):
            target_fps = st["fps"]
        print(target_fps)

        last_settings_check = time()
        settings_check_interval = 1.0  # Check settings every 1 second

        try:
            while self._running and self.app.instance() is not None:
                start_time = time()

                # Check for updated settings
                current_time = time()
                if current_time - last_settings_check >= settings_check_interval:
                    current_settings_hash = self.model_manager.check_settings_hash()
                    if (current_settings_hash != self.model_manager._current_settings_hash or
                            self.model_manager.reconnect):
                        self.model_manager.update_settings()
                        if self.model_manager._current_runner:
                            target_fps = self.model_manager._current_runner.settings["fps"]
                    last_settings_check = current_time

                # Process frame and send to database
                self.model_manager.write_to_db(self.db_manager)
                frame, boxes = self.model_manager.get_images()
                error_message = self.model_manager.get_error()

                # Send signal with frame data to main thread
                self.update_signal.emit(frame, boxes, error_message)

                # Control FPS by adjusting the time spent processing each frame
                processing_time = time() - start_time
                remaining_time = (1.0 / target_fps) - processing_time
                if remaining_time > 0:
                    sleep(remaining_time)

        finally:
            self.push_timer.stop()  # Stop the timer when the loop finishes
            self.model_manager.__del__()
            self.finished.emit()

    def stop(self):
        """Stop the thread and any active timers."""
        self._running = False
        self.push_timer.stop()


if __name__ == '__main__':
    # Initialize the application
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    db_manager = DatabaseManager()
    
    # Create the model controller and connect its signals to the window
    controller = ModelThreadController(app, window, db_manager)
    controller.update_signal.connect(window.update_frame)
    
    window.show()

    root_logger.info("Application started")

    # Start the model processing thread
    model_thread = Thread(target=controller.run)
    model_thread.daemon = True
    model_thread.start()

    # Start the server thread
    server_thread = Thread(target=run_server, args=["data_db/database.db"])
    server_thread.daemon = True
    server_thread.start()

    # Run the application event loop
    ret = app.exec()

    # Stop threads gracefully
    controller.stop()
    model_thread.join(1.0)
    server_thread.join(1.0)

    root_logger.info("Application exited")

    # Exit the application
    sys.exit(ret)
