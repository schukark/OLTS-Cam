import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ..ui.ui_main import Ui_MainWindow


class Application(QMainWindow):
    def __init__(self):
        super(Application, self).__init__()

        # Инициализация интерфейса
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Подключение кнопок к методам переключения страниц
        self.ui.homeButton.clicked.connect(self.show_home_page)
        self.ui.cameraSettingsButton_2.clicked.connect(self.show_camera_settings_page)
        self.ui.modelSettingsButton_2.clicked.connect(self.show_model_settings_page)
        self.ui.videoPlaybackButton_2.clicked.connect(self.show_video_playback_page)

    def show_home_page(self):
        """Переключение на главную страницу."""
        self.ui.stackedWidget.setCurrentWidget(self.ui.homePage)

    def show_camera_settings_page(self):
        """Переключение на страницу настроек камеры."""
        self.ui.stackedWidget.setCurrentWidget(self.ui.cameraSettingsPage)

    def show_model_settings_page(self):
        """Переключение на страницу настроек модели."""
        self.ui.stackedWidget.setCurrentWidget(self.ui.modelSettingsPage)

    def show_video_playback_page(self):
        """Переключение на страницу воспроизведения видео."""
        self.ui.stackedWidget.setCurrentWidget(self.ui.videoPlaybackPage)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec())