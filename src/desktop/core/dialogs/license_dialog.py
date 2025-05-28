"""License Dialog Module

Provides a Qt-based dialog window to display license agreement text from files.

Classes:
    LicenseDialog -- A dialog window displaying license text loaded from LICENSE and LICENSE.PySide6 files.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit,
                               QPushButton, QMessageBox)
from PySide6.QtCore import Qt
import os


class LicenseDialog(QDialog):
    """A dialog window displaying license agreement texts.

    This dialog displays the combined contents of 'LICENSE' and 'LICENSE.PySide6' files
    in a read-only text field, with several newlines between them, along with a close button.
    The window has a fixed size of 600x400 pixels.

    Methods:
        __init__ -- Initializes the LicenseDialog window, setting up the UI components.
        load_license -- Loads and combines license texts from both files.
    """
    
    def __init__(self, parent=None):
        """Initializes the LicenseDialog window.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("License Agreement")
        self.setFixedSize(550, 800)

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
        """Load and combine license texts from both files.

        This function attempts to read the contents of both 'LICENSE' and 'LICENSE.PySide6' files
        from the current working directory and combines them with several newlines in between.

        Returns:
            str: The combined contents of both license files separated by newlines.

        Raises:
            FileNotFoundError: If either license file is not found.
            IOError: If there are issues reading the files.
        """
        license_path = os.path.join(os.getcwd(), "LICENSE")
        pyside_license_path = os.path.join(os.getcwd(), "LICENSE.PySide6")

        # Check if both files exist
        if not os.path.exists(license_path):
            raise FileNotFoundError(f"Main license file not found: {license_path}")
        if not os.path.exists(pyside_license_path):
            raise FileNotFoundError(f"PySide6 license file not found: {pyside_license_path}")

        try:
            with open(license_path, 'r', encoding='utf-8') as f:
                main_license = f.read()
            with open(pyside_license_path, 'r', encoding='utf-8') as f:
                pyside_license = f.read()
            
            # Combine licenses with 5 newlines in between
            return f"{main_license}\n\n\n\n\n{pyside_license}"
        except IOError as e:
            raise IOError(f"Error reading license files: {e}")