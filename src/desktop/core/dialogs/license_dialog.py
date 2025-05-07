from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                             QPushButton, QMessageBox)
from PySide6.QtCore import Qt
import os

class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Лицензионное соглашение")
        self.setFixedSize(600, 400)
        
        layout = QVBoxLayout()
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        
        try:
            license_text = self.load_license()
            self.text_edit.setText(license_text)
        except Exception as e:
            self.text_edit.setText(f"Ошибка загрузки лицензии:\n{str(e)}")
        
        close_button = QPushButton("Закрыть")
        close_button.setFixedWidth(200)
        close_button.clicked.connect(self.close)
        
        layout.addWidget(self.text_edit)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
    
    def load_license(self):
        """Загружает текст лицензии из файла"""
        license_path = os.path.join("license.txt")
        
        if not os.path.exists(license_path):
            raise FileNotFoundError(f"Файл лицензии не найден: {license_path}")
        
        with open(license_path, 'r', encoding='utf-8') as f:
            return f.read()