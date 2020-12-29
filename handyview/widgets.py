"""
Include customized widgets used in HandyView.
"""

from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel, QMessageBox,
                             QPushButton, QVBoxLayout)


def show_msg(icon='Information', title='Title', msg='Message'):
    """
    QMessageBox::NoIcon
    QMessageBox::Question
    QMessageBox::Information
    QMessageBox::Warning
    QMessageBox::Critical
    """
    if icon == 'NoIcon':
        icon = QMessageBox.NoIcon
    elif icon == 'Question':
        icon = QMessageBox.Question
    elif icon == 'Information':
        icon = QMessageBox.Information
    elif icon == 'Warning':
        icon = QMessageBox.warning
    elif icon == 'Critical':
        icon = QMessageBox.Critical

    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(msg)
    msg.exec_()


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


class MessageDialog(QDialog):
    """Message dialog for showing both English and Chinese text."""

    def __init__(self, parent, text_en, text_cn):
        super(MessageDialog, self).__init__(parent)
        self.text_en = text_en
        self.text_cn = text_cn

        # buttons
        self.btn_close = QPushButton('Close', self)
        self.btn_close.clicked.connect(self.button_press)
        self.btn_cn = QPushButton('简体中文', self)
        self.btn_cn.clicked.connect(self.button_press)
        self.btn_en = QPushButton('English', self)
        self.btn_en.clicked.connect(self.button_press)
        self.layout_btn = QHBoxLayout()
        self.layout_btn.setSpacing(10)
        self.layout_btn.addWidget(self.btn_cn)
        self.layout_btn.addWidget(self.btn_en)
        self.layout_btn.addWidget(self.btn_close)

        self.text_label = HVLable(text_en, self, 'black', 'Times', 12)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.addWidget(self.text_label)
        self.layout.addLayout(self.layout_btn)
        self.setLayout(self.layout)

    def button_press(self):
        if self.sender() == self.btn_cn:
            self.setText(self.text_cn)
        elif self.sender() == self.btn_en:
            self.setText(self.text_en)
        else:
            self.close()

    def setText(self, text):
        self.text_label.setText(text)
