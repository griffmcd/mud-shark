import sys
import connectWindow as cw
import client as client
from PyQt5.QtWidgets import (QAction, qApp, QApplication, QLabel, QMainWindow,
                             QMenu, QSizePolicy, QStackedWidget, QWidget,
                             QMenuBar, QStatusBar, QVBoxLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (pyqtSignal, QObject, QRect)


class InitialView(QWidget):
    def __init__(self, parent):
        super(InitialView, self).__init__()
        self.parent = parent
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)
        self.initUI()

    def initUI(self):
        self.initialViewLabel = QLabel(self)
        self.initialViewLabel.setGeometry(QRect(290, 290, 220, 20))
        self.initialViewLabel.setText("Pleace connect to a meter. (Alt + C)")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.initialViewLabel.sizePolicy().hasHeightForWidth())
        self.initialViewLabel.setSizePolicy(sizePolicy)

        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 781, 581))

        self.initialWidgetLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.initialWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutWidget.raise_()
        self.initialViewLabel.raise_()


class ModeChange(QObject):
    modeChange = pyqtSignal()


class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        self.title = "MudShark v0.1"
        self.setWindowTitle(self.title)
        self.defWidth = 800
        self.defHeight = 600
        # self.setGeometry(100, 100, self.defWidth, self.defHeight)
        self.resize(self.defWidth, self.defHeight)
        self.host = "None"
        self.port = "None"
        self.log_name = "None"
        self.log_num = 0
        self.mode = "None"
        self.connected = False
        self.client = None
        self.recSize = 0
        self.rpw = 0
        self.numRecs = 0
        self.init_actions()
        self.modeChangeSignal = ModeChange()
        self.initUI()

    def initUI(self):
        # central widget contains a widget containing a vertical layout,
        # and that widget contains the stacked widget
        self.centralWidget = QWidget(self)
        self.centerVLayoutWidget = QWidget(self.centralWidget)
        self.centerVLayoutWidget.setGeometry(QRect(0, 0, 800, 550))
        self.centralWidLayout = QVBoxLayout(self.centerVLayoutWidget)
        self.centralWidLayout.setContentsMargins(0, 0, 0, 0)

        # stacked widget is contained inside centralWidLayout
        self.stackedWidget = QStackedWidget(self.centerVLayoutWidget)

        # this is where we instantiate the different views inside stackedWidget
        self.initialView = InitialView(self)
        self.stackedWidget.addWidget(self.initialView)
        self.stackedWidget.setCurrentWidget(self.initialView)
        self.centralWidLayout.addWidget(self.stackedWidget)

        self.setCentralWidget(self.centralWidget)

        self.init_menu()
        self.init_statusbar()
        self.init_toolbar()
        self.show()

    def updateMode(self, mode):
        self.mode = mode
        self.modeChangeSignal.modeChange.connect(self.update_view)
        self.modeChangeSignal.modeChange.emit()

    def update_view(self):
        if self.mode == "None":
            self.stackedWidget.setCurrentWidget(self.initialView)
        elif self.mode == "Program log":
            self.stackedWidget.setCurrentWidget(self.programLogView)
        elif self.mode == "Retrieve log":
            self.logDet = client.engage_log(self.client, self.log_num, 0)
            self.recSize = self.logDet.record_size
            self.rpw = self.logDet.records_per_window
            self.numRecs = (self.logDet.max_records
                            / self.logDet.records_per_window)
            self.records = client.retrieve_records(self.client,
                                                   self.logDet.records_per_window,
                                                   self.logDet.max_records,
                                                   self.logDet.record_size)
            client.disengage_log(self.client, self.log_num)
            self.stackedWidget.setCurrentWidget(self.retrieveLogView)

    def init_actions(self):
        # exit action
        self.exitAct = QAction(QIcon('icons/exit.png'), '&Exit', self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.setStatusTip('Exit application')
        self.exitAct.setText("Exit")
        self.exitAct.triggered.connect(qApp.quit)
        # connect action
        self.connectAct = QAction(QIcon('icons/connect.png'), 'Connect', self)
        self.connectAct.setShortcut('Alt+C')
        self.connectAct.setStatusTip('Connect to a Modbus Meter')
        self.connectAct.setText("Connect")
        self.connectAct.triggered.connect(self.connect_popup)
        # disconnect action
        self.disconnectAct = QAction(QIcon('icons/disconnect.png'), 'Disconnect',
                                     self)
        self.disconnectAct.setShortcut('Ctrl+D')
        self.disconnectAct.setText("Disconnect")
        self.disconnectAct.setStatusTip('Disconnect from current'
                                        ' connection')
        self.disconnectAct.triggered.connect(self.disconnect)
        # export as action
        self.exportAsAct = QAction('Export As..', self)
        self.exportAsAct.setShortcut('Ctrl+e')
        self.exportAsAct.setText('Export As..')
        # help action
        self.helpAct = QAction('Help', self)
        self.helpAct.setShortcut('Ctrl+h')
        self.helpAct.setText('Help')
        # about the author action
        self.aboutAuthAct = QAction('About the Author', self)
        self.aboutAuthAct.setText('About the Author')


    def connect_popup(self):
        self.ConnectionWindow = cw.ConnectWindow(self)
        self.ConnectionWindow.show()

    def disconnect(self):
        self.host = "None"
        self.port = "None"
        self.log_name = "None"
        self.connected = False
        self.updateMode("None")
        self.update_statusbar()
        if self.client is not None:
            self.client.close()

    def init_statusbar(self):
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
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
        self.toolbar.addAction(self.connectAct)
        self.toolbar.addAction(self.disconnectAct)
        self.toolbar.addAction(self.exitAct)

    def init_menu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 800, 20))

        self.menuFile = QMenu(self.menubar)
        self.menuFile.setTitle("File")
        self.menuAbout = QMenu(self.menubar)
        self.menuAbout.setTitle("About")
        self.setMenuBar(self.menubar)
        # File -> Connect
        self.menuFile.addAction(self.connectAct)
        # File -> Disconnect
        self.menuFile.addAction(self.disconnectAct)
        self.menuFile.addSeparator()
        # File -> Export As..
        self.menuFile.addAction(self.exportAsAct)
        self.menuFile.addSeparator()
        # File -> Exit
        self.menuFile.addAction(self.exitAct)

        # About -> Help
        self.menuAbout.addAction(self.helpAct)
        # About -> About the Author
        self.menuAbout.addAction(self.aboutAuthAct)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())



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
