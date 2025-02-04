from PySide6.QtWidgets import QApplication, QWidget, QLabel, QStackedWidget, QVBoxLayout, QSizePolicy, QSpacerItem, QHBoxLayout
from PySide6.QtCore import Qt

from ScreenBase import ScreenBase

class Screen1(ScreenBase):
    right_layout: QVBoxLayout
    title: QLabel
    description: QLabel
    right_widget: QWidget

    def __init__(self, stacked_widget: QStackedWidget) -> None:
        super().__init__('About', stacked_widget)

        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        self.title = QLabel("Система отслеживания местоположения вещей с использованием камер (OLTS-Cam)")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.description = QLabel(
            '''OLTS-Cam — это интегрированное решение для мониторинга и управления местоположением физических объектов в реальном времени с помощью камер видеонаблюдения и технологий компьютерного зрения. Система использует алгоритмы обработки изображений для распознавания объектов, их классификации и отслеживания их перемещений в пределах заданного пространства.
            
\tОна предоставляет пользователю возможность получать точную информацию о местоположении вещей через интерфейс десктопного приложения или Telegram-бота.
            
\tРазработчики: И. А. Яковлев и А. А. Щукин.'''
        )
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
        self.description.setStyleSheet("""
            font-size: 14px;
            line-height: 1.5;
            font-family: Arial, sans-serif;
        """)

        self.description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        screen_width = self.width()
        description_width = int(screen_width * 0.8)
        self.description.setMaximumWidth(int(screen_width * 0.8))
        self.description.setMinimumWidth(int(screen_width * 0.5))
        self.description.setFixedWidth(description_width)

        left_spacer = QSpacerItem(int(screen_width * 0.2), 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        right_spacer = QSpacerItem(int(screen_width * 0.2), 0, QSizePolicy.Fixed, QSizePolicy.Minimum)

        title_layout = QHBoxLayout()
        title_layout.addItem(left_spacer)
        title_layout.addWidget(self.title)
        title_layout.addItem(right_spacer)

        description_layout = QHBoxLayout()
        description_layout.addItem(left_spacer)
        description_layout.addWidget(self.description)
        description_layout.addItem(right_spacer)

        self.right_layout.addStretch(1)
        self.right_layout.addLayout(title_layout)
        self.right_layout.addLayout(description_layout)
        self.right_layout.addStretch(2)

        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)

        self.layout.addWidget(self.right_widget, alignment=Qt.AlignRight)

        self.setLayout(self.layout)