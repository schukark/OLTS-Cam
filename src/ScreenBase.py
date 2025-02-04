from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QStackedWidget, QHBoxLayout, QSizePolicy
import sys
from PySide6.QtCore import Qt

class ScreenBase(QWidget):
    stacked_widget: QStackedWidget
    label: QLabel
    layout: QVBoxLayout

    def __init__(self, name: str, stacked_widget: QStackedWidget) -> None:
        super().__init__()
        self.stacked_widget = stacked_widget
        self.layout = QVBoxLayout()
        
        self.label = QLabel(name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.layout.addStretch()
        
        self.setLayout(self.layout)
    
    def switch_screen(self, index: int) -> None:
        self.stacked_widget.setCurrentIndex(index)