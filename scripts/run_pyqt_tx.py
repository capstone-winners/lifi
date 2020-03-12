from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QThread

import random
import weakref

import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

from Lifi.tx import LifiTx

class TransmissionWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.title = "LiFi Tx"

        self.top= 150

        self.left= 150

        self.width = 500

        self.height = 500
        self.points = []

        self.color = QColor(0,255,0)

        self.InitWindow()

    def InitWindow(self):

        self.setWindowTitle(self.title)

        self.setGeometry(self.top, self.left, self.width, self.height)

        self.show()
    
    def mousePressEvent(self, e):
        self.points.append(e.pos())

        color_list = [QColor("cyan"), QColor("magenta"), QColor("red"),
                      QColor("darkRed"), QColor("darkCyan"), QColor("darkMagenta"),
                      QColor("green"), QColor("darkGreen"), QColor("yellow"),
                      QColor("blue")];
        self.color = color_list[random.randint(0, len(color_list) - 1)]
        self.update()
    
    def paintEvent(self, event):

        painter = QPainter(self)
        self.drawRect(event, painter)
        self.drawMyPoints(event, painter)

    def drawMyPoints(self, event, qp):
        for i in range(len(self.points)):
            qp.drawEllipse(self.points[i], 5, 5)

    def drawRect(self, event, qp):
        qp.setPen(QPen(Qt.black,  5, Qt.SolidLine))
        qp.setBrush(QBrush(self.color, Qt.SolidPattern))
        qp.drawRect(40, 40, 400, 200)

    def set_pixels(self, color):
        self.color = QColor.fromRgb(*(color[0][0]))

    def show_colors(self):
        self.update()

class UpdaterThread(QThread):

    def __init__(self, window):
        self.window = weakref.ref(window)
        super().__init__()

        print(self.window)
    
    def run(self):
        print("running updater thread!")
        tx = LifiTx(self.window)
        tx.run(69)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransmissionWindow()
    window.show()
    
    thread = UpdaterThread(window)
    thread.finished.connect(app.exit)
    thread.start()

    sys.exit(app.exec_())

