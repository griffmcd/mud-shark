import client
from PyQt5.QtWidgets import (QComboBox, QFormLayout, QLabel, QListWidget,
                             QListWidgetItem, QHBoxLayout, QVBoxLayout,
                             QWidget, QFrame, QDialogButtonBox, QDialog)

from PyQt5.QtCore import QRect, Qt, QSize

values_register_list = {"Volts A-N": [0x116], "Volts B-N": [0x117],
                        "Volts C-N": [0x118], "Amps A": [0x11c],
                        "Amps B": [0x3F3, 0x3f4], "Amps C": [0x03f7, 0x03f8],
                        "Watts 3-Ph Total": [0x03f9, 0x03fa],
                        "VARs 3-Ph Total": [0x03fb, 0x03fc],
                        "VAs 3-Ph Total": [0x03fd, 0x03fe],
                        "Power Factor 3-Ph total": [0x03ff, 0x0400],
                        "Frequency": [0x0401, 0x0402],
                        "Neutral Current": [0x0403, 0x0404],
                        "W-Hours Received": [0x05db, 0x05dc],
                        "W-Hours Delivered": [0x05dd, 0x05de],
                        "W-Hours Net": [0x05df, 0x05e0],
                        "VAR-hours Net": [0x05e7, 0x05e8],
                        "VAR-hours Total": [0x05e9, 0x05ea],
                        "VA-hours Total": [0x05eb, 0x05ec],
                        "Amps A Average": [0x07cf, 0x07ce],
                        "Amps B Average": [0x07d1, 0x07d2],
                        "Amps C Average": [0x07d3, 0x07d4],
                        "Watts 3-Ph Average": [0x07d5, 0x07d6],
                        "VARs 3-Ph Average": [0x07d7, 0x07d8],
                        "VAs 3-Ph Average": [0x07dd, 0x07de],
                        "Neutral Current Average": [0x07e3, 0x07e4],
                        "W-Hours Total": [0x0bdd, 0x0bde]}
measured_values = ["Volts A-N", "Volts B-N", "Volts C-N", "Amps A", "Amps B",
                   "Amps C", "Watts 3-Ph Total", "VARs 3-Ph Total",
                   "VAs 3-Ph Total", "Power Factor 3-Ph total", "Frequency",
                   "Neutral Current", "W-Hours Received", "W-Hours Delivered",
                   "W-Hours Net", "VAR-hours Net", "VAR-hours Total",
                   "VA-hours Total", "Amps A Average", "Amps B Average",
                   "Amps C Average", "Watts 3-Ph Average",
                   "VARs 3-Ph Average", "VAs 3-Ph Average",
                   "Neutral Current Average", "W-Hours Total"]


class ProgramLogWidget(QDialog):
    def __init__(self, parent):
        super(ProgramLogWidget, self).__init__()
        self.parent = parent
        self.intervals = ["1 minute", "3 minutes", "5 minutes", "10 minutes",
                          "15 minutes", "30 minutes", "60 minutes",
                          "End of Interval Pulse"]
        self.title = "ProgramLogView"
        self.setWindowTitle(self.title)
        self.width = 781
        self.height = 531
        self.resize(self.width, self.height)
        self.numSelected = 0
        self.maxPerLog = 64
        self.selectedValues = []
        self.selectedRegisters = []
        self.initUI()

    def initUI(self):
        self.horizontalLayoutWidget = QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QRect(10, 10, 781, 531))

        self.plvHorizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.plvHorizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.logSettingsWidget = QWidget(self.horizontalLayoutWidget)
        self.formLayoutWidget = QWidget(self.logSettingsWidget)
        self.formLayoutWidget.setGeometry(QRect(10, 10, 361, 511))

        self.logSettingsLayout = QFormLayout(self.formLayoutWidget)
        self.logSettingsLayout.setContentsMargins(0, 0, 0, 0)
        self.logSettingsLayout.setVerticalSpacing(15)
        # log settings header
        self.logSettingsHeader = QLabel(self.formLayoutWidget)
        self.logSettingsHeader.setText("Log Settings")
        self.logSettingsLayout.setWidget(0, QFormLayout.LabelRole,
                                         self.logSettingsHeader)
        # interval label
        self.intervalLabel = QLabel(self.formLayoutWidget)
        self.intervalLabel.setText("Interval: ")
        self.logSettingsLayout.setWidget(1, QFormLayout.LabelRole,
                                         self.intervalLabel)
        # interval box
        self.intervalBox = QComboBox(self.formLayoutWidget)
        for interval in self.intervals:
            self.intervalBox.addItem(interval)
        self.logSettingsLayout.setWidget(1, QFormLayout.FieldRole,
                                         self.intervalBox)

        self.sectorsLabel = QLabel(self.formLayoutWidget)
        self.sectorsLabel.setText("Sectors: ")
        self.logSettingsLayout.setWidget(2, QFormLayout.LabelRole,
                                         self.sectorsLabel)

        self.buttonBox = QDialogButtonBox(self.formLayoutWidget)
        self.buttonBox.setGeometry(QRect(10, 550, 781, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel |
                                          QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.submit_settings)
        self.buttonBox.rejected.connect(self.clear_settings)

        self.logSettingsLayout.addWidget(self.buttonBox)

        self.sectorBox = QComboBox(self.formLayoutWidget)
        for i in range(0, 16):
            self.sectorBox.addItem(str(i))
        self.sectorToolTip = "The number of Flash Sectors allocated to this log. \n Each sector is 64 kb, minus a sector header of 20 bytes. \n 15 sectors are available for allocation between historical logs 1, 2, and 3. \n The sum of all Historical Logs may be less than 15. \n If this value is 0, the log is disabled."
        self.sectorBox.setToolTip(self.sectorToolTip)

        self.logSettingsLayout.setWidget(2, QFormLayout.FieldRole,
                                         self.sectorBox)

        self.plvHorizontalLayout.addWidget(self.logSettingsWidget)

        self.centerLine = QFrame(self.horizontalLayoutWidget)
        self.centerLine.setMinimumSize(QSize(10, 0))
        self.centerLine.setFrameShape(QFrame.VLine)
        self.centerLine.setFrameShadow(QFrame.Sunken)

        self.plvHorizontalLayout.addWidget(self.centerLine)

        self.meterValsWidget = QWidget(self.horizontalLayoutWidget)

        self.verticalLayoutWidget = QWidget(self.meterValsWidget)
        self.verticalLayoutWidget.setGeometry(QRect(9, 10, 361, 475))

        self.meterValsLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.meterValsLayout.setContentsMargins(0, 0, 0, 0)

        self.meterValsHeader = QLabel(self.verticalLayoutWidget)
        self.meterValsHeader.setText("Meter Values to Log: ")

        self.meterValsLayout.addWidget(self.meterValsHeader)
        self.meterValsList = QListWidget(self.verticalLayoutWidget)
        for value in measured_values:
            item = QListWidgetItem(value)
            item.setCheckState(0)
            self.meterValsList.addItem(item)

        self.meterValsLayout.addWidget(self.meterValsList)
        self.plvHorizontalLayout.addWidget(self.meterValsWidget)

    def submit_settings(self):
        # go through the list of checkboxes, if an item is checked we
        # add the text to the self.selectedValues list
        for i in range(0, self.meterValsList.count()):
            if(self.meterValsList.item(i).checkState()):
                item = self.meterValsList.item(i)
                self.selectedValues.append(str(item.text()))
        # from the list of selected Values, extract each ones list of registers
        # (they're a list b/c some values span multiple registers)
        # and append it to the list of selected Registers
        for val in self.selectedValues:
            reg_list = values_register_list.get(val)
            for reg in reg_list:
                self.selectedRegisters.append(reg)
        # write each of the selected registers to a position in the reg list
        # extra values are filled with 0xFF to denote its not being used
        self.interval = self.interval_code(str(self.intervalBox.currentText()))
        self.sectors = int(str(self.sectorBox.currentText()))
        client.program_log(self.parent.client, self.parent.log_num,
                           self.selectedRegisters, self.interval,
                           self.sectors)
        # cleanup stuff, return to initial View
        self.clear_settings()

    def clear_settings(self):
        for i in range(0, self.meterValsList.count()):
            self.meterValsList.item(i).setCheckState(0)
        self.selectedValues = []
        self.selectedRegisters = []
        self.parent.parent.connected = False
        self.parent.parent.disconnect()

    def interval_code(self, interval):
        if interval is "1 minute":
            return 0x01
        elif interval is "3 minutes":
            return 0x02
        elif interval is "5 minutes":
            return 0x04
        elif interval is "10 minutes":
            return 0x08
        elif interval is "15 minutes":
            return 0x10
        elif interval is "30 minutes":
            return 0x20
        elif interval is "60 minutes":
            return 0x40
        else:
            return 0x80  # EOI pulse
