import os
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLineEdit, QPushButton,
                             QWidget)

from handyview.view_scene import HVScene, HVView
from handyview.widgets import ColorLabel, HVLable, show_msg


class Canvas(QWidget):
    """The main canvas showing a single view."""

    def __init__(self, parent, db):
        super(Canvas, self).__init__()
        self.parent = parent
        self.db = db

        # initialize widgets and layout
        self.init_widgets_layout()
        self.qview_bg_color = 'white'
        self.show_image(init=True)

    def init_widgets_layout(self):
        # QGraphicsView - QGraphicsScene - QPixmap
        self.qscene = HVScene(self)
        self.qview = HVView(self.qscene, self)

        # name label showing image index and image path
        self.name_label = HVLable('', self, 'green', 'Times', 15)
        # goto edit and botton for indexing
        self.goto_edit = QLineEdit()
        self.goto_edit.setPlaceholderText('Index. Default: 1')
        goto_btn = QPushButton('GO', self)
        goto_btn.clicked.connect(self.goto_button_clicked)

        # info label showing image shape, size and color type
        self.info_label = HVLable('', self, 'blue', 'Times', 12)
        # zoom label showing zoom ratio
        self.zoom_label = HVLable('1.00', self, 'green', 'Times', 12)
        # mouse position and mouse rgb value
        mouse_pos_text = ('Cursor position:\n (ignore zoom)\n'
                          ' Height(y): 0.0\n Width(x):  0.0')
        self.mouse_pos_label = HVLable(mouse_pos_text, self, 'black', 'Times',
                                       12)
        self.mouse_rgb_label = HVLable(' (255, 255, 255, 255)', self, 'black',
                                       'Times', 12)
        # pixel color at the mouse position
        self.mouse_color_title = HVLable('RGBA:', self, 'black', 'Times', 12)
        self.mouse_color_label = ColorLabel(color=(255, 255, 255))

        # selection rectangle position and length
        selection_pos_text = ('Rect Pos: (H, W)\n Start: 0, 0\n'
                              ' End  : 0, 0\n Len  : 0, 0')
        self.selection_pos_label = HVLable(selection_pos_text, self, 'black',
                                           'Times', 12)

        # include and exclude names
        self.include_names_label = HVLable('', self, 'black', 'Times', 12)
        self.exclude_names_label = HVLable('', self, 'black', 'Times', 12)
        # comparison folders
        self.comparison_label = HVLable('', self, 'red', 'Times', 12)

        # ---------
        # layouts
        # ---------
        main_layout = QGridLayout(self)
        # QGridLayout:
        # int row, int column, int rowSpan, int columnSpan
        main_layout.addWidget(self.name_label, 0, 0, 1, 50)

        name_grid = QGridLayout()
        name_grid.addWidget(self.goto_edit, 0, 0, 1, 1)
        name_grid.addWidget(goto_btn, 0, 1, 1, 1)
        main_layout.addLayout(name_grid, 1, 0, 1, 10)

        main_layout.addWidget(self.qview, 0, 0, -1, 50)
        # blank label for layout
        blank_label = HVLable('', self, 'black', 'Times', 12)
        main_layout.addWidget(blank_label, 61, 0, 1, 1)

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.key() == QtCore.Qt.Key_F9:
            self.toggle_bg_color()
        elif event.key() == QtCore.Qt.Key_R:
            self.qview.set_zoom(1)
        elif event.key() == QtCore.Qt.Key_C:
            self.compare_folders(1)
        elif event.key() == QtCore.Qt.Key_V:
            self.compare_folders(-1)
        elif event.key() == QtCore.Qt.Key_Space:
            if modifiers == QtCore.Qt.ShiftModifier:
                self.dir_browse(10)
            else:
                self.dir_browse(1)
        elif event.key() == QtCore.Qt.Key_Backspace:
            if modifiers == QtCore.Qt.ShiftModifier:
                self.dir_browse(-10)
            else:
                self.dir_browse(-1)
        elif event.key() == QtCore.Qt.Key_Right:
            if modifiers == QtCore.Qt.ShiftModifier:
                self.dir_browse(10)
            else:
                self.dir_browse(1)
        elif event.key() == QtCore.Qt.Key_Left:
            if modifiers == QtCore.Qt.ShiftModifier:
                self.dir_browse(-10)
            else:
                self.dir_browse(-1)
        elif event.key() == QtCore.Qt.Key_Up:
            self.qview.zoom_in()
        elif event.key() == QtCore.Qt.Key_Down:
            self.qview.zoom_out()

    def goto_button_clicked(self):
        goto_str = self.goto_edit.text()
        if goto_str == '':
            self.db.pidx = 0
        elif goto_str.isdigit():
            self.db.pidx = int(goto_str) - 1
        else:
            return
        self.show_image()

    def update_cmp_path_list(self, cmp_path):
        is_same_len, img_len_list = self.db.update_cmp_path_list(cmp_path)

        show_str = 'Number for each folder:\n\t' + '\n\t'.join(
            map(str, img_len_list))
        self.comparison_label.setText(show_str)
        if is_same_len is False:
            msg = ('Comparison folders have differnet number of images.\n'
                   f'{show_str}')
            show_msg('Warning', 'Warning!', msg)

    def compare_folders(self, step):
        self.db.folder_browse(step)
        self.show_image()

        # when in main folder (1st folder), show red color
        if self.db.fidx == 0:
            self.comparison_label.setStyleSheet('QLabel {color : red;}')
        else:
            self.comparison_label.setStyleSheet('QLabel {color : black;}')

    def show_image(self, init=False):
        self.qscene.clear()
        img_path = self.db.get_path()
        self.qimg = QImage(img_path)
        self.qpixmap = QPixmap.fromImage(self.qimg)
        self.qscene.addPixmap(self.qpixmap)
        self.width, self.height = self.db.get_shape()
        # put image always in the center of a QGraphicsView
        self.qscene.setSceneRect(0, 0, self.width, self.height)
        # show image path in the statusbar
        self.parent.set_statusbar(f'{img_path}')

        # update information panel
        basename = os.path.basename(img_path)
        self.name_label.setText(f'[{self.db.pidx + 1:d} / '
                                f'{self.db.get_path_len():d}] '
                                f'{basename}')
        self.info_label.setText(
            'Info: \n'
            f' Height: {self.height:d}\n Width:  {self.width:d}\n'
            f' Size: {self.db.get_file_size()}\n'
            f' Type: {self.db.get_color_type()}')

        if init:
            if self.width < 500:
                self.qview.set_zoom(500 // self.height)
            else:
                self.qview.set_zoom(1)
        self.qview.set_transform()

    def dir_browse(self, step):
        self.db.path_browse(step)
        self.show_image()

    def toggle_bg_color(self):
        """Toggle background color."""

        if self.qview_bg_color == 'white':
            self.qview_bg_color = 'lightgray'
            self.qscene.setBackgroundBrush(QColor(211, 211, 211))
        else:
            self.qview_bg_color = 'white'
            self.qscene.setBackgroundBrush(QtCore.Qt.white)
