"""License Dialog Module

Provides a Qt-based dialog window to display license agreement text from a file.

Classes:
    LicenseDialog -- A dialog window displaying license text loaded from a specified file.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit,
                               QPushButton, QMessageBox)
from PySide6.QtCore import Qt
import os


class LicenseDialog(QDialog):
    """A dialog window displaying a license agreement text.

    This dialog displays the contents of a license file (e.g., 'license.txt') in a read-only text field,
    along with a close button. The window has a fixed size of 600x400 pixels.

    Methods:
        __init__ -- Initializes the LicenseDialog window, setting up the UI components.
        load_license -- Loads the license text from the specified file.
    """
    
    def __init__(self, parent=None):
        """Initializes the LicenseDialog window.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("License Agreement")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        try:
            license_text = self.load_license()
            self.text_edit.setText(license_text)
        except Exception as e:
            self.text_edit.setText(f"Error loading license:\n{str(e)}")

        close_button = QPushButton("Close")
        close_button.setFixedWidth(200)
        close_button.clicked.connect(self.close)

        layout.addWidget(self.text_edit)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def load_license(self):
        """Load license text from the specified file.

        This function attempts to read the contents of a license text file (e.g., 'license.txt') from
        the current working directory.

        Returns:
            str: The contents of the license file.

        Raises:
            FileNotFoundError: If the license file does not exist in the specified location.
            IOError: If there are issues reading the file.
        """
        license_path = os.path.join(os.getcwd(), "license.txt")

        if not os.path.exists(license_path):
            raise FileNotFoundError(f"License file not found: {license_path}")

        try:
            with open(license_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            raise IOError(f"Error reading the license file: {e}")
