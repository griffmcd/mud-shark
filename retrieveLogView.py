from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QHeaderView, QWidget, QSizePolicy, QFormLayout,
                             QLabel, QGridLayout, QPushButton, QSpacerItem,
                             QFrame, QTableView, QHBoxLayout)

from PyQt5 import QtCore


class LogTableWidget(QTableWidget):
    def __init__(self, parent):
        super(LogTableWidget, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.testHeaders = ["Average Total Watts", "Average Total Var",
                            "Total Watt Hours", "Wh Net"]
        self.testTimestamps = ["Monday", "Tuesday", "Wednesday", "Thursday",
                               "Friday"]
        self.setRowCount(len(self.testTimestamps))
        self.setColumnCount(len(self.testHeaders))
        self.setHorizontalHeaderLabels(self.testHeaders)
        self.setVerticalHeaderLabels(self.testTimestamps)
        for i in range(0, len(self.testTimestamps)):
            for j in range(0, len(self.testHeaders)):
                self.setItem(i, j, self.cell(str(i+j)))
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)

    def cell(self, var=""):
        item = QTableWidgetItem()
        item.setText(var)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        return item


class RetrieveLogWidget(QWidget):
    def __init__(self, parent):
        super(RetrieveLogWidget, self).__init__()
        self.parent = parent
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)
        self.title = "Retrieve Log View"
        self.setWindowTitle(self.title)
        self.initUI()

    def initUI(self):
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10,  10, 781, 581))
        self.rlvVerticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.rlvVerticalLayout.setContentsMargins(0, 0, 0, 0)

        self.topPane = QWidget(self.verticalLayoutWidget)

        self.horizontalLayoutWidget = QWidget(self.topPane)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 761, 271))

        self.topPaneHLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.topPaneHLayout.setContentsMargins(0, 0, 0, 0)

        self.topInfoPaneWid = QWidget(self.horizontalLayoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred,
                                 QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.topInfoPaneWid.sizePolicy().hasHeightForWidth())
        self.topInfoPaneWid.setSizePolicy(sizePolicy)

        self.formLayoutWidget = QWidget(self.topInfoPaneWid)
        self.formLayoutWidget.setGeometry(QtCore.QRect(0, 0, 371, 271))

        self.logInfoFormLayout = QFormLayout(self.formLayoutWidget)
        self.logInfoFormLayout.setContentsMargins(0, 0, 0, 0)
        self.logInfoFormLayout.setVerticalSpacing(20)

        self.logNameLabel = QLabel(self.formLayoutWidget)
        self.logNameLabel.setText("Log Name: ")
        self.logInfoFormLayout.setWidget(0, QFormLayout.LabelRole,
                                         self.logNameLabel)

        self.logNameBox = QLabel(self.formLayoutWidget)
        self.logNameBox.setText(self.parent.log_name)
        self.logInfoFormLayout.setWidget(0, QFormLayout.FieldRole,
                                         self.logNameBox)

        self.recordSizeLabel = QLabel(self.formLayoutWidget)
        self.recordSizeLabel.setText("Record Size: ")
        self.logInfoFormLayout.setWidget(1, QFormLayout.LabelRole,
                                         self.recordSizeLabel)

        self.recordSizeBox = QLabel(self.formLayoutWidget)
        self.recordSizeBox.setText(str(self.parent.parent.recSize))
        self.logInfoFormLayout.setWidget(1, QFormLayout.FieldRole,
                                         self.recordSizeBox)

        self.recsPerWindowLabel = QLabel(self.formLayoutWidget)
        self.recsPerWindowLabel.setText("Records per Window: ")
        self.logInfoFormLayout.setWidget(2, QFormLayout.LabelRole,
                                         self.recsPerWindowLabel)
        self.recsPerWindowBox = QLabel(self.formLayoutWidget)
        self.recsPerWindowBox.setText(str(self.parent.parent.rpw))
        self.logInfoFormLayout.setWidget(2, QFormLayout.FieldRole,
                                         self.recsPerWindowBox)

        self.numRecordsLabel = QLabel(self.formLayoutWidget)
        self.numRecordsLabel.setText("Number of Records: ")
        self.logInfoFormLayout.setWidget(3, QFormLayout.LabelRole,
                                         self.numRecordsLabel)
        self.numRecordsBox = QLabel(self.formLayoutWidget)
        self.numRecordsBox.setText(str(self.parent.parent.numRecs))
        self.logInfoFormLayout.setWidget(3, QFormLayout.FieldRole,
                                         self.numRecordsBox)

        """
        self.fstTimestampLabel = QLabel(self.formLayoutWidget)
        self.fstTimestampLabel.setText("First Timestamp: ")
        self.logInfoFormLayout.setWidget(4, QFormLayout.LabelRole,
                                         self.fstTimestampLabel)
        self.fstTimestampBox = QLabel(self.formLayoutWidget)
        self.fstTimestampBox.setText(self.fstTimestamp)
        self.logInfoFormLayout.setWidget(4, QFormLayout.FieldRole,
                                         self.fstTimestampBox)

        self.lastTimestampLabel = QLabel(self.formLayoutWidget)
        self.lastTimestampLabel.setText("Last Timestamp: ")
        self.logInfoFormLayout.setWidget(5, QFormLayout.LabelRole,
                                         self.lastTimestampLabel)
        self.lastTimestampBox = QLabel(self.formLayoutWidget)
        self.lastTimestampBox.setText("last timestamp")
        self.logInfoFormLayout.setWidget(5, QFormLayout.FieldRole,
                                         self.lastTimestampBox)

        """
        self.topPaneHLayout.addWidget(self.topInfoPaneWid)

        self.topVDivider = QFrame(self.horizontalLayoutWidget)
        self.topVDivider.setFrameShape(QFrame.VLine)
        self.topVDivider.setFrameShadow(QFrame.Sunken)

        self.topPaneHLayout.addWidget(self.topVDivider)

        self.graphLogWidget = QWidget(self.horizontalLayoutWidget)
        self.topHorizontalLayoutWidget = QWidget(self.graphLogWidget)
        self.topHorizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 371, 271))

        self.graphsLayout = QHBoxLayout(self.topHorizontalLayoutWidget)
        self.graphsLayout.setContentsMargins(0, 0, 0, 0)

        self.graphButtonsWid = QWidget(self.topHorizontalLayoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.graphButtonsWid.sizePolicy().hasHeightForWidth())
        self.graphButtonsWid.setSizePolicy(sizePolicy)
        self.graphButtonsWid.setMinimumSize(250, 0)

        self.gridLayoutWidget = QWidget(self.graphButtonsWid)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 254, 271))

        self.graphButtonsGrid = QGridLayout(self.gridLayoutWidget)
        self.graphButtonsGrid.setContentsMargins(0, 0, 0, 0)

        self.graphButtons = []

        i = 0
        for x in range(0, 3):
            for y in range(0, 3):
                button = QPushButton(self.gridLayoutWidget)
                button.setText("Graph " + str(i))
                self.graphButtonsGrid.addWidget(button, x, y, 1, 1)
                self.graphButtons.append(button)
                i += 1

        self.graphsLayout.addWidget(self.graphButtonsWid)
        self.graphsVLine = QFrame(self.topHorizontalLayoutWidget)
        self.graphsVLine.setFrameShape(QFrame.VLine)
        self.graphsVLine.setFrameShadow(QFrame.Sunken)
        self.graphsLayout.addWidget(self.graphsVLine)

        self.graphsSubmitWidget = QWidget(self.topHorizontalLayoutWidget)
        self.graphsSubmitLayoutWidget = QWidget(self.graphsSubmitWidget)
        self.graphsSubmitLayoutWidget.setGeometry(QtCore.QRect(0, 0, 101, 271))
        self.graphsSubmitLayout = QVBoxLayout(self.graphsSubmitLayoutWidget)
        self.graphsSubmitLayout.setContentsMargins(0, 0, 0, 0)
        self.submitButton = QPushButton(self.graphsSubmitLayoutWidget)
        self.submitButton.setText("Graph")
        self.graphsSubmitLayout.addWidget(self.submitButton)
        self.exitButton = QPushButton(self.graphsSubmitLayoutWidget)
        self.exitButton.setText("Close ")
        self.graphsSubmitLayout.addWidget(self.exitButton)
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum,
                                 QSizePolicy.Expanding)
        self.graphsSubmitLayout.addItem(spacerItem)
        self.graphsLayout.addWidget(self.graphsSubmitWidget)
        self.topPaneHLayout.addWidget(self.graphLogWidget)
        self.rlvVerticalLayout.addWidget(self.topPane)
        self.horzDivider = QFrame(self.verticalLayoutWidget)
        self.horzDivider.setFrameShape(QFrame.HLine)
        self.horzDivider.setFrameShadow(QFrame.Sunken)

        self.rlvVerticalLayout.addWidget(self.horzDivider)

        self.logTableWidget = LogTableWidget(self.verticalLayoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.logTableWidget.sizePolicy().hasHeightForWidth())
        self.logTableWidget.setSizePolicy(sizePolicy)
        self.rlvVerticalLayout.addWidget(self.logTableWidget)
