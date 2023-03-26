from PySide6.QtWidgets import QProgressBar

class ProgressBar(QProgressBar):
    def __init__(self):
        super().__init__()
        # self.setProperties()

    def setProperties(self):
        self.setGeometry(200, 100, 200, 30)
        self.setStyleSheet("""QProgressBar
                                    {
                                    border: solid grey;
                                    border-radius: 15px;
                                     color: black;
                                    }
                                    QProgressBar::chunk
                                    {background-color: #05B8CC;
                                    border-radius :15px;
                                    }""")
        
    def setProgress(self, _value):
        self.setValue(_value)

    def getValue(self):
        return self.value()