import os
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLineEdit, QPushButton,
                             QWidget)

from handyview.view_scene import HVScene, HVView
from handyview.widgets import ColorLabel, HVLable, show_msg


class Canvas(QWidget):
    """Main canvas showing a single view."""

    def __init__(self, parent, db, num_view=1):
        super(Canvas, self).__init__()
        self.parent = parent
        self.db = db  # database
        self.num_view = num_view

        # initialize widgets and layout
        self.init_widgets_layout()
        self.qview_bg_color = 'white'
        self.show_image(init=True)

        # set bg color to light_gray when num_view > 1
        if self.num_view > 1:
            self.toggle_bg_color()

    def init_widgets_layout(self):
        # QGraphicsView - QGraphicsScene - QPixmap
        self.qscenes = []
        self.qviews = []
        if self.num_view == 1:
            show_info = True
        else:
            show_info = False
        for i in range(self.num_view):
            self.qscenes.append(HVScene(self, show_info=show_info))
            self.qviews.append(
                HVView(self.qscenes[i], self, show_info=show_info))

        # ---------------------------------------
        # Basic info, TODO: for each view
        # ---------------------------------------

        # name label showing image index and image path
        self.name_label = HVLable('', self, 'green', 'Times', 15)
        # goto edit and botton for indexing
        self.goto_edit = QLineEdit()
        self.goto_edit.setPlaceholderText('Index. Default: 1')
        goto_btn = QPushButton('GO', self)
        goto_btn.clicked.connect(self.goto_button_clicked)

        # ---------------------------------------
        # Dock window
        # ---------------------------------------
        if self.num_view == 1:
            # info label showing image shape, size and color type
            self.info_label = HVLable('', self, 'blue', 'Times', 12)
            # zoom label showing zoom ratio
            self.zoom_label = HVLable('1.00', self, 'green', 'Times', 12)
            # mouse position and mouse rgb value
            mouse_pos_text = ('Cursor position:\n (ignore zoom)\n'
                              ' Height(y): 0.0\n Width(x):  0.0')
            self.mouse_pos_label = HVLable(mouse_pos_text, self, 'black',
                                           'Times', 12)
            self.mouse_rgb_label = HVLable(' (255, 255, 255, 255)', self,
                                           'black', 'Times', 12)
            # pixel color at the mouse position
            self.mouse_color_title = HVLable('RGBA:', self, 'black', 'Times',
                                             12)
            self.mouse_color_label = ColorLabel(color=(255, 255, 255))

            # selection rectangle position and length
            selection_pos_text = ('Rect Pos: (H, W)\n Start: 0, 0\n'
                                  ' End  : 0, 0\n Len  : 0, 0')
            self.selection_pos_label = HVLable(selection_pos_text, self,
                                               'black', 'Times', 12)

            # include and exclude names
            self.include_names_label = HVLable('', self, 'black', 'Times', 12)
            self.exclude_names_label = HVLable('', self, 'black', 'Times', 12)
            # comparison folders
            self.comparison_label = HVLable('', self, 'red', 'Times', 12)

        # ---------------------------------------
        # layouts
        # ---------------------------------------
        main_layout = QGridLayout(self)
        # QGridLayout:
        # int row, int column, int rowSpan, int columnSpan
        main_layout.addWidget(self.name_label, 0, 0, 1, 50)

        name_grid = QGridLayout()
        name_grid.addWidget(self.goto_edit, 0, 0, 1, 1)
        name_grid.addWidget(goto_btn, 0, 1, 1, 1)
        main_layout.addLayout(name_grid, 1, 0, 1, 10)

        if self.num_view == 1:
            main_layout.addWidget(self.qviews[0], 0, 0, -1, 50)
        elif self.num_view == 2:
            main_layout.addWidget(self.qviews[0], 0, 0, -1, 30)
            main_layout.addWidget(self.qviews[1], 0, 30, -1, 30)
        elif self.num_view == 3:
            main_layout.addWidget(self.qviews[0], 0, 0, -1, 30)
            main_layout.addWidget(self.qviews[1], 0, 30, -1, 30)
            main_layout.addWidget(self.qviews[2], 0, 60, -1, 30)
        elif self.num_view == 4:
            main_layout.addWidget(self.qviews[0], 0, 0, 25, 30)
            main_layout.addWidget(self.qviews[1], 0, 30, 25, 30)
            main_layout.addWidget(self.qviews[2], 25, 0, 25, 30)
            main_layout.addWidget(self.qviews[3], 25, 30, 25, 30)

        # blank label for layout
        blank_label = HVLable('', self, 'black', 'Times', 12)
        main_layout.addWidget(blank_label, 61, 0, 1, 1)

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.key() == QtCore.Qt.Key_F9:
            self.toggle_bg_color()
        elif event.key() == QtCore.Qt.Key_R:
            for qview in self.qviews:
                qview.set_zoom(1)
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
            for qview in self.qviews:
                qview.zoom_in()
        elif event.key() == QtCore.Qt.Key_Down:
            for qview in self.qviews:
                qview.zoom_out()

    def goto_button_clicked(self):
        goto_str = self.goto_edit.text()
        if goto_str == '':
            self.db.pidx = 0
        elif goto_str.isdigit():
            self.db.pidx = int(goto_str) - 1
        else:
            return
        self.show_image()

    def add_cmp_folder(self, cmp_path):
        is_same_len, img_len_list = self.db.add_cmp_folder(cmp_path)

        show_str = 'Number for each folder:\n\t' + '\n\t'.join(
            map(str, img_len_list))
        self.comparison_label.setText(show_str)
        if is_same_len is False:
            msg = ('Comparison folders have differnet number of images.\n'
                   f'{show_str}')
            show_msg('Warning', 'Warning!', msg)

    def update_path_list(self):
        is_same_len, img_len_list = self.db.update_path_list()
        if len(img_len_list) > 1:
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
        interval_mode = (self.db.get_folder_len() == 1)
        for idx, qscene in enumerate(self.qscenes):
            if interval_mode:
                pidx = self.db.pidx + idx
                img_path = self.db.get_path(pidx=pidx)
                width, height = self.db.get_shape(pidx=pidx)
            else:
                fidx = idx  # always has the same folder order
                img_path = self.db.get_path(fidx=fidx)
                width, height = self.db.get_shape(fidx=fidx)
            qimg = QImage(img_path)
            if idx == 0:
                # for HVView, HVScene show_mouse_color.
                # only work on first qimg (main canvas mode)
                self.qimg = qimg

            qpixmap = QPixmap.fromImage(qimg)

            qscene.clear()
            qscene.addPixmap(qpixmap)
            qscene.set_width_height(width, height)
            # put image always in the center of a QGraphicsView
            qscene.setSceneRect(0, 0, width, height)

        # show image path in the statusbar
        self.parent.set_statusbar(f'{img_path}')

        # update information panel
        basename = os.path.basename(img_path)
        self.name_label.setText(f'[{self.db.pidx + 1:d} / '
                                f'{self.db.get_path_len():d}] '
                                f'{basename}')

        if self.num_view == 1:
            self.info_label.setText(
                'Info: \n'
                f' Height: {height:d}\n Width:  {width:d}\n'
                f' Size: {self.db.get_file_size()}\n'
                f' Type: {self.db.get_color_type()}')

        if init:
            if width < 500:
                self.qviews[0].set_zoom(500 // height)
            else:
                self.qviews[0].set_zoom(1)
        for qview in self.qviews:
            qview.set_transform()

    def dir_browse(self, step):
        self.db.path_browse(step)
        self.show_image()

    def toggle_bg_color(self):
        if self.qview_bg_color == 'white':
            self.qview_bg_color = 'lightgray'
            for qscene in self.qscenes:
                qscene.setBackgroundBrush(QColor(211, 211, 211))
        else:
            self.qview_bg_color = 'white'
            for qscene in self.qscenes:
                qscene.setBackgroundBrush(QtCore.Qt.white)
