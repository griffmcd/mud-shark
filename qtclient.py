import sys
import connectWindow as cw
import programLogView as plv
import retrieveLogView as rlv
from PyQt5.QtWidgets import (QAction, qApp, QApplication, QHBoxLayout, QLabel,
                             QMainWindow, QMenu, QSizePolicy, QStackedWidget,
                             QWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (pyqtSignal, QObject)


class InitialWidget(QWidget):
    def __init__(self, parent):
        super(InitialWidget, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()
        self.welcomeMessage = QLabel("Please Connect to a Meter.")
        self.welcomeMessage.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                                      QSizePolicy.Fixed))
        self.welcomeMessage.setMinimumHeight(300)
        self.welcomeMessage.setMinimumWidth(200)
        self.layout.addWidget(self.welcomeMessage)
        self.setLayout(self.layout)


class ModeChange(QObject):
    modeChange = pyqtSignal()


class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()

        self.initUI()

    def initUI(self):
        self.init_actions()
        self.host = "None"
        self.port = "None"
        self.log_name = "None"
        self.mode = "None"
        self.connected = False
        self.modeChangeSignal = ModeChange()
        self.client = None
        self.init_statusbar()
        self.init_menu()
        self.init_toolbar()
        self.setGeometry(150, 150, 800, 600)
        self.setWindowTitle('MudShark v0.1')
        self.programLogWidget = plv.ProgramLogWidget(self)
        self.retrieveLogWidget = rlv.RetrieveLogWidget(self)
        self.initialWidget = InitialWidget(self)
        self.widgetStack = QStackedWidget()
        self.widgetStack.addWidget(self.initialWidget)
        self.widgetStack.addWidget(self.retrieveLogWidget)
        self.widgetStack.addWidget(self.programLogWidget)
        self.widgetStack.setCurrentWidget(self.initialWidget)
        self.setCentralWidget(self.widgetStack)
        self.show()

    def updateMode(self, mode):
        self.mode = mode
        self.modeChangeSignal.modeChange.connect(self.update_view)
        self.modeChangeSignal.modeChange.emit()

    def update_view(self):
        if self.mode == "None":
            self.widgetStack.setCurrentWidget(self.initialWidget)
        elif self.mode == "Program log":
            self.widgetStack.setCurrentWidget(self.programLogWidget)
        elif self.mode == "Retrieve log":
            self.widgetStack.setCurrentWidget(self.retrieveLogWidget)

    def init_actions(self):
        # exit action
        self.exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.setStatusTip('Exit application')
        self.exitAct.triggered.connect(qApp.quit)
        # connect action
        self.fileConnectAct = QAction(QIcon('connect.png'), 'Connect', self)
        self.fileConnectAct.setShortcut('Ctrl+C')
        self.fileConnectAct.setStatusTip('Connect to a Modbus Meter')
        self.fileConnectAct.triggered.connect(self.connect_popup)
        # disconnect action
        self.fileDisconnectAct = QAction(QIcon('disconnect.png'), 'Disconnect',
                                         self)
        self.fileDisconnectAct.setShortcut('Ctrl+D')
        self.fileDisconnectAct.setStatusTip('Disconnect from current'
                                            ' connection')
        self.fileDisconnectAct.triggered.connect(self.disconnect)

    def connect_popup(self):
        self.ConnectionWindow = cw.ConnectWindow(self)
        self.ConnectionWindow.show()

    def disconnect(self):
        self.host = "None"
        self.port = "None"
        self.log_name = "None"
        self.updateMode("None")
        self.Connected = True
        self.update_statusbar()
        if self.client is not None:
            self.client.close()

    def init_statusbar(self):
        self.statusMessage = QLabel()
        statusString = ("Host: " + self.host + "  |  Port: " + self.port
                        + "  |  Log: " + self.log_name + "  |  Mode: "
                        + self.mode + "  |  Connected: " + str(self.connected))
        self.statusMessage.setText(statusString)
        self.statusBar().addPermanentWidget(self.statusMessage)

    def update_statusbar(self):
        self.statusBar().removeWidget(self.statusMessage)
        statusString = ("Host: " + self.host + "  |  Port: " + self.port
                        + "  |  Log: " + self.log_name + "  |  Mode: "
                        + self.mode + "  |  Connected: " + str(self.connected))
        self.statusMessage = QLabel()
        self.statusMessage.setText(statusString)
        self.statusBar().addPermanentWidget(self.statusMessage)

    def init_toolbar(self):
        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.addAction(self.fileConnectAct)
        self.toolbar.addAction(self.fileDisconnectAct)
        self.toolbar.addAction(self.exitAct)

    def init_menu(self):
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        # File -> Connect
        fileMenu.addAction(self.fileConnectAct)
        # File -> Disconnect
        fileMenu.addAction(self.fileDisconnectAct)
        # File -> Exit
        fileMenu.addAction(self.exitAct)

##################
# EVENT HANDLING #
##################
    def toggleMenu(self, state):
        if state:
            self.statusbar.show()
        else:
            self.statusbar.hide()

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
