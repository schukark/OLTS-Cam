from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QStackedWidget, QHBoxLayout, QSizePolicy
import sys
from PySide6.QtCore import Qt

from NavigationBar import NavigationBar
from ScreenBase import ScreenBase
from screens import *

class MainApp(QWidget):
    stacked_widget: QStackedWidget
    screens: list[ScreenBase]
    nav_bar: NavigationBar

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Screen Switcher")
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        self.stacked_widget = QStackedWidget()
        
        self.screens = [Screen1(self.stacked_widget), Screen2(self.stacked_widget),
                        Screen3(self.stacked_widget), Screen4(self.stacked_widget),
                        Screen5(self.stacked_widget)]
        
        for screen in self.screens:
            self.stacked_widget.addWidget(screen)
        
        layout.addWidget(self.stacked_widget)
        
        self.nav_bar = NavigationBar(self.stacked_widget)
        layout.addWidget(self.nav_bar)
        
        layout.setStretch(0, 9)
        layout.setStretch(1, 1)
        
        self.setLayout(layout)
        
        self.stacked_widget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())