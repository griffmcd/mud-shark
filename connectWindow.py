import mudshark_client as client
import programLogView as plv
import retrieveLogView as rlv
from PyQt5.QtWidgets import (QComboBox, QDialog, QErrorMessage, QGridLayout,
                             QLabel, QLineEdit, QPushButton)


class ConnectWindow(QDialog):
    def __init__(self, parent):
        super(ConnectWindow, self).__init__()
        self.parent = parent
        self.logs = {0: 'System',
                     1: 'Alarm',
                     2: 'Hist. Log 1',
                     3: 'Hist. Log 2',
                     4: 'Hist. Log 3',
                     5: 'I/O Changes'}

        self.modes = {0: 'Program log',
                      1: 'Retrieve log'}
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
        for i in self.logs:
            self.logBox.addItem(self.logs.get(i))
        # choose mode dropdown
        self.modeLabel = QLabel('Mode: ')
        self.modeBox = QComboBox()
        for i in self.modes:
            self.modeBox.addItem(self.modes.get(i))
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
        self.parent.client = self.client
        self.parent.connected = self.connected
        # we assign these here because we need to create the client before
        # some of the functionality of these views works
        self.parent.programLogView = plv.ProgramLogWidget(self)
        self.parent.retrieveLogView = rlv.RetrieveLogWidget(self)
        self.parent.stackedWidget.addWidget(self.parent.retrieveLogView)
        self.parent.stackedWidget.addWidget(self.parent.programLogView)
        self.parent.updateMode(self.mode)
        self.parent.update_statusbar()

        self.close()

    def get_log_number(self, log_name):
        for num, log in self.logs.items():
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
