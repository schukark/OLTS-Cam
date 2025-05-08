# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QSlider, QStackedWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1588, 900)
        MainWindow.setMinimumSize(QSize(800, 600))
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
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
        self.stackedWidget.addWidget(self.homePage)
        self.cameraSettingsPage = QWidget()
        self.cameraSettingsPage.setObjectName(u"cameraSettingsPage")
        self.verticalLayout_3 = QVBoxLayout(self.cameraSettingsPage)
        self.verticalLayout_3.setSpacing(10)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(20, 20, 20, 20)
        self.label_2 = QLabel(self.cameraSettingsPage)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_2)

        self.cameraIPInput = QLineEdit(self.cameraSettingsPage)
        self.cameraIPInput.setObjectName(u"cameraIPInput")
        self.cameraIPInput.setMinimumSize(QSize(0, 40))

        self.verticalLayout_3.addWidget(self.cameraIPInput)

        self.cameraPortInput = QLineEdit(self.cameraSettingsPage)
        self.cameraPortInput.setObjectName(u"cameraPortInput")
        self.cameraPortInput.setMinimumSize(QSize(0, 40))

        self.verticalLayout_3.addWidget(self.cameraPortInput)

        self.cameraLoginInput = QLineEdit(self.cameraSettingsPage)
        self.cameraLoginInput.setObjectName(u"cameraLoginInput")
        self.cameraLoginInput.setMinimumSize(QSize(0, 40))

        self.verticalLayout_3.addWidget(self.cameraLoginInput)

        self.cameraPasswordInput = QLineEdit(self.cameraSettingsPage)
        self.cameraPasswordInput.setObjectName(u"cameraPasswordInput")
        self.cameraPasswordInput.setMinimumSize(QSize(0, 40))
        self.cameraPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)

        self.verticalLayout_3.addWidget(self.cameraPasswordInput)

        self.rtspUrlInput = QLineEdit(self.cameraSettingsPage)
        self.rtspUrlInput.setObjectName(u"rtspUrlInput")
        self.rtspUrlInput.setMinimumSize(QSize(0, 40))

        self.verticalLayout_3.addWidget(self.rtspUrlInput)

        self.saveCameraSettingsButton = QPushButton(self.cameraSettingsPage)
        self.saveCameraSettingsButton.setObjectName(u"saveCameraSettingsButton")
        self.saveCameraSettingsButton.setMinimumSize(QSize(0, 50))
        font1 = QFont()
        font1.setPointSize(12)
        self.saveCameraSettingsButton.setFont(font1)

        self.verticalLayout_3.addWidget(self.saveCameraSettingsButton)

        self.stackedWidget.addWidget(self.cameraSettingsPage)
        self.modelSettingsPage = QWidget()
        self.modelSettingsPage.setObjectName(u"modelSettingsPage")
        self.verticalLayout_4 = QVBoxLayout(self.modelSettingsPage)
        self.verticalLayout_4.setSpacing(10)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(20, 20, 20, 20)
        self.label_3 = QLabel(self.modelSettingsPage)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_3)

        self.videoObjectCount = QLineEdit(self.modelSettingsPage)
        self.videoObjectCount.setObjectName(u"videoObjectCount")
        self.videoObjectCount.setMinimumSize(QSize(0, 40))

        self.verticalLayout_4.addWidget(self.videoObjectCount)

        self.fpsInput = QLineEdit(self.modelSettingsPage)
        self.fpsInput.setObjectName(u"fpsInput")
        self.fpsInput.setMinimumSize(QSize(0, 40))

        self.verticalLayout_4.addWidget(self.fpsInput)

        self.tresholdwidget = QWidget(self.modelSettingsPage)
        self.tresholdwidget.setObjectName(u"tresholdwidget")
        self.tresholdwidget.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_2 = QHBoxLayout(self.tresholdwidget)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.objectThresholdInput = QLineEdit(self.tresholdwidget)
        self.objectThresholdInput.setObjectName(u"objectThresholdInput")
        self.objectThresholdInput.setEnabled(False)
        self.objectThresholdInput.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.objectThresholdInput)

        self.horizontalSlider = QSlider(self.tresholdwidget)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setMinimum(20)
        self.horizontalSlider.setMaximum(90)
        self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_2.addWidget(self.horizontalSlider)


        self.verticalLayout_4.addWidget(self.tresholdwidget)

        self.widget = QWidget(self.modelSettingsPage)
        self.widget.setObjectName(u"widget")
        self.widget.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_4 = QHBoxLayout(self.widget)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.saveFolderInput = QLineEdit(self.widget)
        self.saveFolderInput.setObjectName(u"saveFolderInput")
        self.saveFolderInput.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.saveFolderInput.sizePolicy().hasHeightForWidth())
        self.saveFolderInput.setSizePolicy(sizePolicy1)
        self.saveFolderInput.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_4.addWidget(self.saveFolderInput)

        self.browseFolderButton = QPushButton(self.widget)
        self.browseFolderButton.setObjectName(u"browseFolderButton")
        self.browseFolderButton.setMinimumSize(QSize(100, 40))
        self.browseFolderButton.setMaximumSize(QSize(100, 40))

        self.horizontalLayout_4.addWidget(self.browseFolderButton)


        self.verticalLayout_4.addWidget(self.widget)

        self.saveModelSettingsButton = QPushButton(self.modelSettingsPage)
        self.saveModelSettingsButton.setObjectName(u"saveModelSettingsButton")
        self.saveModelSettingsButton.setMinimumSize(QSize(0, 50))
        self.saveModelSettingsButton.setFont(font1)

        self.verticalLayout_4.addWidget(self.saveModelSettingsButton)

        self.stackedWidget.addWidget(self.modelSettingsPage)
        self.videoPlaybackPage = QWidget()
        self.videoPlaybackPage.setObjectName(u"videoPlaybackPage")
        self.verticalLayout_5 = QVBoxLayout(self.videoPlaybackPage)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_4 = QLabel(self.videoPlaybackPage)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMaximumSize(QSize(16777215, 50))
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_5.addWidget(self.label_4)

        self.video_label = QLabel(self.videoPlaybackPage)
        self.video_label.setObjectName(u"video_label")
        font2 = QFont()
        font2.setPointSize(21)
        self.video_label.setFont(font2)
        self.video_label.setTextFormat(Qt.TextFormat.AutoText)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_5.addWidget(self.video_label)

        self.CheckBoxModel = QCheckBox(self.videoPlaybackPage)
        self.CheckBoxModel.setObjectName(u"CheckBoxModel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.CheckBoxModel.sizePolicy().hasHeightForWidth())
        self.CheckBoxModel.setSizePolicy(sizePolicy2)
        font3 = QFont()
        font3.setPointSize(12)
        font3.setHintingPreference(QFont.PreferNoHinting)
        self.CheckBoxModel.setFont(font3)
        self.CheckBoxModel.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout_5.addWidget(self.CheckBoxModel)

        self.stackedWidget.addWidget(self.videoPlaybackPage)

        self.verticalLayout.addWidget(self.stackedWidget)

        self.horizontalWidget = QWidget(self.centralwidget)
        self.horizontalWidget.setObjectName(u"horizontalWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.horizontalWidget.sizePolicy().hasHeightForWidth())
        self.horizontalWidget.setSizePolicy(sizePolicy3)
        self.horizontalLayout = QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.homeButton = QPushButton(self.horizontalWidget)
        self.homeButton.setObjectName(u"homeButton")
        self.homeButton.setMinimumSize(QSize(0, 135))
        font4 = QFont()
        font4.setPointSize(15)
        self.homeButton.setFont(font4)

        self.horizontalLayout.addWidget(self.homeButton)

        self.cameraSettingsButton_2 = QPushButton(self.horizontalWidget)
        self.cameraSettingsButton_2.setObjectName(u"cameraSettingsButton_2")
        self.cameraSettingsButton_2.setMinimumSize(QSize(0, 135))
        self.cameraSettingsButton_2.setFont(font4)

        self.horizontalLayout.addWidget(self.cameraSettingsButton_2)

        self.modelSettingsButton_2 = QPushButton(self.horizontalWidget)
        self.modelSettingsButton_2.setObjectName(u"modelSettingsButton_2")
        self.modelSettingsButton_2.setMinimumSize(QSize(0, 135))
        self.modelSettingsButton_2.setFont(font4)

        self.horizontalLayout.addWidget(self.modelSettingsButton_2)

        self.videoPlaybackButton_2 = QPushButton(self.horizontalWidget)
        self.videoPlaybackButton_2.setObjectName(u"videoPlaybackButton_2")
        self.videoPlaybackButton_2.setMinimumSize(QSize(0, 135))
        self.videoPlaybackButton_2.setFont(font4)

        self.horizontalLayout.addWidget(self.videoPlaybackButton_2)


        self.verticalLayout.addWidget(self.horizontalWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043a\u0430\u043c\u0435\u0440\u044b \u0438 \u0444\u0430\u0439\u043b\u043e\u0432\u043e\u0439 \u0441\u0438\u0441\u0442\u0435\u043c\u044b", None))
        self.cameraIPInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 IP \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.cameraPortInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u043e\u0440\u0442 \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.cameraLoginInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043b\u043e\u0433\u0438\u043d \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.cameraPasswordInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u0430\u0440\u043e\u043b\u044c \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.rtspUrlInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 RTSP URL", None))
        self.saveCameraSettingsButton.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043c\u043e\u0434\u0435\u043b\u0438 \u0438 \u0431\u0430\u0437\u044b \u0434\u0430\u043d\u043d\u044b\u0445", None))
        self.videoObjectCount.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0440\u0430\u0441\u043f\u043e\u0437\u043d\u0430\u0432\u0430\u0435\u043c\u044b\u0445 \u043e\u0431\u044a\u0435\u043a\u0442\u043e\u0432 \u0437\u0430 \u043a\u0430\u0434\u0440 (\u043e\u0442 3 \u0434\u043e 15)", None))
        self.fpsInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043a\u0430\u0434\u0440\u043e\u0432 \u0432 \u0441\u0435\u043a\u0443\u043d\u0434\u0443", None))
        self.objectThresholdInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u043e\u0440\u043e\u0433 \u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438 \u043e\u0431\u044a\u0435\u043a\u0442\u043e\u0432", None))
        self.saveFolderInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0430\u043f\u043a\u0443 \u0434\u043b\u044f \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f", None))
        self.browseFolderButton.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0431\u0437\u043e\u0440...", None))
        self.saveModelSettingsButton.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043c\u043e\u0434\u0435\u043b\u0438", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u0412\u043e\u0441\u043f\u0440\u043e\u0438\u0437\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0432\u0438\u0434\u0435\u043e", None))
        self.video_label.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u0432\u0438\u0434\u0435\u043e", None))
        self.CheckBoxModel.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u0431\u043e\u043a\u0441\u044b \u043e\u0431\u044a\u0435\u043a\u0442\u043e\u0432", None))
        self.homeButton.setText(QCoreApplication.translate("MainWindow", u"\u0413\u043b\u0430\u0432\u043d\u0430\u044f", None))
        self.cameraSettingsButton_2.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.modelSettingsButton_2.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043c\u043e\u0434\u0435\u043b\u0438", None))
        self.videoPlaybackButton_2.setText(QCoreApplication.translate("MainWindow", u"\u0412\u043e\u0441\u043f\u0440\u043e\u0438\u0437\u0432\u0435\u0434\u0435\u043d\u0438\u0435", None))
    # retranslateUi

