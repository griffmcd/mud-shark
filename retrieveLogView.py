from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QHeaderView, QWidget)

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
        self.initUI()

    def initUI(self):
        self.logTableWidget = LogTableWidget(self)
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.logTableWidget)
        self.setLayout(self.vlayout)
