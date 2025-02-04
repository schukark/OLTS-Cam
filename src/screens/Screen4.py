from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QStackedWidget, QHBoxLayout, QSizePolicy
import sys
from PySide6.QtCore import Qt

from ScreenBase import ScreenBase

class Screen4(ScreenBase):
    def __init__(self, stacked_widget: QStackedWidget) -> None:
        super().__init__('Screen 4', stacked_widget)