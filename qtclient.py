import sys
from PyQt5.QtWidgets import (QAction, qApp, QApplication, QMainWindow, QMenu,
                             QMessageBox, QPushButton, QToolTip)
from PyQt5.QtGui import QFont, QIcon

""" Credit for the shark icon goes to Freepik--you can find their work
at http://www.freepik.com """


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        self.init_actions()
        self.init_statusbar()
        self.init_menu()
        self.init_toolbar()
        # self.draw_connect_btn()
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('MudShark v0.1')
        self.setWindowIcon(QIcon('shark.png'))
        self.show()

    def init_actions(self):
        # exit action
        self.exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.setStatusTip('Exit application')
        self.exitAct.triggered.connect(qApp.quit)
        # new action
        self.newAct = QAction('New', self)
        # import action
        self.importAct = QAction('Import mail', self)
        # view status action
        self.viewStatAct = QAction('View Status', self, checkable=True)
        self.viewStatAct.setStatusTip('View Status')
        self.viewStatAct.setChecked(True)
        self.viewStatAct.triggered.connect(self.toggleMenu)

    def init_statusbar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')

    def init_toolbar(self):
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(self.exitAct)

    def init_menu(self):
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        viewMenu = self.menubar.addMenu('&View')
        # File -> New
        fileMenu.addAction(self.newAct)
        # File -> Import
        importMenu = QMenu('Import', self)
        importMenu.addAction(self.importAct)
        fileMenu.addMenu(importMenu)
        # File -> Exit
        fileMenu.addAction(self.exitAct)
        # View -> View Status
        viewMenu.addAction(self.viewStatAct)

    def draw_connect_btn(self):
        connect_btn = QPushButton('Connect', self)
        connect_btn.setToolTip('Attempt Connection to Shark 200 meter')
        connect_btn.resize(connect_btn.sizeHint())
        connect_btn.move(175, 175)

##################
# EVENT HANDLING #
##################
    def toggleMenu(self, state):
        if state:
            self.statusbar.show()
        else:
            self.statusbar.hide()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            quit()

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)
        quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            qApp.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())
