from framework.controls.dialogs.popups.about_popup import AboutPopup
from framework.controls.dialogs.popups.about_popup import AboutPopup
from framework.controls.dialogs.popups.about_popup import AboutPopup
from framework.controls.dialogs.popups.about_popup import AboutPopup
from framework.controls.dialogs.popups.about_popup import AboutPopup

"""
a swiss army knife of all required utility functionalities
"""
class MirandaApp:
    def read_file(file):
        with open(file, 'r') as file:
            return file.read()
        
    def write_file(file, content):
        with open(file, 'w') as file:
            file.write(content)
        
    def append_file(file, content):
        with open(file, 'a') as file:
            file.write(content)
            
    def createFile(file_):
        with open(file_, 'w') as file: pass