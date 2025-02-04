from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QStackedWidget, QHBoxLayout, QSizePolicy
import sys
from PySide6.QtCore import Qt

class NavigationBar(QWidget):
    button_layout: QHBoxLayout
    buttons: list[QPushButton]

    def __init__(self, stacked_widget: QStackedWidget) -> None:
        super().__init__()
        self.button_layout = QHBoxLayout()
        self.buttons = []
        
        for i in range(5):
            button = QPushButton(f'Screen {i + 1}')
            button.clicked.connect(lambda _, i=i: stacked_widget.setCurrentIndex(i))
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.button_layout.addWidget(button)
            self.buttons.append(button)
        
        self.setLayout(self.button_layout)