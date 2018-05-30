import sys
import client
from PyQt5.QtWidgets import (QAction, qApp, QApplication, QComboBox,
                             QDialog, QErrorMessage, QFrame, QGridLayout,
                             QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMainWindow, QMenu, QMessageBox, QPushButton,
                             QToolTip, QWidget)
from PyQt5.QtGui import QFont, QIcon

logs = {0: 'System',
        1: 'Alarm',
        2: 'Hist. Log 1',
        3: 'Hist. Log 2',
        4: 'Hist. Log 3',
        5: 'I/O Changes'}

modes = {0: 'Program log',
         1: 'Retrieve log'}

intervals = ["1 minute", "3 minutes", "5 minutes", "10 minutes", "15 minutes",
             "30 minutes", "60 minutes", "End of Interval Pulse"]

measured_values = ["Instant Voltage L-N", "Max Voltage L-N", "Min Voltage L-N",
                   "Instant Voltage L-L", "Max Voltage L-L", "Min Voltage L-L",

                   "Instant Current per Phase", "Average Current per Phase",
                   "Max Current per Phase", "Min Current per Phase",

                   "Instant Current Neutral", "Average Current Neutral",
                   "Max Current Neutral", "Min Current Neutral",

                   "Instant Total Watts", "Average Total Watts",
                   "Max Total Watts", "Min Total Watts",
                   "Instant A Watts", "Average A Watts", "Max A Watts",
                   "Min A Watts",
                   "Instant B Watts", "Average B Watts", "Max B Watts",
                   "Min B Watts",
                   "Instant C Watts", "Average C Watts", "Max C Watts",
                   "Min C Watts",

                   "Instant Total Var", "Average Total Var", "Max Total Var",
                   "Min Total Var",
                   "Instant A Var", "Average A Var", "Max A Var", "Min A Var",
                   "Instant B Var", "Average B Var", "Max B Var", "Min B Var",
                   "Instant C Var", "Average C Var", "Max C Var", "Min C Var",

                   "Instant Total VA", "Average Total VA", "Max Total VA",
                   "Min Total VA",
                   "Instant A VA", "Average A VA", "Max A VA", "Min A VA",
                   "Instant B VA", "Average B VA", "Max B VA", "Min B VA",
                   "Instant C VA", "Average C VA", "Max C VA", "Min C VA",

                   "Instant Total PF", "Average Total PF", "Max Total PF",
                   "Min Total PF",
                   "Instant A PF", "Average A PF", "Max A PF", "Min A PF",
                   "Instant B PF", "Average B PF", "Max B PF", "Min B PF",
                   "Instant C PF", "Average C PF", "Max C PF", "Min C PF",

                   "Total Watt Hours", "A Watt Hours", "B Watt Hours",
                   "C Watt Hours",

                   "Total -Wh", "A -Wh", "B -Wh", "C -Wh",
                   "Wh Net",
                   "Total +VARh", "A +VARh", "B +VARh", "C +VARh",
                   "Total -VARh", "A -VARh", "B -VARh", "C -VARh",
                   "Total VARh Net", "A VARh Net", "B VARh Net", "C VARh Net",
                   "Total VAh", "A VAh", "B VAh", "C VAh",
                   "Instant Frequency", "Max Frequency", "Min Frequency",
                   "Harmonics to the 40th Order",
                   "Instant THD", "Max THD", "Min THD",
                   "Voltage Angles", "Current Angles", "% of Load Bar"]


class MeterValuesListWidget(QListWidget):
    def __init__(self, parent):
        super(MeterValuesListWidget, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        for value in measured_values:
            self.addItem(QListWidgetItem(value, self).setCheckState(0))


class ProgramLogView(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.intervalLabel = QLabel("Interval: ")
        self.intervalBox = QComboBox()
        for interval in intervals:
            self.intervalBox.addItem(interval)
        self.sectorLabel = QLabel("Sectors: ")
        self.sectorBox = QComboBox()
        for i in range(0, 16):
            self.sectorBox.addItem(str(i))
        self.submitButton = QPushButton("Submit")
        self.submitButton.clicked.connect(self.submit_button_push)
        self.clearButton = QPushButton("Clear")
        self.clearButton.clicked.connect(self.reset_program_log_view)
        self.meterValLabel = QLabel("Values to Log:")
        self.meterValWidget = MeterValuesListWidget(self)
        self.grid.addWidget(self.intervalLabel, 0, 0)
        self.grid.addWidget(self.intervalBox, 0, 1)
        self.grid.addWidget(self.sectorLabel, 1, 0)
        self.grid.addWidget(self.sectorBox, 1, 1)
        self.grid.addWidget(self.meterValLabel, 0, 2)
        self.grid.addWidget(self.meterValWidget, 1, 2)
        self.grid.addWidget(self.submitButton, 3, 1)
        self.grid.addWidget(self.clearButton, 3, 0)
        # Memstats Frame
        self.grid.setColumnStretch(1, 1)
        self.grid.setColumnStretch(0, 1)
        self.setLayout(self.grid)

    def submit_button_push(self):
        print("Pushed submit")

    def reset_program_log_view(self):
        print("Pushed reset")


class ConnectWindow(QDialog):
    def __init__(self, parent):
        super(ConnectWindow, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        # host entry box
        self.hostLabel = QLabel('Host: ')
        self.hostBox = QLineEdit()
        # port entry box
        self.portLabel = QLabel('Port: ')
        self.portBox = QLineEdit()
        # choose log dropdown
        self.logLabel = QLabel('Log: ')
        self.logBox = QComboBox()
        for i in logs:
            self.logBox.addItem(logs.get(i))
        # choose mode dropdown
        self.modeLabel = QLabel('Mode: ')
        self.modeBox = QComboBox()
        for i in modes:
            self.modeBox.addItem(modes.get(i))
        # connect button
        self.connectBtn = QPushButton('Connect')
        self.connectBtn.clicked.connect(self.attempt_connection)
        # close button
        self.closeBtn = QPushButton('Close')
        self.closeBtn.clicked.connect(self.close)
        # add all widgets
        self.grid.addWidget(self.hostLabel, 1, 0)
        self.grid.addWidget(self.hostBox, 1, 1)
        self.grid.addWidget(self.portLabel, 2, 0)
        self.grid.addWidget(self.portBox, 2, 1)
        self.grid.addWidget(self.logLabel, 3, 0)
        self.grid.addWidget(self.logBox, 3, 1)
        self.grid.addWidget(self.modeLabel, 4, 0)
        self.grid.addWidget(self.modeBox, 4, 1)
        self.grid.addWidget(self.connectBtn, 5, 1)
        self.grid.addWidget(self.closeBtn, 5, 0)

        self.setLayout(self.grid)
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Connect to Server')

    def attempt_connection(self):
        """Saves the entered information (Host, Port, Log, and Mode) and attemtps
        a connection. Throws an error dialog if it does not succeed. Otherwise
        it will close the connection dialog and show the appropriate view in
        the main window (for programming or retrieving the logs)"""
        self.host = self.hostBox.text()
        self.port = self.portBox.text()
        self.log_name = str(self.logBox.currentText())
        self.log_num = self.get_log_number(self.log_name)
        self.mode = str(self.modeBox.currentText())
        if not self.log_mode_programmable():
            self.incomp_mode_err = QErrorMessage()
            self.incomp_mode_err.showMessage('Incompatible mode: can only '
                                             + 'program historical logs 1, 2, '
                                             + 'and 3')
            return
        while True:
            try:
                self.client = client.connect(self.host, self.port)
                self.connected = True
                break
            except Exception as e:
                self.connection_failed_err = QErrorMessage()
                self.connection_failed_err.showMessage('Failed to connect to'
                                                       + ' meter')
                return
        self.parent.host = self.host
        self.parent.port = self.port
        self.parent.log_name = self.log_name
        self.parent.log_num = self.log_num
        self.parent.mode = self.mode
        self.parent.connected = True
        self.parent.update_statusbar()
        self.close()

    def get_log_number(self, log_name):
        for num, log in logs.items():
            if log == log_name:
                return num

    def log_mode_programmable(self):
        if self.mode == 'Retrieve log':
            return True
        elif self.mode == 'Program log':
            if self.log_num == 2 or self.log_num == 3 or self.log_num == 4:
                return True
            else:
                return False


class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        self.initUI()

    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        self.init_actions()
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.host = "None"
        self.port = "None"
        self.log_name = "None"
        self.mode = "None"
        self.connected = False
        self.client = None
        self.init_statusbar()
        self.init_menu()
        self.init_toolbar()
        self.programLogView = ProgramLogView(self)
        self.setCentralWidget(self.programLogView)
        self.setGeometry(150, 150, 800, 600)
        self.setWindowTitle('MudShark v0.1')
        self.show()

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
        self.ConnectionWindow = ConnectWindow(self)
        self.ConnectionWindow.show()

    def disconnect(self):
        self.host = "None"
        self.port = "None"
        self.log_name = "None"
        self.mode = "None"
        self.connected = False
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
