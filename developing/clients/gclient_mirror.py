import time
from ._client_robot import ClientRobot

# !/usr/bin/env python
# -*- coding: utf-8 -*-

from ._client_robot import ClientRobot
import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QPushButton


class Mirror(QtGui.QWidget):
    def __init__(self, bot):
        QtGui.QWidget.__init__(self)
        self.title = 'bot SimpleClient'
        self.left = 10
        self.top = 10
        self.width = 300
        self.height = 320
        self.bot = bot
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.layout = QtGui.QVBoxLayout(self)

        button = QPushButton('FORWARD', self)
        button.setToolTip('FORWARD')
        button.clicked.connect(self.bot_forward)
        self.layout.addWidget(button)

        button3 = QPushButton('RIGHT', self)
        button3.setToolTip('RIGHT')
        button3.clicked.connect(self.bot_right)
        self.layout.addWidget(button3)

        button4 = QPushButton('LEFT', self)
        button4.setToolTip('LEFT')
        button4.clicked.connect(self.bot_left)
        self.layout.addWidget(button4)

        button2 = QPushButton('BACKWARD', self)
        button2.setToolTip('BACKWARD')
        button2.clicked.connect(self.bot_backward)
        self.layout.addWidget(button2)

        button5 = QPushButton('STOP', self)
        button5.setToolTip('STOP')
        button5.clicked.connect(self.bot_stop)
        self.layout.addWidget(button5)

        self.show()

    def bot_forward(self):
        self.bot.mirror.set__vel(1000, 1000)

    def bot_backward(self):
        self.bot.mirror.set__vel(-1000, -1000)

    def bot_left(self):
        self.bot.mirror.set__vel(0, 1000)

    def bot_right(self):
        self.bot.mirror.set__vel(1000, 0)

    def bot_stop(self):
        self.bot.mirror.set__vel(0, 0)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        bot = ClientRobot(sys.argv[1])
        try:
            app = QtGui.QApplication(sys.argv)
            ex = Mirror(bot)
            sys.exit(app.exec_())
        except Exception:
            sys.exit()
    else:
        print("Error. Introducir nombre robot por parametro.")
