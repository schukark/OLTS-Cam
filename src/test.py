import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setGeometry(400,400,400,300)
        MainWindow.setWindowTitle("Построение Windows GUI")
        MainWindow.textBox1 = QTextEdit("TextBox 1")
        MainWindow.textBox2 = QTextEdit("TextBox 2")
        MainWindow.textBox3 = QTextEdit("TextBox 3")
        MainWindow.textBox4 = QTextEdit("TextBox 4")

        layout = QWidget()
        layout.setLayout(QVBoxLayout())
        layout.layout().addWidget(MainWindow.textBox1)
        layout.layout().addWidget(MainWindow.textBox2)
        layout.layout().addWidget(MainWindow.textBox3)
        layout.layout().addWidget(MainWindow.textBox4)

        MainWindow.setCentralWidget(layout)
        
if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())