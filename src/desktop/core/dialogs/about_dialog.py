"""About Dialog Module

Provides a Qt-based dialog window to display about information and license agreement text from a file.

Classes:
    AboutDialog -- A dialog window displaying about information and license text.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit,
                               QPushButton)
from PySide6.QtCore import Qt
import os


class AboutDialog(QDialog):
    """A dialog window displaying about information and license text.

    This dialog displays the contents of a license file (e.g., 'license.txt') in a read-only text field
    along with an option to close the dialog. The window has a fixed size of 600x400 pixels.

    Methods:
        __init__ -- Initializes the AboutDialog, including setting up UI components.
        load_license -- Loads the license text from a file, typically 'license.txt'.
    """
    
    def __init__(self, parent=None, about_path=None):
        """Initializes the AboutDialog window.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            about_path (str, optional): Path to the license text file. Defaults to None.
        """
        super().__init__(parent)
        self.about_path = about_path
        self.setWindowTitle("About")
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

        This function attempts to read the contents of a license text file from the path specified in `self.about_path`.

        Returns:
            str: The contents of the license file.

        Raises:
            FileNotFoundError: If the license file is not found at the specified path.
            IOError: If there are issues reading the file.
        """

        if not os.path.exists(self.about_path):
            raise FileNotFoundError(f"License file not found: {self.about_path}")

        try:
            with open(self.about_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            raise IOError(f"Error reading the license file: {e}")
