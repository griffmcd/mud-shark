from PyQt5.QtWidgets import (QComboBox, QFormLayout, QGridLayout, QLabel,
                             QListWidget, QListWidgetItem, QHBoxLayout,
                             QPushButton, QVBoxLayout, QWidget)


class MeterValuesListWidget(QListWidget):
    def __init__(self, parent):
        super(MeterValuesListWidget, self).__init__()
        self.parent = parent
        self.measured_values = ["Instant Voltage L-N", "Max Voltage L-N",
                                "Min Voltage L-N",

                                "Instant Voltage L-L", "Max Voltage L-L",
                                "Min Voltage L-L",

                                "Instant Current per Phase",
                                "Average Current per Phase",

                                "Max Current per Phase",
                                "Min Current per Phase",

                                "Instant Current Neutral",
                                "Average Current Neutral",
                                "Max Current Neutral", "Min Current Neutral",

                                "Instant Total Watts", "Average Total Watts",
                                "Max Total Watts", "Min Total Watts",

                                "Instant A Watts", "Average A Watts",
                                "Max A Watts", "Min A Watts",

                                "Instant B Watts", "Average B Watts",
                                "Max B Watts", "Min B Watts",

                                "Instant C Watts", "Average C Watts",
                                "Max C Watts", "Min C Watts",

                                "Instant Total Var", "Average Total Var",
                                "Max Total Var", "Min Total Var",

                                "Instant A Var", "Average A Var", "Max A Var",
                                "Min A Var",

                                "Instant B Var", "Average B Var", "Max B Var",
                                "Min B Var",

                                "Instant C Var", "Average C Var", "Max C Var",
                                "Min C Var",

                                "Instant Total VA", "Average Total VA",
                                "Max Total VA", "Min Total VA",

                                "Instant A VA", "Average A VA", "Max A VA",
                                "Min A VA",

                                "Instant B VA", "Average B VA", "Max B VA",
                                "Min B VA",

                                "Instant C VA", "Average C VA", "Max C VA",
                                "Min C VA",

                                "Instant Total PF", "Average Total PF",
                                "Max Total PF", "Min Total PF",

                                "Instant A PF", "Average A PF", "Max A PF",
                                "Min A PF",

                                "Instant B PF", "Average B PF", "Max B PF",
                                "Min B PF",

                                "Instant C PF", "Average C PF", "Max C PF",
                                "Min C PF",

                                "Total Watt Hours", "A Watt Hours",
                                "B Watt Hours", "C Watt Hours",

                                "Total -Wh", "A -Wh", "B -Wh", "C -Wh",

                                "Wh Net",

                                "Total +VARh", "A +VARh", "B +VARh", "C +VARh",

                                "Total -VARh", "A -VARh", "B -VARh", "C -VARh",

                                "Total VARh Net", "A VARh Net", "B VARh Net",
                                "C VARh Net",

                                "Total VAh", "A VAh", "B VAh", "C VAh",

                                "Instant Frequency", "Max Frequency",
                                "Min Frequency",

                                "Harmonics to the 40th Order",
                                "Instant THD", "Max THD", "Min THD",
                                "Voltage Angles", "Current Angles",
                                "% of Load Bar"]
        self.initUI()

    def initUI(self):
        for value in self.measured_values:
            self.addItem(QListWidgetItem(value, self).setCheckState(0))


class ProgramLogWidget(QWidget):
    def __init__(self, parent):
        super(ProgramLogWidget, self).__init__()
        self.parent = parent
        self.intervals = ["1 minute", "3 minutes", "5 minutes", "10 minutes",
                          "15 minutes", "30 minutes", "60 minutes",
                          "End of Interval Pulse"]
        self.initUI()

    def initUI(self):
        # Log Input Widget (0,0)
        self.inputFormLabel = QLabel("Log Settings: ")
        self.inputFormWidget = QWidget()
        self.intervalLabel = QLabel("Interval: ")
        self.intervalBox = QComboBox()
        for interval in self.intervals:
            self.intervalBox.addItem(interval)
        self.inputFormLayout = QFormLayout()
        self.sectorLabel = QLabel("Sectors: ")
        self.sectorBox = QComboBox()
        for i in range(0, 16):
            self.sectorBox.addItem(str(i))
        self.inputFormLayout = QFormLayout()
        self.inputFormLayout.addRow(self.inputFormLabel)
        self.inputFormLayout.addRow(self.intervalLabel, self.intervalBox)
        self.inputFormLayout.addRow(self.sectorLabel, self.sectorBox)
        self.inputFormWidget.setLayout(self.inputFormLayout)
        self.inputFormLayout.setSpacing(10)

        # List Widget (0, 1)
        self.meterValsWidget = QWidget()
        self.meterValLabel = QLabel("Values to Log (Max 64 per meter): ")
        self.meterValuesListWidget = MeterValuesListWidget(self)
        self.meterValsLayout = QVBoxLayout()
        self.meterValsLayout.addWidget(self.meterValLabel)
        self.meterValsLayout.addWidget(self.meterValuesListWidget)
        self.meterValsWidget.setLayout(self.meterValsLayout)
        self.meterValsWidget.setFixedSize(400, 600)

        # button bar widget (2,1)
        self.buttonBarWidget = QWidget()
        self.submitButton = QPushButton("Submit")
        self.submitButton.clicked.connect(self.submit_button_pushed)
        self.clearButton = QPushButton("Clear")
        self.clearButton.clicked.connect(self.clear_button_pushed)
        self.buttonBarLayout = QHBoxLayout()
        self.buttonBarLayout.addWidget(self.submitButton)
        self.buttonBarLayout.addWidget(self.clearButton)
        self.buttonBarWidget.setLayout(self.buttonBarLayout)

        # mem usage info widget(1,0)
        self.memUsageLabel = QLabel("This is where mem usage info will go")
        self.memUsageLayout = QVBoxLayout()
        self.memUsageLayout.addWidget(self.memUsageLabel)
        self.memUsageWidget = QWidget()
        self.memUsageWidget.setLayout(self.memUsageLayout)
        for i in range(0, 10):
            self.memUsageLayout.addWidget(QLabel(str(i)))
        self.memUsageWidget.setFixedHeight(500)

        # spacer
        self.spacerWidget = QWidget()
        self.spacerLayout = QHBoxLayout()
        self.spacerWidget.setLayout(QHBoxLayout())
        self.spacerWidget.setFixedWidth(400)

        # grid
        self.grid = QGridLayout()
        self.grid.addWidget(self.inputFormWidget, 0, 0)
        self.grid.addWidget(self.meterValsWidget, 0, 1, 3, 1)
        self.grid.addWidget(self.memUsageWidget, 1, 0, 1, 2)
        self.grid.addWidget(self.spacerWidget, 3, 0)
        self.grid.addWidget(self.buttonBarWidget, 3, 1)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.grid, 1)
        self.mainLayout.addStretch(0)
        self.setLayout(self.mainLayout)

    def submit_button_pushed(self):
        print("Pushed submit")

    def clear_button_pushed(self):
        print("Clear button pushed")
