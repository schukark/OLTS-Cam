from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QWidget, QSpacerItem)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSizePolicy
import os
from core.dialogs.license_dialog import LicenseDialog

class HomeScreen:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        # Очищаем существующий layout
        if self.parent.layout():
            while self.parent.layout().count():
                self.parent.layout().takeAt(0)
        
        # Основной контейнер
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Добавляем растяжку сверху
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Горизонтальный layout для логотипа и правой части
        content_layout = QHBoxLayout()
        
        # Левая часть - логотип
        logo_label = QLabel()
        logo_path = os.path.join(
            "resources", 
            "logo.jpg"
        )
        
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_pixmap = logo_pixmap.scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("Логотип не найден")
            logo_label.setAlignment(Qt.AlignCenter)
        
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Правая часть - текст и кнопка
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignCenter)
        
        welcome_label = QLabel("Добро пожаловать в приложение!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.license_button = QPushButton("Показать лицензию")
        self.license_button.setFixedWidth(300)
        self.license_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.license_button.clicked.connect(self.show_license_dialog)
        
        right_layout.addWidget(welcome_label, alignment=Qt.AlignCenter)
        right_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        right_layout.addWidget(self.license_button, alignment=Qt.AlignCenter)
        right_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Добавляем части в горизонтальный layout
        content_layout.addWidget(logo_label)
        content_layout.addWidget(right_widget)
        
        # Добавляем горизонтальный layout в основной
        main_layout.addLayout(content_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Устанавливаем layout на родительский виджет
        self.parent.layout().addWidget(container)
    
    def show_license_dialog(self):
        """Показывает диалоговое окно с лицензией"""
        dialog = LicenseDialog(self.parent)
        dialog.exec()