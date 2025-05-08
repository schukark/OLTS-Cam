from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import QMessageBox
from pathlib import Path


class VideoSignals(QObject):
    error_occurred = Signal(str)
    frame_ready = Signal(QImage, QImage)


class VideoScreen:
    SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / \
        "settings" / "camera_settings.json"

    def __init__(self, ui):
        self.ui = ui
        self.signals = VideoSignals()
        self.cap = None
        self.is_running = False
        self.current_image1 = None
        self.current_image2 = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Инициализация интерфейса"""
        self.ui.video_label.resizeEvent = self.on_label_resize
        # Настраиваем стиль для отображения текста ошибки
        self.ui.video_label.setStyleSheet("""
            QLabel {
                color: White;
                font-size: 20px;
                background-color: black;
                qproperty-alignment: AlignCenter;
            }
        """)

    def setup_connections(self):
        """Подключение сигналов к слотам"""
        self.signals.frame_ready.connect(self.update_frame)
        self.signals.error_occurred.connect(self.show_error)
        self.ui.CheckBoxModel.stateChanged.connect(
            self._update_displayed_image)

    def show_error(self, message):
        """Отображение ошибки"""
        QMessageBox.critical(self.ui.video_label, "Ошибка", message)

    def on_label_resize(self, event):
        """Обработчик изменения размера QLabel"""
        if hasattr(self, 'current_pixmap') and self.current_pixmap:
            scaled_pixmap = self.current_pixmap.scaled(
                self.ui.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.ui.video_label.setPixmap(scaled_pixmap)
        event.accept()

    def update_frame(self, image1, image2, error_msg=None):
        """
        Обновление изображений или отображение ошибки
        :param image1: Первое изображение (QImage) или None
        :param image2: Второе изображение (QImage) или None
        :param error_msg: Сообщение об ошибке (str) или None
        """
        if error_msg:
            self._show_error_message(error_msg)
            return

        self.current_image1 = image1
        self.current_image2 = image2
        self._update_displayed_image()

    def _show_error_message(self, message):
        """Отображает сообщение об ошибке в video_label"""
        # Создаем пустое черное изображение
        pixmap = QPixmap(self.ui.video_label.size())
        pixmap.fill(Qt.black)
        
        # Рисуем текст ошибки
        painter = QPainter(pixmap)
        painter.setPen(QColor(Qt.red))
        painter.setFont(QFont("Arial", 16))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, message)
        painter.end()
        
        self.ui.video_label.setPixmap(pixmap)

    def _update_displayed_image(self):
        """Внутренний метод для обновления отображаемого изображения"""
        if not (self.current_image1 and self.current_image2):
            return

        # Выбираем изображение в зависимости от состояния CheckBoxModel
        use_model_view = self.ui.CheckBoxModel.isChecked()
        image_to_show = self.current_image2 if use_model_view \
            else self.current_image1

        self.current_pixmap = QPixmap.fromImage(image_to_show)
        scaled_pixmap = self.current_pixmap.scaled(
            self.ui.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.ui.video_label.setPixmap(scaled_pixmap)