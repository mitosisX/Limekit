from PySide6.QtWidgets import QApplication

# import PySide6.QtWidgets
# print(PySide6.QtWidgets.QStyleFactory.keys())

import qdarkstyle  # noqa: E402
from qdarkstyle.dark.palette import DarkPalette  # noqa: E402
from qdarkstyle.light.palette import LightPalette  # noqa: E402

# app.setStyle('Windows')
# ['windowsvista', 'Windows', 'Fusion']


class App(object):
    app = QApplication([])
    
        
    file = open(r"D:\Projects\Limekit\framework\controls\widgets\theme.qss") 
    content = file.read()
    file.close()
    
    app.setStyle(content)

    # Tis prevents the program from closing once all windows
    # have been closed; the programs runs in the background
    # app.setQuitOnLastWindowClosed(False)

    @staticmethod
    def execute():
        return App.app.exec_()