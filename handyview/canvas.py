import glob
import os
import sys
from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLineEdit, QPushButton,
                             QWidget)
from utils import FORMATS, get_img_list, sizeof_fmt
from view_scene import HVScene, HVView
from widgets import ColorLabel, HVLable, show_msg

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    CURRENT_PATH = sys._MEIPASS
else:
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class Canvas(QWidget):
    """The main canvas showing a single view."""

    def __init__(self, parent):
        super(Canvas, self).__init__()
        self.parent = parent
        try:
            self.key = sys.argv[1]
        except IndexError:
            # show the icon image
            self.key = os.path.join(CURRENT_PATH, 'icon.png')

        if os.path.isdir(self.key):
            self.key = sorted(glob.glob(os.path.join(self.key, '*')))[0]

        # initialize widgets and layout
        self.init_widgets_layout()

        self.include_names = None
        self.exclude_names = None
        self.qview_bg_color = 'white'
        # list of image list
        # the first list is the main list, the others are for comparisons
        self.img_list = [[]]
        self.img_list_idx = 0

        self.get_main_img_list()
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
            self.dirpos = 0
        elif goto_str.isdigit():
            self.dirpos = int(goto_str) - 1
        else:
            return
        self.key = self.img_list[self.img_list_idx][self.dirpos]
        self.show_image()

    def get_main_img_list(self):
        # if key is a folder, get the first image path
        if os.path.isdir(self.key):
            self.key = sorted(glob.glob(os.path.join(self.key, '*')))[0]

        # fix the key pattern passed from windows system when double click
        self.key = self.key.replace('\\', '/')

        if self.key.endswith(FORMATS):
            # get image list
            self.path, self.img_name = os.path.split(self.key)
            self.img_list[self.img_list_idx] = get_img_list(
                self.path, self.include_names, self.exclude_names)
            # get current position
            try:
                self.dirpos = self.img_list[self.img_list_idx].index(self.key)
            except ValueError:
                # self.key may not in self.img_list after refreshing
                self.dirpos = 0
            # save open file history
            self.save_open_history()
        else:
            show_msg('Critical', 'Critical', f'Wrong key! {self.key}')

    def update_cmp_img_list(self, cmp_path):
        path, _ = os.path.split(cmp_path)
        self.img_list.append(
            get_img_list(path, self.include_names, self.exclude_names))
        # all the image list should have the same length
        all_same_len = True
        lens_img_list = [len(self.img_list[0])]
        for img_list in self.img_list[1:]:
            lens_img_list.append(len(img_list))
            if len(img_list) != lens_img_list[0]:
                all_same_len = False

        show_str = 'Number for each folder:\n\t' + '\n\t'.join(
            map(str, lens_img_list))
        self.comparison_label.setText(show_str)
        if all_same_len is False:
            msg = ('Comparison folders have differnet number of images.\n'
                   f'{show_str}')
            show_msg('Warning', 'Warning!', msg)

    def compare_folders(self, direction):
        if len(self.img_list) > 1:
            self.img_list_idx += direction
            if self.img_list_idx > (len(self.img_list) - 1):
                self.img_list_idx = 0
            elif self.img_list_idx < 0:
                self.img_list_idx = (len(self.img_list) - 1)
            try:
                self.key = self.img_list[self.img_list_idx][self.dirpos]
            except IndexError:
                self.dirpos = len(self.img_list[self.img_list_idx]) - 1
                self.key = self.img_list[self.img_list_idx][self.dirpos]
            self.show_image()
            # when in main folder (1st folder), show red color
            if self.img_list_idx == 0:
                self.comparison_label.setStyleSheet('QLabel {color : red;}')
            else:
                self.comparison_label.setStyleSheet('QLabel {color : black;}')

    def save_open_history(self):
        try:
            with open(os.path.join(CURRENT_PATH, 'history.txt'), 'r') as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
                if len(lines) == 5:
                    del lines[-1]
        except Exception:
            lines = []
        # add the new record to the first line
        if self.key not in ['icon.png', './icon.png'] and (self.key
                                                           not in lines):
            lines.insert(0, self.key)
        with open(os.path.join(CURRENT_PATH, 'history.txt'), 'w') as f:
            for line in lines:
                f.write(f'{line}\n')

    def show_image(self, init=False):
        self.qscene.clear()
        self.qimg = QImage(self.key)
        self.qpixmap = QPixmap.fromImage(self.qimg)
        self.qscene.addPixmap(self.qpixmap)
        self.imgw, self.imgh = self.qpixmap.width(), self.qpixmap.height()
        # put image always in the center of a QGraphicsView
        self.qscene.setSceneRect(0, 0, self.imgw, self.imgh)
        # show image path in the statusbar
        self.parent.set_statusbar(f'{self.key}')

        try:
            with Image.open(self.key) as lazy_img:
                self.color_type = lazy_img.mode
        except FileNotFoundError:
            show_msg('Critical', 'Critical', f'Cannot open {self.key}')

        # update information panel
        self.path, self.img_name = os.path.split(self.key)
        self.file_size = sizeof_fmt(os.path.getsize(self.key))
        self.name_label.setText(f'[{self.dirpos + 1:d} / '
                                f'{len(self.img_list[self.img_list_idx]):d}] '
                                f'{self.img_name}')
        self.info_label.setText(
            'Info: \n'
            f' Height: {self.imgh:d}\n Width:  {self.imgw:d}\n'
            f' Size: {self.file_size}\n Type: {self.color_type}')

        if init:
            if self.imgw < 500:
                self.qview.set_zoom(500 // self.imgw)
            else:
                self.qview.set_zoom(1)
        self.qview.set_transform()

    def dir_browse(self, direction):
        if len(self.img_list[self.img_list_idx]) > 1:
            self.dirpos += direction
            if self.dirpos > (len(self.img_list[self.img_list_idx]) - 1):
                self.dirpos = 0
            elif self.dirpos < 0:
                self.dirpos = (len(self.img_list[self.img_list_idx]) - 1)
            self.key = self.img_list[self.img_list_idx][self.dirpos]
            self.show_image()

    def toggle_bg_color(self):
        """Toggle background color."""
        if self.qview_bg_color == 'white':
            self.qview_bg_color = 'gray'
            self.qscene.setBackgroundBrush(QtCore.Qt.gray)
        else:
            self.qview_bg_color = 'white'
            self.qscene.setBackgroundBrush(QtCore.Qt.white)


class CanvasCompare(Canvas):

    def __init__(self, parent, num_scene=2):
        super(CanvasCompare, self).__init__(parent)
        self.toggle_bg_color()  # default bg color: gray
