import os

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QImage, QPainter, QPen, QPixmap, qRgb
from PyQt5.QtWidgets import QApplication, QGridLayout, QSplitter, QWidget

from handyview.view_scene import HVScene, HVView
from handyview.widgets import ColorLabel, HVLable, show_msg
# For LUT
import cv2

class Canvas(QWidget):
    """Main canvas"""

    def __init__(self, parent, db, num_view=1):
        super(Canvas, self).__init__()
        self.parent = parent
        self.db = db  # database
        self.num_view = num_view  # number of views in layouts

        # initialize widgets and layout
        self.init_widgets_layout()
        self.qview_bg_color = 'white'
        self.show_fingerprint = False

        # set bg color to light_gray when num_view > 1
        if self.num_view > 1:
            self.toggle_bg_color()

        # for auto zoom ratio
        self.target_zoom_width = 0

        self.show_image(init=True)

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
            self.qviews.append(HVView(self.qscenes[i], self, show_info=show_info))

        # ---------------------------------------
        # Dock window widgets
        # ---------------------------------------
        if self.num_view == 1:
            # zoom label showing zoom ratio
            self.zoom_label = HVLable('1.00', self, 'green', 'Times', 12)
            # mouse position and mouse rgb value
            mouse_pos_text = ('Cursor position:\n (ignore zoom)\nHeight(y): 0.0\n Width(x):  0.0')
            self.mouse_pos_label = HVLable(mouse_pos_text, self, 'black', 'Times', 12)
            self.mouse_rgb_label = HVLable(' (255, 255, 255, 255)', self, 'black', 'Times', 12)
            # pixel color at the mouse position
            self.mouse_color_title = HVLable('RGBA:', self, 'black', 'Times', 12)
            self.mouse_color_label = ColorLabel(color=(255, 255, 255))

            # selection rectangle position and length
            selection_pos_text = ('Rect Pos: (H, W)\n Start: 0, 0\nEnd  : 0, 0\n Len  : 0, 0')
            self.selection_pos_label = HVLable(selection_pos_text, self, 'black', 'Times', 12)

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
        if self.num_view == 1:
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
            splitter = QSplitter(QtCore.Qt.Vertical)
            splitter_1 = QSplitter(QtCore.Qt.Horizontal)
            splitter_2 = QSplitter(QtCore.Qt.Horizontal)
            splitter_1.addWidget(self.qviews[0])
            splitter_1.addWidget(self.qviews[1])
            splitter_2.addWidget(self.qviews[2])
            splitter_2.addWidget(self.qviews[3])
            splitter.addWidget(splitter_1)
            splitter.addWidget(splitter_2)
            main_layout.addWidget(splitter, 0, 0, -1, 50)

        # link zoom operation
        for i in range(self.num_view):
            for j in range(self.num_view):
                if i != j:
                    self.qviews[i].zoom_signal.connect(self.qviews[j].set_zoom)

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
            if modifiers == QtCore.Qt.ControlModifier:
                # copy image to clipboard
                clipboard = QApplication.clipboard()
                mime_data = QtCore.QMimeData()
                full_path = os.path.abspath(self.img_path)
                mime_data.setUrls([QtCore.QUrl(f'file:///{full_path}')])
                clipboard.setMimeData(mime_data)
            else:
                self.compare_folders(1)
        elif event.key() == QtCore.Qt.Key_V:
            self.compare_folders(-1)

        elif event.key() == QtCore.Qt.Key_Z:
            if modifiers == QtCore.Qt.ControlModifier:
                # cancel auto zoom
                self.target_zoom_width = 0
            else:
                self.auto_zoom()

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
            if modifiers == QtCore.Qt.ShiftModifier:  # quickly zoom in all qviews
                for qview in self.qviews:
                    qview.zoom_in(scale=1.2)
            elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
                # only modify the zoom ration for the current view
                for qview in self.qviews:
                    if qview.hasFocus():
                        qview.zoom_in(scale=1.05, emit_signal=False)
            else:
                for qview in self.qviews:
                    qview.zoom_in(scale=1.05)
        elif event.key() == QtCore.Qt.Key_Down:
            if modifiers == QtCore.Qt.ShiftModifier:  # quickly zoom out all qviews
                for qview in self.qviews:
                    qview.zoom_out(scale=1.2)
            elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
                # only modify the zoom ration for the current view
                for qview in self.qviews:
                    if qview.hasFocus():
                        qview.zoom_out(scale=1.05, emit_signal=False)
            else:
                for qview in self.qviews:
                    qview.zoom_out(scale=1.05)

        elif event.key() == QtCore.Qt.Key_F11:
            self.parent.switch_fullscreen()

    def goto_index(self, index):
        self.db.pidx = index
        self.show_image()

    def add_cmp_folder(self, cmp_path):
        is_same_len, img_len_list = self.db.add_cmp_folder(cmp_path)
        show_str = 'Number for each folder:\n\t' + '\n\t'.join(map(str, img_len_list))
        self.comparison_label.setText(show_str)
        if is_same_len is False:
            msg = f'Comparison folders have different number of images.\n{show_str}'
            show_msg('Warning', 'Warning!', msg)
        # refresh
        self.show_image()

    def update_path_list(self):
        is_same_len, img_len_list = self.db.update_path_list()
        show_str = 'Comparison:\n # for each folder:\n\t' + '\n\t'.join(map(str, img_len_list))
        self.comparison_label.setText(show_str)
        if is_same_len is False:
            msg = f'Comparison folders have different number of images.\n{show_str}'
            show_msg('Warning', 'Warning!', msg)

    def compare_folders(self, step):
        self.db.folder_browse(step)
        self.show_image()

        if self.num_view == 1:
            # when in main folder (1st folder), show red color
            if self.db.fidx == 0:
                self.comparison_label.setStyleSheet('QLabel {color : red;}')
            else:
                self.comparison_label.setStyleSheet('QLabel {color : black;}')

    def show_image(self, init=False):
        interval_mode = (self.db.get_folder_len() == 1)
        for idx, qscene in enumerate(self.qscenes):
            qview = self.qviews[idx]
            if interval_mode:
                pidx = self.db.pidx + idx
                img_path = self.db.get_path(pidx=pidx)[0]
                width, height = self.db.get_shape(pidx=pidx)
                file_size = self.db.get_file_size(pidx=pidx)
                color_type = self.db.get_color_type(pidx=pidx)
                if self.show_fingerprint:
                    md5, phash = self.db.get_fingerprint(pidx=pidx)
                    md5_0, phash_0 = self.db.get_fingerprint(pidx=self.db.pidx)
            else:
                fidx = self.db.fidx + idx
                img_path = self.db.get_path(fidx=fidx)[0]
                width, height = self.db.get_shape(fidx=fidx)
                file_size = self.db.get_file_size(fidx=fidx)
                color_type = self.db.get_color_type(fidx=fidx)
                if self.show_fingerprint:
                    md5, phash = self.db.get_fingerprint(fidx=fidx)
                    md5_0, phash_0 = self.db.get_fingerprint(fidx=self.db.fidx)

            # get LUT and processing
            cv2_lut, cv2_lut_name = self.db.get_LUT()
            processing = self.db.get_processing()

            # None use directly Qt
            if cv2_lut == 0 and processing == "None":
                # no LUT --> use QImage function
                qimg = QImage(img_path)  # using Qt to load the image
            else:
                # Using OpenCV for image processing w/o LUT
                if cv2_lut == 0 and processing != "None":
                    # No LUT but processing (on RGB)
                    cvimg = cv2.imread(img_path, flags=cv2.IMREAD_COLOR)

                    # Apply the different processing params
                    if processing == "Shift 2 Bit":
                        cvimgproc = cvimg * 4
                    elif processing == "Histogram equalization":
                        cvimgyuv = cv2.cvtColor(cvimg, cv2.COLOR_BGR2YUV)
                        # equalize the histogram of the Y channel
                        cvimgyuv[:, :, 0] = cv2.equalizeHist(cvimgyuv[:, :, 0])

                        # convert the YUV image back to RGB format
                        cvimgproc = cv2.cvtColor(cvimgyuv, cv2.COLOR_YUV2BGR)
                    else:
                        cvimgproc = cvimg

                # Using OpenCV for image processing w LUT
                if cv2_lut != 0:
                    # using OpenCV to load the image in gray and apply the LUT
                    cvimg = cv2.imread(img_path, flags=cv2.IMREAD_GRAYSCALE)

                    # Apply the different processing params
                    if processing == "Shift 2 Bit":
                        cvimgproc = cvimg * 4
                    elif processing == "Histogram equalization":
                        cvimgproc = cv2.equalizeHist(cvimg)
                    else:
                        cvimgproc = cvimg

                # Apply LUT
                if cv2_lut != 0:
                    # Apply LUT
                    lutImg = cv2.applyColorMap(cvimgproc, cv2_lut)
                else:
                    lutImg = cvimgproc

                # finally set image for Qt
                qimg = QImage(lutImg.data, lutImg.shape[1], lutImg.shape[0], lutImg.strides[0], QImage.Format_RGB888)

            self.img_path = img_path
            if idx == 0:
                # for HVView, HVScene show_mouse_color.
                # only work on the first qimg (main canvas mode)
                self.qimg = qimg

                # show image path in the statusbar
                self.parent.set_statusbar(f'{img_path}')

            # --------------- auto zoom scale ratio -------------------
            if self.target_zoom_width > 0:
                qview.set_zoom(self.target_zoom_width / qimg.width())
            # --------------- end of auto zoom scale ratio -------------------

            # shown text
            # basename = os.path.basename(img_path)

            def get_parent_dir(path, levels=1):
                common = path
                for _ in range(levels + 1):
                    common = os.path.dirname(common)
                return os.path.relpath(path, common)

            shown_path = get_parent_dir(img_path, 2).replace('\\', '/')

            if interval_mode:
                shown_idx = self.db.pidx + 1 + idx
            else:
                shown_idx = self.db.pidx + 1

            # TODO: add zoom ratio
            head, tail = os.path.split(shown_path)
            shown_text = [
                f'[{shown_idx:d} / {self.db.get_path_len():d}] {tail}', head, f'{height:d} x {width:d}, {file_size}',
                f'{color_type}'
            ]

            # Add processing and LUT
            if processing != "None":
                shown_text.append(" Processing:" + processing)
            if cv2_lut != 0:
                shown_text.append(" LUT:" + cv2_lut_name)

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

            if qview.hasFocus():
                color = 'green'
            else:
                color = 'red'
            qview.set_shown_text(shown_text, color)

            # qview.viewport().update()
            qpixmap = QPixmap.fromImage(qimg)

            # draw border
            if not interval_mode and len(self.qscenes) == 1 and self.db.fidx == 0:  # compare mode, the main image
                painter = QPainter()
                painter.begin(qpixmap)
                pen = QPen(QColor(220, 0, 0), 5, QtCore.Qt.SolidLine)
                painter.setPen(pen)
                painter.drawRect(0, 0, qpixmap.width(), qpixmap.height())
                painter.end()

            qscene.clear()
            qscene.addPixmap(qpixmap)
            qscene.set_width_height(width, height)
            # put image always in the center of a QGraphicsView
            qscene.setSceneRect(0, 0, width, height)
            # set the scroll bar position, so that it can keep the same position in auto_zoom
            qview.verticalScrollBar().setSliderPosition(qview.vertical_scroll_value)
            qview.horizontalScrollBar().setSliderPosition(qview.horizontal_scroll_value)

        # set include and exclude name info
        if self.num_view == 1:
            # show include names in the information panel
            if isinstance(self.db.include_names, list):
                show_str = 'Include:\n\t' + '\n\t'.join(self.db.include_names)
                self.include_names_label.setStyleSheet('QLabel {color : blue;}')
            else:
                show_str = 'Include: None'
                self.include_names_label.setStyleSheet('QLabel {color : black;}')
            self.include_names_label.setText(show_str)
            # show exclude names in the information panel
            if isinstance(self.db.exclude_names, list):
                show_str = 'Exclude:\n\t' + '\n\t'.join(self.db.exclude_names)
                self.exclude_names_label.setStyleSheet('QLabel {color : red;}')
            else:
                show_str = 'Exclude: None'
                self.exclude_names_label.setStyleSheet('QLabel {color : black;}')
            self.exclude_names_label.setText(show_str)

        if init:
            if width < 500:
                self.qviews[0].set_zoom(500 // width)
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

    def auto_zoom(self):
        target_zoom_width = self.qimg.width() * self.qviews[0].zoom
        self.target_zoom_width = int(target_zoom_width)
        return self.target_zoom_width
