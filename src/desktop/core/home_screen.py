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
    HomeScreen UI Module

    This class sets up the home screen interface, which includes a logo, 
    a welcome message, and buttons to display the license and about dialogs.

    Attributes:
        RESOURCES_PATH (Path): Path to the resources directory containing images and assets.
        parent (QWidget): The parent widget that hosts this screen.
        license_button (QPushButton): Button to trigger the license dialog.
        about_button (QPushButton): Button to trigger the about dialog.
    """

    RESOURCES_PATH = Path(__file__).parent.parent.parent.parent / "resources"
    README_PATH = Path(__file__).parent.parent.parent.parent / "Readme.md"

    def __init__(self, parent):
        """
        Initializes the HomeScreen.

        Args:
            parent (QWidget): The parent widget in which the home screen is displayed.
        """
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the user interface layout.

        This method clears any existing layout from the parent widget and creates
        a new layout that includes:
            - A logo image on the left side.
            - A welcome message and buttons on the right side.
            - Proper spacers to center and balance the layout visually.
        """
        # Clear the existing layout if any
        if self.parent.layout():
            while self.parent.layout().count():
                self.parent.layout().takeAt(0)

        # Main container and layout
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Add top spacer
        main_layout.addSpacerItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Horizontal layout for logo and right-side content
        content_layout = QHBoxLayout()

        # Left side - Logo
        logo_label = QLabel()
        logo_path = os.path.join(
            self.RESOURCES_PATH,
            "logo.jpg"
        )
        print(logo_path)
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_pixmap = logo_pixmap.scaled(
                500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("Logo not found")
            logo_label.setAlignment(Qt.AlignCenter)

        logo_label.setAlignment(Qt.AlignCenter)

        # Right side - Welcome text and buttons
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignCenter)

        welcome_label = QLabel("Welcome to the application!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.license_button = QPushButton("Show License")
        self.license_button.setFixedWidth(300)
        self.license_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.license_button.clicked.connect(self.show_license_dialog)

        self.about_button = QPushButton("About")
        self.about_button.setFixedWidth(300)
        self.about_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.about_button.clicked.connect(self.show_about_dialog)

        right_layout.addWidget(welcome_label, alignment=Qt.AlignCenter)
        right_layout.addSpacerItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        right_layout.addWidget(self.license_button, alignment=Qt.AlignCenter)
        right_layout.addSpacerItem(QSpacerItem(
            20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        right_layout.addWidget(self.about_button, alignment=Qt.AlignCenter)
        right_layout.addSpacerItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add left and right sections to the horizontal layout
        content_layout.addWidget(logo_label)
        content_layout.addWidget(right_widget)

        # Add the horizontal layout to the main layout
        main_layout.addLayout(content_layout)
        main_layout.addSpacerItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Set the layout to the parent widget
        self.parent.layout().addWidget(container)

    def show_license_dialog(self):
        """
        Displays the license dialog window.
        """
        dialog = LicenseDialog(self.parent)
        dialog.exec()

    def show_about_dialog(self):
        """
        Displays the about dialog with contents from Readme.md.
        """
        dialog = AboutDialog(self.parent, self.README_PATH)
        dialog.exec()