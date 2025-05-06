# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'untitled2.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QStackedWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1600, 900)
        MainWindow.setMinimumSize(QSize(800, 600))
        #MainWindow.setMaximumSize(QSize(1920, 1080))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.homePage = QWidget()
        self.homePage.setObjectName(u"homePage")
        self.verticalLayout_2 = QVBoxLayout(self.homePage)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        #self.label = QLabel(self.homePage)
        #self.label.setObjectName(u"label")
        #self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #self.verticalLayout_2.addWidget(self.label)

        self.stackedWidget.addWidget(self.homePage)
        self.cameraSettingsPage = QWidget()
        self.cameraSettingsPage.setObjectName(u"cameraSettingsPage")
        self.verticalLayout_3 = QVBoxLayout(self.cameraSettingsPage)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_2 = QLabel(self.cameraSettingsPage)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_2)

        self.cameraIPInput = QLineEdit(self.cameraSettingsPage)
        self.cameraIPInput.setObjectName(u"cameraIPInput")

        self.verticalLayout_3.addWidget(self.cameraIPInput)

        self.cameraPortInput = QLineEdit(self.cameraSettingsPage)
        self.cameraPortInput.setObjectName(u"cameraPortInput")

        self.verticalLayout_3.addWidget(self.cameraPortInput)

        self.cameraLoginInput = QLineEdit(self.cameraSettingsPage)
        self.cameraLoginInput.setObjectName(u"cameraLoginInput")

        self.verticalLayout_3.addWidget(self.cameraLoginInput)

        self.cameraPasswordInput = QLineEdit(self.cameraSettingsPage)
        self.cameraPasswordInput.setObjectName(u"cameraPasswordInput")

        self.verticalLayout_3.addWidget(self.cameraPasswordInput)

        self.rtspUrlInput = QLineEdit(self.cameraSettingsPage)
        self.rtspUrlInput.setObjectName(u"rtspUrlInput")

        self.verticalLayout_3.addWidget(self.rtspUrlInput)

        self.saveCameraSettingsButton = QPushButton(self.cameraSettingsPage)
        self.saveCameraSettingsButton.setObjectName(u"saveCameraSettingsButton")

        self.verticalLayout_3.addWidget(self.saveCameraSettingsButton)

        self.stackedWidget.addWidget(self.cameraSettingsPage)
        self.modelSettingsPage = QWidget()
        self.modelSettingsPage.setObjectName(u"modelSettingsPage")
        self.verticalLayout_4 = QVBoxLayout(self.modelSettingsPage)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_3 = QLabel(self.modelSettingsPage)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_3)

        self.videoResolutionInput = QLineEdit(self.modelSettingsPage)
        self.videoResolutionInput.setObjectName(u"videoResolutionInput")

        self.verticalLayout_4.addWidget(self.videoResolutionInput)

        self.fpsInput = QLineEdit(self.modelSettingsPage)
        self.fpsInput.setObjectName(u"fpsInput")

        self.verticalLayout_4.addWidget(self.fpsInput)

        self.saveVideoCheckbox = QCheckBox(self.modelSettingsPage)
        self.saveVideoCheckbox.setObjectName(u"saveVideoCheckbox")

        self.verticalLayout_4.addWidget(self.saveVideoCheckbox)

        self.objectThresholdInput = QLineEdit(self.modelSettingsPage)
        self.objectThresholdInput.setObjectName(u"objectThresholdInput")

        self.verticalLayout_4.addWidget(self.objectThresholdInput)

        self.saveModelSettingsButton = QPushButton(self.modelSettingsPage)
        self.saveModelSettingsButton.setObjectName(u"saveModelSettingsButton")

        self.verticalLayout_4.addWidget(self.saveModelSettingsButton)

        self.stackedWidget.addWidget(self.modelSettingsPage)
        self.videoPlaybackPage = QWidget()
        self.videoPlaybackPage.setObjectName(u"videoPlaybackPage")
        self.verticalLayout_5 = QVBoxLayout(self.videoPlaybackPage)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_4 = QLabel(self.videoPlaybackPage)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_5.addWidget(self.label_4)

        self.videoWidget = QVideoWidget(self.videoPlaybackPage)
        self.videoWidget.setObjectName(u"videoWidget")
        sizePolicy.setHeightForWidth(self.videoWidget.sizePolicy().hasHeightForWidth())
        self.videoWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_5.addWidget(self.videoWidget)

        self.stackedWidget.addWidget(self.videoPlaybackPage)

        self.verticalLayout.addWidget(self.stackedWidget)

        self.horizontalWidget = QWidget(self.centralwidget)
        self.horizontalWidget.setObjectName(u"horizontalWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.horizontalWidget.sizePolicy().hasHeightForWidth())
        self.horizontalWidget.setSizePolicy(sizePolicy1)
        self.horizontalWidget.setMinimumHeight(135)
        self.horizontalLayout = QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.homeButton = QPushButton(self.horizontalWidget)
        self.homeButton.setObjectName(u"homeButton")
        self.homeButton.setMinimumSize(QSize(0, 135))

        self.horizontalLayout.addWidget(self.homeButton)

        self.cameraSettingsButton_2 = QPushButton(self.horizontalWidget)
        self.cameraSettingsButton_2.setObjectName(u"cameraSettingsButton_2")
        self.cameraSettingsButton_2.setMinimumSize(QSize(0, 135))

        self.horizontalLayout.addWidget(self.cameraSettingsButton_2)

        self.modelSettingsButton_2 = QPushButton(self.horizontalWidget)
        self.modelSettingsButton_2.setObjectName(u"modelSettingsButton_2")
        self.modelSettingsButton_2.setMinimumSize(QSize(0, 135))

        self.horizontalLayout.addWidget(self.modelSettingsButton_2)

        self.videoPlaybackButton_2 = QPushButton(self.horizontalWidget)
        self.videoPlaybackButton_2.setObjectName(u"videoPlaybackButton_2")
        self.videoPlaybackButton_2.setMinimumSize(QSize(0, 135))

        self.horizontalLayout.addWidget(self.videoPlaybackButton_2)


        self.verticalLayout.addWidget(self.horizontalWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        #self.label.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c \u0432 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435!", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043a\u0430\u043c\u0435\u0440\u044b \u0438 \u0444\u0430\u0439\u043b\u043e\u0432\u043e\u0439 \u0441\u0438\u0441\u0442\u0435\u043c\u044b", None))
        self.cameraIPInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 IP \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.cameraPortInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u043e\u0440\u0442 \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.cameraLoginInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043b\u043e\u0433\u0438\u043d \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.cameraPasswordInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u0430\u0440\u043e\u043b\u044c \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.rtspUrlInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 RTSP URL", None))
        self.saveCameraSettingsButton.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043c\u043e\u0434\u0435\u043b\u0438 \u0438 \u0431\u0430\u0437\u044b \u0434\u0430\u043d\u043d\u044b\u0445", None))
        self.videoResolutionInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u0432\u0438\u0434\u0435\u043e", None))
        self.fpsInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043a\u0430\u0434\u0440\u043e\u0432 \u0432 \u0441\u0435\u043a\u0443\u043d\u0434\u0443", None))
        self.saveVideoCheckbox.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u044f\u0442\u044c \u0432\u0438\u0434\u0435\u043e \u0441 \u043e\u0431\u043d\u0430\u0440\u0443\u0436\u0435\u043d\u043d\u044b\u043c\u0438 \u043e\u0431\u044a\u0435\u043a\u0442\u0430\u043c\u0438", None))
        self.objectThresholdInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u043e\u0440\u043e\u0433 \u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438 \u043e\u0431\u044a\u0435\u043a\u0442\u043e\u0432", None))
        self.saveModelSettingsButton.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043c\u043e\u0434\u0435\u043b\u0438", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u0412\u043e\u0441\u043f\u0440\u043e\u0438\u0437\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0432\u0438\u0434\u0435\u043e", None))
        self.homeButton.setText(QCoreApplication.translate("MainWindow", u"\u0413\u043b\u0430\u0432\u043d\u0430\u044f", None))
        self.cameraSettingsButton_2.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.modelSettingsButton_2.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043c\u043e\u0434\u0435\u043b\u0438", None))
        self.videoPlaybackButton_2.setText(QCoreApplication.translate("MainWindow", u"\u0412\u043e\u0441\u043f\u0440\u043e\u0438\u0437\u0432\u0435\u0434\u0435\u043d\u0438\u0435", None))
    # retranslateUi

