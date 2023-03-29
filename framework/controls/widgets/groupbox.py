from PySide6.QtWidgets import QGroupBox

"""
To set the title
g.setTitle("&User information");

Only a layout can be used to add widgets using setLayout method
setCheckable(bool) displays a checkbox on the title bar

This property holds whether the group box is painted flat or has a frame. (Qt documentation)
bool	isFlat() const
void	setFlat(bool flat)
"""
class GroupBox(QGroupBox):
    def __init__(self, title = "GroupBox"):
        super().__init__(title)