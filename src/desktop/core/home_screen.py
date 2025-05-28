from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QWidget, QSpacerItem, QTextEdit,
                               QDialog, QVBoxLayout, QDialogButtonBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy
import os
from pathlib import Path
from .dialogs.license_dialog import LicenseDialog
from .dialogs.about_dialog import AboutDialog

class HomeScreen:
    """
    HomeScreen UI Module with muted color scheme
    """

    RESOURCES_PATH = Path(__file__).parent.parent.parent.parent / "resources"
    README_PATH = Path(__file__).parent.parent.parent.parent / "Readme.md"

    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        # Clear existing layout
        if self.parent.layout():
            while self.parent.layout().count():
                self.parent.layout().takeAt(0)

        # Main container with soft background
        container = QWidget()
        container.setStyleSheet("""
            background-color: #f8f9fa;
        """)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Add top spacer
        main_layout.addSpacerItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Content layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)

        # Logo section
        logo_label = QLabel()
        logo_path = os.path.join(self.RESOURCES_PATH, "logo.jpg")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_pixmap = logo_pixmap.scaled(
                500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("Logo not found")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("""
                font-size: 16px;
                color: #495057;
            """)

        logo_label.setAlignment(Qt.AlignCenter)

        # Right side content
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setSpacing(20)

        welcome_label = QLabel("Welcome to the application")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: 500;
            color: #343a40;
            margin-bottom: 30px;
        """)

        # Primary button (subtle blue)
        self.license_button = QPushButton("Show License")
        self.license_button.setFixedWidth(300)
        self.license_button.setFixedHeight(50)
        self.license_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: #ffffff;
                font-size: 15px;
                font-weight: 500;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #495056;
            }
        """)
        self.license_button.clicked.connect(self.show_license_dialog)

        # Secondary button (very subtle)
        self.about_button = QPushButton("About")
        self.about_button.setFixedWidth(300)
        self.about_button.setFixedHeight(50)
        self.about_button.setStyleSheet("""
            QPushButton {
                background-color: #d3d8de; /* Более темный серый цвет */
                color: #343a40; /* Более темный серый текст */
                font-size: 15px;
                font-weight: 500;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #b5bbbf; /* Более темный серый при наведении */
                border-color: #a8b2bf;
            }
            QPushButton:pressed {
                background-color: #9ea8ad; /* Более темный серый при нажатии */
            }
        """)
        self.about_button.clicked.connect(self.show_about_dialog)

        right_layout.addWidget(welcome_label)
        right_layout.addWidget(self.license_button, alignment=Qt.AlignCenter)
        right_layout.addWidget(self.about_button, alignment=Qt.AlignCenter)

        content_layout.addWidget(logo_label)
        content_layout.addWidget(right_widget)

        main_layout.addLayout(content_layout)
        main_layout.addSpacerItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.parent.layout().addWidget(container)

    def show_license_dialog(self):
        dialog = LicenseDialog(self.parent)
        dialog.exec()

    def show_about_dialog(self):
        dialog = AboutDialog(self.parent, self.README_PATH)
        dialog.exec()