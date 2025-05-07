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
        self.cur_screen = 'home'
        
        # Инициализация экранов
        self.screens = {
            'home': HomeScreen(self.ui.homePage),
            'camera': CameraScreen(self.ui, self),
            'model': ModelScreen(self.ui, self),
            'video': VideoScreen(self.ui)
        }
        
        # Подключение кнопок навигации
        self.ui.homeButton.clicked.connect(lambda: self.show_screen('home'))
        self.ui.cameraSettingsButton_2.clicked.connect(lambda: self.show_screen('camera'))
        self.ui.modelSettingsButton_2.clicked.connect(lambda: self.show_screen('model'))
        self.ui.videoPlaybackButton_2.clicked.connect(lambda: self.show_screen('video'))
        
        # Показываем главный экран по умолчанию
        self.show_screen('home')

    def stop_video(self):
        self.screens['video'].stop_capture()

    def show_screen(self, screen_name):
        """Переключает на указанный экран"""
        screen_map = {
            'home': self.ui.homePage,
            'camera': self.ui.cameraSettingsPage,
            'model': self.ui.modelSettingsPage,
            'video': self.ui.videoPlaybackPage
        }
        
        
        if (self.cur_screen == "camera"):
            self.screens['camera'].load_settings()
            self.screens['camera'].clear_highlight()
            
        if screen_name == "video":
            self.screens['video'].start_capture()
        
        self.ui.stackedWidget.setCurrentWidget(screen_map[screen_name])
        self.cur_screen = screen_name
        