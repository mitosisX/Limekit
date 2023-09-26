from PySide6.QtWidgets import QDockWidget, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


class Docker(QDockWidget, EnginePart):
    name = "Dock"

    def __init__(self, title="Dock", parent=None):
        super().__init__(parent=parent)

        self.widget = QWidget()
        self.setWidget(self.widget)

    """
    we want PyQt to save and restore the dock widget’s
    size and position, and since there could be any number of dock widgets, PyQt
    uses the object name to distinguish between them
    """

    def setName(self, name):
        self.setObjectName(name)

    """
    Represents areas permitted areas for docking; more like magnetic areas
    could have been setAreas but I thought the "magnetic" name madeit look
    cool instead.
    
    Coz whenever one tries to dock some widget onto some areas, the allowed areas
    respond with a strong magnetic pull to signal the use that the particular area
    is ready to dock.
    
        Available positional enums
    NoDockWidgetArea
    LeftDockWidgetArea
    RightDockWidgetArea
    TopDockWidgetArea
    BottomDockWidgetArea
    AllDockWidgetAreas
    DockWidgetArea_Mask
    
    Set the allowed areas for a QDockWidget based on a list of areas.
        Multiple strings can be passed to set the allowed areas accordingly.
        
        Parameters:
            areas (list): list indicating the sides where the QDockWidget is allowed to be docked.
                        Valid strings are "top", "bottom", "left", and "right".
    """

    def setMagneticAreas(self, areas):
        allowed_areas = Qt.NoDockWidgetArea

        for area in list(areas.values()):
            if area == "top":
                allowed_areas |= Qt.TopDockWidgetArea
            elif area == "bottom":
                allowed_areas |= Qt.BottomDockWidgetArea
            elif area == "left":
                allowed_areas |= Qt.LeftDockWidgetArea
            elif area == "right":
                allowed_areas |= Qt.RightDockWidgetArea

        self.setAllowedAreas(allowed_areas)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setIcon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def setSize(self, width, height):
        self.resize(width, height)

    def setChild(self, child):
        self.setWidget(child)
