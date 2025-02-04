from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QStackedWidget, QHBoxLayout, QSizePolicy
import sys
from PySide6.QtCore import Qt

class ScreenBase(QWidget):
    stacked_widget: QStackedWidget
    label: QLabel

    def __init__(self, name: str, stacked_widget: QStackedWidget) -> None:
        super().__init__()
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()
        
        self.label = QLabel(name, self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def switch_screen(self, index: int) -> None:
        self.stacked_widget.setCurrentIndex(index)