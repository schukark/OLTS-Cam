from PySide6.QtWidgets import QMainWindow
from ui.ui_main import Ui_MainWindow
from .home_screen import HomeScreen
from .camera_screen import CameraScreen
from .model_screen import ModelScreen
from .video_screen import VideoScreen

class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Инициализация экранов
        self.screens = {
            'home': HomeScreen(self.ui.homePage),
            'camera': CameraScreen(self.ui.cameraSettingsPage),
            'model': ModelScreen(self.ui.modelSettingsPage),
            'video': VideoScreen(self.ui.videoPlaybackPage)
        }
        
        # Подключение кнопок навигации
        self.ui.homeButton.clicked.connect(lambda: self.show_screen('home'))
        self.ui.cameraSettingsButton_2.clicked.connect(lambda: self.show_screen('camera'))
        self.ui.modelSettingsButton_2.clicked.connect(lambda: self.show_screen('model'))
        self.ui.videoPlaybackButton_2.clicked.connect(lambda: self.show_screen('video'))
        
        # Показываем главный экран по умолчанию
        self.show_screen('home')

    def show_screen(self, screen_name):
        """Переключает на указанный экран"""
        screen_map = {
            'home': self.ui.homePage,
            'camera': self.ui.cameraSettingsPage,
            'model': self.ui.modelSettingsPage,
            'video': self.ui.videoPlaybackPage
        }
        self.ui.stackedWidget.setCurrentWidget(screen_map[screen_name])