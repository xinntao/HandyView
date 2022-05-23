import os
import subprocess
import sys
from glob import glob
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QPushButton, QScrollArea, QVBoxLayout, QWidget)
from shutil import rmtree
from time import localtime, strftime

from handyview.utils import ROOT_DIR, crop_images
from handyview.widgets import HLine, HVLable, show_msg


class CanvasCrop(QWidget):
    """Crop canvas

    TODO:
    1. modify selected rectangular
    2. drag and drop mode

    """

    def __init__(self, parent, db):
        super(CanvasCrop, self).__init__()
        self.parent = parent
        self.db = db  # database

        # initialize widgets and layout
        self.init_widgets_layout()

        # get patch and rect folder
        self.patch_folder = os.path.join(os.path.dirname(self.db.path_list[0][0]), os.pardir, 'crop_patch')
        self.rect_folder = os.path.join(os.path.dirname(self.db.path_list[0][0]), os.pardir, 'draw_rect')

    def init_widgets_layout(self):
        # show thumbnails
        self.scrollArea = QScrollArea(widgetResizable=True)
        self.thumbnails = QListWidget()
        self.thumbnails.setIconSize(QSize(200, 150))
        self.thumbnails.setViewMode(QListWidget.IconMode)
        self.thumbnails.setResizeMode(QListWidget.Adjust)
        self.scrollArea.setWidget(self.thumbnails)
        self.thumbnails.itemSelectionChanged.connect(self.selectionChanged)

        # show thumbnails for cropped images
        self.crop_scrollArea = QScrollArea(widgetResizable=True)
        self.crop_thumbnails = QListWidget()
        self.crop_thumbnails.setIconSize(QSize(200, 150))
        self.crop_thumbnails.setViewMode(QListWidget.IconMode)
        self.crop_thumbnails.setResizeMode(QListWidget.Adjust)
        self.crop_scrollArea.setWidget(self.crop_thumbnails)

        # show thumbnails for images with rect
        self.rect_scrollArea = QScrollArea(widgetResizable=True)
        self.rect_thumbnails = QListWidget()
        self.rect_thumbnails.setIconSize(QSize(200, 150))
        self.rect_thumbnails.setViewMode(QListWidget.IconMode)
        self.rect_thumbnails.setResizeMode(QListWidget.Adjust)
        self.rect_scrollArea.setWidget(self.rect_thumbnails)

        # ---------------------------------------
        # layouts
        # ---------------------------------------
        # selected rectangular
        label_height = HVLable('Height', self, color='blue')
        label_width = HVLable('Width', self, color='blue')
        label_start = HVLable('Start', self, color='blue')
        label_len = HVLable('Length', self, color='blue')
        # get init label pos
        self.edit_start_h = QLineEdit('0')
        self.edit_start_w = QLineEdit('0')
        self.edit_len_h = QLineEdit('0')
        self.edit_len_w = QLineEdit('0')
        # scale
        label_scale = HVLable('Scale', self, color='blue')
        label_ratio = HVLable('Ratio', self, color='blue')
        label_mode = HVLable('Mode', self, color='blue')
        self.edit_ratio = QLineEdit('2')
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(['bicubic', 'bilinear', 'nearest'])
        # rect
        label_line_width = HVLable('Rect: Line width', self, color='blue')
        label_line_color = HVLable('Color', self, color='blue')
        self.edit_line_width = QLineEdit('2')
        self.combo_line_color = QComboBox()
        self.combo_line_color.addItems([
            'yellow', 'green', 'red', 'magenta', 'matlab_blue', 'matlab_orange', 'matlab_yellow', 'matlab_purple',
            'matlab_green', 'matlab_liblue', 'matlab_brown'
        ])
        # config grid
        config_grid = QGridLayout()
        # config_grid.setSpacing(10)
        # int row, int column, int rowSpan, int columnSpan
        # -----  Start  Len   -----  Scale
        # Height [   ] [   ]  Ratio  [   ]
        # Width  [   ] [   ]  Mode   Combo
        # --------------------------------
        # Rect: Line Width [   ], Color Combo
        # row 0
        config_grid.addWidget(label_start, 0, 1, 1, 1)
        config_grid.addWidget(label_len, 0, 2, 1, 1)
        config_grid.addWidget(label_scale, 0, 4, 1, 1)
        # row 1
        config_grid.addWidget(label_height, 1, 0, 1, 1)
        config_grid.addWidget(self.edit_start_h, 1, 1, 1, 1)
        config_grid.addWidget(self.edit_len_h, 1, 2, 1, 1)
        config_grid.addWidget(label_ratio, 1, 3, 1, 1)
        config_grid.addWidget(self.edit_ratio, 1, 4, 1, 1)
        # row 2
        config_grid.addWidget(label_width, 2, 0, 1, 1)
        config_grid.addWidget(self.edit_start_w, 2, 1, 1, 1)
        config_grid.addWidget(self.edit_len_w, 2, 2, 1, 1)
        config_grid.addWidget(label_mode, 2, 3, 1, 1)
        config_grid.addWidget(self.combo_mode, 2, 4, 1, 1)
        # row 3: horizontal line
        config_grid.addWidget(HLine(), 3, 0, 1, 5)
        # row 4
        config_grid.addWidget(label_line_width, 4, 0, 1, 1)
        config_grid.addWidget(self.edit_line_width, 4, 1, 1, 1)
        config_grid.addWidget(label_line_color, 4, 2, 1, 1)
        config_grid.addWidget(self.combo_line_color, 4, 3, 1, 1)
        # blank
        config_grid.addWidget(QLabel(), 5, 0, 5, 5)

        # actions
        button_add = QPushButton('Add ALL', self)
        button_add.clicked.connect(self.add_all_images)
        button_selection_pos = QPushButton('Set Selection Pos', self)
        button_selection_pos.clicked.connect(self.set_selection_pos)
        button_crop = QPushButton('Crop', self)
        button_crop.clicked.connect(self.crop_images)
        button_open_patch = QPushButton('Open Patch Folder', self)
        button_open_patch.clicked.connect(self.open_patch_folder)
        button_open_rect = QPushButton('Open Rect Folder', self)
        button_open_rect.clicked.connect(self.open_rect_folder)
        button_open_history = QPushButton('Open History Info', self)
        button_open_history.clicked.connect(self.open_history_file)

        button_delete_patch = QPushButton('Delete Patch Folder', self)
        button_delete_patch.clicked.connect(self.delete_patch_folder)
        button_delete_rect = QPushButton('Delete Rect Folder', self)
        button_delete_rect.clicked.connect(self.delete_rect_folder)

        button_add.setStyleSheet('background-color : lightblue')
        button_crop.setStyleSheet('background-color : lightblue')
        button_open_patch.setStyleSheet('background-color : lightgreen')
        button_open_rect.setStyleSheet('background-color : lightgreen')

        action_grid = QGridLayout()
        action_grid.addWidget(button_add, 0, 0, 1, 1)
        action_grid.addWidget(button_selection_pos, 1, 0, 1, 1)
        action_grid.addWidget(button_crop, 2, 0, 1, 1)
        action_grid.addWidget(HLine(), 3, 0, 1, 1)
        action_grid.addWidget(button_open_patch, 4, 0, 1, 1)
        action_grid.addWidget(button_open_rect, 5, 0, 1, 1)
        action_grid.addWidget(button_open_history, 6, 0, 1, 1)
        action_grid.addWidget(HLine(), 7, 0, 1, 1)
        action_grid.addWidget(button_delete_patch, 8, 0, 1, 1)
        action_grid.addWidget(button_delete_rect, 9, 0, 1, 1)

        config_box = QGroupBox('Config')
        config_box.setLayout(config_grid)
        action_box = QGroupBox('Actions')
        action_box.setLayout(action_grid)

        panel_grid = QVBoxLayout()
        panel_grid.addWidget(config_box)
        panel_grid.addWidget(action_box)
        panel_grid.setSpacing(0)  # No Spacing
        panel_grid.addStretch(1)  # No Expanding when the window expands

        # ---------------------------------------
        # main layouts
        # ---------------------------------------
        main_layout = QGridLayout(self)
        # int row, int column, int rowSpan, int columnSpan
        main_layout.addWidget(self.scrollArea, 0, 0, 20, 20)
        main_layout.addWidget(self.crop_scrollArea, 20, 0, 20, 20)
        main_layout.addWidget(self.rect_scrollArea, 40, 0, 20, 20)

        main_layout.addLayout(panel_grid, 0, 20, 60, 5)

    def selectionChanged(self):
        print('Selected items: ', self.thumbnails.selectedItems())

    def set_selection_pos(self):
        start_h, start_w, len_h, len_w = self.db.selection_pos
        self.edit_start_h.setText(str(start_h))
        self.edit_start_w.setText(str(start_w))
        self.edit_len_h.setText(str(len_h))
        self.edit_len_w.setText(str(len_w))

    def add_all_images(self):
        self.set_selection_pos()
        # 1. clear all the existing thumbnails
        self.thumbnails.clear()
        # 2. add thumbnails
        for path in self.db.path_list[0]:
            self.thumbnails.addItem(QListWidgetItem(QIcon(path), os.path.basename(path)))

    def update_crop_rect_images(self):
        # 1. clear all the existing thumbnails
        self.crop_thumbnails.clear()
        self.rect_thumbnails.clear()
        # 2. add thumbnails
        for path in sorted(glob(os.path.join(self.patch_folder, '*'))):
            self.crop_thumbnails.addItem(QListWidgetItem(QIcon(path), os.path.basename(path)))
        if os.path.isdir(self.rect_folder):
            for path in sorted(glob(os.path.join(self.rect_folder, '*'))):
                self.rect_thumbnails.addItem(QListWidgetItem(QIcon(path), os.path.basename(path)))

    def crop_images(self):
        # 1. check all images has the same shape
        # TODO
        # 2. crop
        try:
            start_h = int(self.edit_start_h.text())
            start_w = int(self.edit_start_w.text())
            len_h = int(self.edit_len_h.text())
            len_w = int(self.edit_len_w.text())
            ratio = int(self.edit_ratio.text())
            mode = self.combo_mode.currentText()
            line_width = int(self.edit_line_width.text())
            line_color = self.combo_line_color.currentText()
        except ValueError as error:
            show_msg(icon='Critical', title='Title', text=f'Wrong input: {error}', timeout=None)
            return 0

        try:
            crop_images(
                self.db.path_list[0], [start_h, start_w, len_h, len_w],
                self.patch_folder,
                enlarge_ratio=ratio,
                interpolation=mode,
                line_width=line_width,
                color=line_color,
                rect_folder=self.rect_folder)
        except Exception as error:
            show_msg(icon='Critical', title='Title', text=f'Crop error: {error}', timeout=None)
        else:
            # update crop info to txt
            self.record_crop_history(self.db.path_list[0][0], [start_h, start_w, len_h, len_w], ratio, mode)
            # show cropped image
            self.update_crop_rect_images()

    def record_crop_history(self, path, pos, ratio, mode):
        pos_str = ', '.join(map(str, pos))
        content = f'{strftime("%Y%m%d-%H%M%S", localtime())} {path} ({pos_str}) {ratio} {mode}\n'
        try:
            with open(os.path.join(ROOT_DIR, 'history_crop.txt'), 'a') as f:
                f.write(content)
        except Exception as error:
            show_msg(icon='Warning', title='Title', text=f'Record crop history error: {error}', timeout=None)

    def open_patch_folder(self):
        try:
            if sys.platform == "win32":
                os.startfile(self.patch_folder)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, self.patch_folder])
        except Exception as error:
            show_msg(icon='Critical', title='Title', text=f'Open error: {error}', timeout=None)

    def open_rect_folder(self):
        try:
            if sys.platform == "win32":
                os.startfile(self.rect_folder)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, self.rect_folder])
        except Exception as error:
            show_msg(icon='Critical', title='Title', text=f'Open error: {error}', timeout=None)

    def delete_patch_folder(self):
        try:
            rmtree(self.patch_folder)
        except Exception as error:
            show_msg(icon='Critical', title='Title', text=f'Open error: {error}', timeout=None)

    def delete_rect_folder(self):
        try:
            rmtree(self.rect_folder)
        except Exception as error:
            show_msg(icon='Critical', title='Title', text=f'Open error: {error}', timeout=None)

    def open_history_file(self):
        try:
            if sys.platform == "win32":
                os.startfile(os.path.join(ROOT_DIR, 'history_crop.txt'))
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, os.path.join(ROOT_DIR, 'history_crop.txt')])
        except Exception as error:
            show_msg(icon='Critical', title='Title', text=f'Open error: {error}', timeout=None)

    def keyPressEvent(self, event):
        pass
