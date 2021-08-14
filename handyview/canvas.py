import os
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QGridLayout, QSplitter, QWidget

from handyview.view_scene import HVScene, HVView
from handyview.widgets import ColorLabel, HVLable, show_msg


class Canvas(QWidget):
    """Main canvas

    Attributes:
        parent (MainWindow, subclass of QMainWindow):

        db (HVDB):
        num_view (int): allowed values → 1, 2, 3, 4 ← number of images shown in canvas
        qimg (TYPE): Description

        qscenes (list(QGraphicsScene))
        qviews (list(QGraphicsView)): Description
        qview_bg_color (str): 'white' or 'lightgray' ← background color

        show_fingerprint (bool):

        mouse_color_title (HVLable):
        comparison_label (HVLable):
        exclude_names_label (HVLable):
        include_names_label (HVLable):
        mouse_color_label (HVLable):
        mouse_pos_label (HVLable):
        mouse_rgb_label (HVLable):
        selection_pos_label (HVLable):
        zoom_label (HVLable):
    """

    def __init__(self, parent, db, num_view=1):
        super(Canvas, self).__init__()
        self.parent = parent  # QMainWindow
        self.db = db  # database
        self.num_view = num_view  # number of views in layouts

        # initialize widgets and layout
        self.__init_widgets_layout()
        self.qview_bg_color = 'white'
        self.show_fingerprint = False
        self.show_image(init=True)

        # set bg color to light_gray when num_view > 1
        if self.num_view > 1:
            self.__toggle_bg_color()

    def __init_blank_scenes_and_views(self):
        # QGraphicsView - QGraphicsScene - QPixmap
        self.qscenes = []
        self.qviews = []
        if self.num_view == 1:
            show_info = True
        else:
            show_info = False
        for i in range(self.num_view):
            self.qscenes.append(HVScene(self, show_info=show_info))
            self.qviews.append(HVView(self.qscenes[i],
                                      self,
                                      show_info=show_info,
                                      fast_zoom=self.parent.fast_zoom
                                      )
                               )

    def __init_info_panel_widgets(self):
        # ---------------------------------------
        # Dock window widgets
        # ---------------------------------------
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

    def __init_widgets_layout(self):
        self.__init_blank_scenes_and_views()

        # ---------------------------------------
        # layouts
        # ---------------------------------------
        main_layout = QGridLayout(self)
        # QGridLayout:
        # int row, int column, int rowSpan, int columnSpan
        if self.num_view == 1:
            self.__init_info_panel_widgets()
            main_layout.addWidget(self.qviews[0], 0, 0, -1, 50)
        elif self.num_view == 2:
            splitter = QSplitter(QtCore.Qt.Horizontal)
            splitter.addWidget(self.qviews[0])
            splitter.addWidget(self.qviews[1])
            main_layout.addWidget(splitter, 0, 0, -1, 50)
        elif self.num_view == 3:
            splitter = QSplitter(QtCore.Qt.Horizontal)
            splitter.addWidget(self.qviews[0])
            splitter.addWidget(self.qviews[1])
            splitter.addWidget(self.qviews[2])
            main_layout.addWidget(splitter, 1, 0, -1, 50)
        elif self.num_view == 4:
            main_splitter = QSplitter(QtCore.Qt.Vertical)
            sub_splitter_1 = QSplitter(QtCore.Qt.Horizontal)
            sub_splitter_2 = QSplitter(QtCore.Qt.Horizontal)
            sub_splitter_1.addWidget(self.qviews[0])
            sub_splitter_1.addWidget(self.qviews[1])
            sub_splitter_2.addWidget(self.qviews[2])
            sub_splitter_2.addWidget(self.qviews[3])
            main_splitter.addWidget(sub_splitter_1)
            main_splitter.addWidget(sub_splitter_2)
            main_layout.addWidget(main_splitter, 0, 0, -1, 50)

        # link zoom operation; used in comparison view: when when one HVView
        # zoom changes, zoom state is emitted and connected to set zoom of
        # other HVView's in the layout
        for i in range(self.num_view):
            for j in range(self.num_view):
                if i != j:
                    self.qviews[i].zoom_signal.connect(self.qviews[j].set_zoom)

        # blank label for layout
        blank_label = HVLable('', self, 'black', 'Times', 12)
        main_layout.addWidget(blank_label, 61, 0, 1, 1)

    def __toggle_bg_color(self):
        if self.qview_bg_color == 'white':
            self.qview_bg_color = 'lightgray'
            for qscene in self.qscenes:
                qscene.setBackgroundGrey()
        else:
            self.qview_bg_color = 'white'
            for qscene in self.qscenes:
                qscene.setBackgroundWhite()

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.key() == QtCore.Qt.Key_F9:
            self.__toggle_bg_color()
        elif event.key() == QtCore.Qt.Key_R and event.modifiers() & QtCore.Qt.ControlModifier:
            for qview in self.qviews:
                if qview.fast_zoom:
                    qview.precise_zoom()
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
            if modifiers == QtCore.Qt.ShiftModifier:
                scale = 1.2
            else:
                scale = 1.05
            for qview in self.qviews:
                qview.zoom_in(scale=scale)
        elif event.key() == QtCore.Qt.Key_Down:
            if modifiers == QtCore.Qt.ShiftModifier:
                scale = 1.2
            else:
                scale = 1.05
            for qview in self.qviews:
                qview.zoom_out(scale=scale)

        elif event.key() == QtCore.Qt.Key_F11:
            self.parent.switch_fullscreen()

    def goto_index(self, index):
        self.db.pidx = index
        self.show_image()

    def add_cmp_folder(self, cmp_path):
        is_same_len, img_len_list = self.db.add_cmp_folder(cmp_path)
        show_str = 'Number for each folder:\n\t' + '\n\t'.join(
            map(str, img_len_list))
        self.comparison_label.setText(show_str)
        if is_same_len is False:
            msg = ('Comparison folders have differnet number of images.\n'
                   f'{show_str}')
            show_msg(self, 'Warning', 'Warning!', msg)

    def clear_cmp_folder(self):
        self.comparison_label.setText("")

    def update_path_list(self):
        is_same_len, img_len_list = self.db.update_path_list()
        if len(img_len_list) > 1:
            show_str = 'Comparison:\n # for each folder:\n\t' + '\n\t'.join(
                map(str, img_len_list))
            self.comparison_label.setText(show_str)
            if is_same_len is False:
                msg = ('Comparison folders have differnet number of images.\n'
                       f'{show_str}')
                show_msg(self, 'Warning', 'Warning!', msg)

    def compare_folders(self, step):
        self.db.folder_browse(step)
        self.show_image()

        if self.num_view == 1:
            # when in main folder (1st folder), show red color
            if self.db.fidx == 0:
                self.comparison_label.setStyleSheet('QLabel {color : red;}')
            else:
                self.comparison_label.setStyleSheet('QLabel {color : black;}')

    def __get_image_data_pidx(self, idx):
        pidx = self.db.pidx + idx
        img_path = self.db.get_img_path(pidx=pidx)[0]
        width, height = self.db.get_shape(pidx=pidx)
        file_size = self.db.get_file_size(pidx=pidx)
        color_type = self.db.get_color_type(pidx=pidx)
        if self.show_fingerprint:
            md5, phash = self.db.get_fingerprint(pidx=pidx)
            md5_0, phash_0 = self.db.get_fingerprint(pidx=self.db.pidx)
        else:
            md5 = phash = md5_0 = phash_0 = None
        return img_path, width, height, file_size, color_type, md5, phash, md5_0, phash_0

    def __get_image_data_fidx(self, idx):
        fidx = self.db.fidx + idx
        img_path = self.db.get_img_path(fidx=fidx)[0]
        width, height = self.db.get_shape(fidx=fidx)
        file_size = self.db.get_file_size(fidx=fidx)
        color_type = self.db.get_color_type(fidx=fidx)
        if self.show_fingerprint:
            md5, phash = self.db.get_fingerprint(fidx=fidx)
            md5_0, phash_0 = self.db.get_fingerprint(fidx=self.db.fidx)
        else:
            md5 = phash = md5_0 = phash_0 = None
        return img_path, width, height, file_size, color_type, md5, phash, md5_0, phash_0

    def __get_shown_text(self, idx, data, interval_mode):
        ''' returns text shown on the top left over the image '''

        img_path, width, height, file_size, color_type, md5, phash, md5_0, phash_0 = data
        # shown text
        basename = os.path.basename(img_path)
        if interval_mode:
            shown_idx = self.db.pidx + 1 + idx
        else:
            shown_idx = self.db.pidx + 1

        # TODO: add zoom ratio
        shown_text = [
            f'[{shown_idx:d} / {self.db.get_image_count():d}] {basename}',
            f'{height:d} x {width:d}, {file_size}', f'{color_type}'
        ]
        # show fingerprint
        if self.show_fingerprint:
            if idx > 0:
                md5_diff = (md5 == md5_0)
                phash_diff = phash - phash_0
                shown_text.append(f'md5: {md5_diff} - {md5}')
                shown_text.append(f'phash: {phash_diff} - {phash}')
            else:
                shown_text.append(f'md5: {md5}')
                shown_text.append(f'phash: {phash}')
        return shown_text

    def __set_include_and_exclude_labels(self):
        # set include and exclude name info
        if self.num_view == 1:  # meaning → Main View
            # show include names in the information panel
            if isinstance(self.db.include_names, list):
                show_str = 'Include:\n\t' + '\n\t'.join(self.db.include_names)
                self.include_names_label.setStyleSheet(
                    'QLabel {color : blue;}')
            else:
                show_str = 'Include: None'
                self.include_names_label.setStyleSheet(
                    'QLabel {color : black;}')
            self.include_names_label.setText(show_str)
            # show exclude names in the information panel
            if isinstance(self.db.exclude_names, list):
                show_str = 'Exclude:\n\t' + '\n\t'.join(self.db.exclude_names)
                self.exclude_names_label.setStyleSheet('QLabel {color : red;}')
            else:
                show_str = 'Exclude: None'
                self.exclude_names_label.setStyleSheet(
                    'QLabel {color : black;}')
            self.exclude_names_label.setText(show_str)

    def show_image(self, init=False):
        # populate_scenes
        interval_mode = (self.db.get_folder_count() == 1)
        for idx, qscene in enumerate(self.qscenes):
            if interval_mode:
                data = self.__get_image_data_pidx(idx)
            else:
                data = self.__get_image_data_fidx(idx)
            img_path, width, height, file_size, color_type, md5, phash, md5_0, phash_0 = data

            shown_text = self.__get_shown_text(idx, data, interval_mode)
            self.qviews[idx].set_shown_text(shown_text)

            qscene.set_image(img_path)
            if idx == 0:
                self.parent.set_statusbar(f'{img_path}')

            # self.qviews[idx].viewport().update()

        self.__set_include_and_exclude_labels()

        if init:
            if width < 500:
                self.qviews[0].set_zoom(500 // width)
            else:
                self.qviews[0].set_zoom(1)
        for qview in self.qviews:
            qview.perform_zoom()

    def dir_browse(self, step):
        self.db.path_browse(step)
        self.show_image()
