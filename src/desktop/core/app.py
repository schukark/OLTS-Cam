from PySide6.QtWidgets import QMainWindow
from ..ui.ui_main import Ui_MainWindow
from .home_screen import HomeScreen
from .camera_screen import CameraScreen
from .model_screen import ModelScreen
from .video_screen import VideoScreen

import logging
from utils.logger import setup_logger

setup_logger(__name__)


class ApplicationWindow(QMainWindow):
    """
    The main application window that handles screen navigation and video updates.

    Attributes:
        ui (Ui_MainWindow): The UI object for the main window.
        cur_screen (str): The current active screen name.
        runner_status (int): A status flag for the runner (default: 0).
        screens (dict): A dictionary of all initialized screen objects.
    """
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.cur_screen = 'home'
        self.runner_status = 0

        # Initialize all screens
        self.screens = {
            'home': HomeScreen(self.ui.homePage),
            'camera': CameraScreen(self.ui, self),
            'model': ModelScreen(self.ui, self),
            'video': VideoScreen(self.ui)
        }

        # Connect navigation buttons to corresponding screens
        self.ui.homeButton.clicked.connect(lambda: self.show_screen('home'))
        self.ui.cameraSettingsButton_2.clicked.connect(
            lambda: self.show_screen('camera'))
        self.ui.modelSettingsButton_2.clicked.connect(
            lambda: self.show_screen('model'))
        self.ui.videoPlaybackButton_2.clicked.connect(
            lambda: self.show_screen('video'))

        # Show the home screen by default
        self.show_screen('home')

    def show_screen(self, screen_name):
        """
        Switches the view to the specified screen.

        Args:
            screen_name (str): The name of the screen to display.
        """
        screen_map = {
            'home': self.ui.homePage,
            'camera': self.ui.cameraSettingsPage,
            'model': self.ui.modelSettingsPage,
            'video': self.ui.videoPlaybackPage
        }

        self.screens["model"].folder_update = False
        if self.cur_screen == "camera":
            self.screens['camera'].load_settings()
            self.screens['camera'].clear_highlight()

        logging.debug(f"Switched to screen: {screen_name}")
        self.ui.stackedWidget.setCurrentWidget(screen_map[screen_name])
        self.cur_screen = screen_name

    def update_frame(self, image1, image2, error_msg=None):
        """
        Updates the video frame on the video screen.

        Args:
            image1 (QImage): The primary video frame or None.
            image2 (QImage): The processed/model video frame or None.
            error_msg (str, optional): An error message to display instead of frames.
        """
        self.screens['video'].update_frame(image1, image2, error_msg)

    def set_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            QStackedWidget, QWidget {
                background-color: #f8f9fa;
                color: #212529;
            }
            
            QLabel {
                color: #343a40;
                font-size: 14px;
            }
            
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                color: #495057;
            }
            
            QLineEdit:focus {
                border: 1px solid #adb5bd;
                background-color: #f1f3f5;
            }
            
            QPushButton {
                background-color: #6c757d;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #5a6268;
            }
            
            QPushButton:pressed {
                background-color: #495056;
            }
            
            QPushButton:flat {
                background-color: transparent;
                border: 1px solid #ced4da;
                color: #495057;
            }
            
            QSlider::groove:horizontal {
                height: 6px;
                background: #e9ecef;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                background: #6c757d;
                border-radius: 7px;
                margin: -4px 0;
            }
            
            QCheckBox {
                spacing: 8px;
                color: #495057;
                font-size: 14px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #adb5bd;
                border-radius: 3px;
                background: #ffffff;
            }
            
            QCheckBox::indicator:checked {
                background-color: #6c757d;
                border: 1px solid #6c757d;
            }
            
            QTextEdit, QPlainTextEdit {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                color: #495057;
            }
        """)