"""
Include customized widgets used in HandyView.
"""

from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtWidgets import QFrame, QLabel


class ColorLabel(QLabel):
    """Show color in QLabel.

    Args:
        text (str): Shown text. Default: None.
        color (tuple): RGBA value. Default: None.
    """

    def __init__(self, text=None, color=None, parent=None):
        super(ColorLabel, self).__init__(parent)
        self.parent = parent
        # self.setStyleSheet('border: 2px solid gray;')
        self.pixmap = QPixmap(40, 20)
        self.setPixmap(self.pixmap)
        if text is not None:
            self.setText(text)
        if color is not None:
            self.fill(color)

    def fill(self, color):
        if isinstance(color, (list, tuple)):
            self.pixmap.fill(QColor(*color))
        else:
            self.pixmap.fill(color)
        self.setPixmap(self.pixmap)


class HLine(QFrame):
    """Horizontal separation line used in dock window."""

    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class HVLable(QLabel):
    """QLabel with customized initializations."""

    def __init__(self,
                 text,
                 parent,
                 color='black',
                 font='Times',
                 font_size=12):
        super(HVLable, self).__init__(text, parent)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.setStyleSheet('QLabel {color : ' + color + ';}')
        self.setFont(QFont(font, font_size))
