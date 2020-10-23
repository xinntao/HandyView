import os
import sys
import glob
import re
from PIL import Image

from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QTransform, QColor, QImage, QIcon, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                             QGraphicsScene)
from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QGroupBox,
                             QLabel, QToolBar, QLineEdit, QPushButton)
from PyQt5.QtWidgets import QFileDialog, QInputDialog

import actions as actions

FORMATS = ('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.ppm', '.PPM',
           '.bmp', '.BMP', '.gif', '.GIF', 'tiff')


class HandyScene(QGraphicsScene):

    def __init__(self, parent=None):
        super(HandyScene, self).__init__()
        self.parent = parent

    def mouseMoveEvent(self, event):
        """Show mouse position on the original image.
        Zooming will not influence the position."""
        x_pos = event.scenePos().x()
        y_pos = event.scenePos().y()
        self.parent.qlabel_info_mouse_pos.setText(
            ('Cursor position: (ignore zoom) \n'
             f"  x (width):\t{x_pos:.1f}\n  y (height):\t{y_pos:.1f}"))
        # if the curse is out of image, the text will be red
        if (x_pos < 0 or y_pos < 0 or x_pos > self.parent.imgw
                or y_pos > self.parent.imgh):
            self.parent.qlabel_info_mouse_pos.setStyleSheet(
                'QLabel {color : red;}')
        else:
            self.parent.qlabel_info_mouse_pos.setStyleSheet(
                'QLabel {color : black;}')
            # show RGB value
            pixel = self.parent.qimg.pixel(int(x_pos), int(y_pos))
            rgba = QColor(pixel).getRgb()  # 8 bit RGBA
            self.parent.qlabel_info_mouse_rgb_value.setText(
                f'\nRGBA: ({rgba[0]:3d}, {rgba[1]:3d}, {rgba[2]:3d}, '
                f'{rgba[3]:3d})')


class HandyView(QGraphicsView):

    def __init__(self, scene, parent=None):
        super(HandyView, self).__init__(scene, parent)
        self.parent = parent
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)
        self.zoom = 1
        self.rotvals = (0, -90, -180, -270)
        self.rotate = 0

    def wheelEvent(self, event):
        moose = event.angleDelta().y() / 120
        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            # zoom in / out
            if moose > 0:
                self.zoom_in()
            elif moose < 0:
                self.zoom_out()
        else:
            # next or previous image
            if moose > 0:
                self.parent.dir_browse(-1)
            elif moose < 0:
                self.parent.dir_browse(1)

    def zoom_in(self):
        self.zoom *= 1.05
        self.parent.qlabel_info_zoom_ration.setText(
            f'\nZoom ration:\t{self.zoom:.1f}')
        self.set_transform()

    def zoom_out(self):
        self.zoom /= 1.05
        self.parent.qlabel_info_zoom_ration.setText(
            f'\nZoom ration:\t{self.zoom:.1f}')
        self.set_transform()

    def set_zoom(self, ratio):
        self.zoom = ratio
        self.parent.qlabel_info_zoom_ration.setText(
            f'\nZoom ration:\t{self.zoom:.1f}')
        self.set_transform()

    def set_transform(self):
        self.setTransform(QTransform().scale(self.zoom,
                                             self.zoom).rotate(self.rotate))


class Canvas(QWidget):
    """The main canvas to show the image, information panel."""

    def __init__(self, parent):
        super(Canvas, self).__init__()
        try:
            self.key = sys.argv[1]
        except IndexError:
            self.key = 'icon.png'  # show the icon image

        self.exclude_names = None
        try:
            open(self.key, 'r')
        except IOError:
            print(f'There was an error opening {self.key}')
            sys.exit(1)

        if self.key.endswith(FORMATS):
            # layout
            main_layout = QGridLayout(self)
            # QGraphicsView - QGraphicsScene - QPixmap
            self.qscene = HandyScene(self)
            self.qview = HandyView(self.qscene, self)

            self.goto_edit = QLineEdit()
            self.goto_edit.setPlaceholderText('Index. Default: 1')
            goto_btn = QPushButton('GO', self)
            goto_btn.clicked.connect(self.goto_button_clicked)
            self.name_label = QLabel(self)
            self.name_label.setFont(QFont('Times', 15))
            self.name_label.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.name_label.setStyleSheet('QLabel {color : green;}')
            self.info_label = QLabel(self)
            self.info_label.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.info_label.setStyleSheet('QLabel {color : blue;}')

            info_grid = QGridLayout()
            info_grid.addWidget(self.goto_edit, 0, 0, 1, 1)
            info_grid.addWidget(goto_btn, 0, 1, 1, 1)
            # info_grid.addWidget(self.name_label, 0, 2, 1, 10)

            main_layout.addLayout(info_grid, 0, 0, 1, 10)
            main_layout.addWidget(self.name_label, 1, 0, 1, 50)
            main_layout.addWidget(self.info_label, 2, 0, 1, 50)

            # main view
            main_layout.addWidget(self.qview, 0, 0, -1, 50)
            # bottom QLabel, show image path
            self.qlabel_img_path = QLabel(self)
            main_layout.addWidget(self.qlabel_img_path, 61, 0, 1, 50)

            # information panel; multiple QLabels, using setText to update
            self.info_group = QGroupBox('Information Panel')
            self.qlabel_info_mouse_pos = QLabel(self)
            self.qlabel_info_mouse_rgb_value = QLabel(self)
            self.qlabel_info_wh = QLabel(self)  # image width and height
            self.qlabel_info_color_type = QLabel(self)  # image color type
            self.qlabel_info_zoom_ration = QLabel(self)  # zoom ratio
            self.qlabel_info_exclude_names = QLabel(self)  # exclude names

            self.qlabel_info_mouse_pos.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_info_mouse_rgb_value.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_info_wh.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_info_color_type.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_info_zoom_ration.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_info_exclude_names.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            # real-time mouse position(relate to original images)
            infor_group_layout = QVBoxLayout()
            infor_group_layout.setAlignment(QtCore.Qt.AlignTop)
            infor_group_layout.addWidget(self.qlabel_info_mouse_pos)
            infor_group_layout.addWidget(self.qlabel_info_mouse_rgb_value)
            infor_group_layout.addWidget(self.qlabel_info_wh)
            infor_group_layout.addWidget(self.qlabel_info_color_type)
            infor_group_layout.addWidget(self.qlabel_info_zoom_ration)
            infor_group_layout.addWidget(self.qlabel_info_exclude_names)
            self.info_group.setLayout(infor_group_layout)
            main_layout.addWidget(self.info_group, 30, 50, 15, 10)

            self.qview_bg_color = 'white'

            self.get_img_list()
            self.show_image(init=True)
        else:
            print('Unsupported file format.')
            sys.exit(1)

    def goto_button_clicked(self):
        goto_str = self.goto_edit.text()
        if goto_str == '':
            self.dirpos = 0
        elif goto_str.isdigit():
            self.dirpos = int(goto_str) - 1
        else:
            return
        self.key = os.path.join(self.path, self.imgfiles[self.dirpos])
        self.show_image()

    def get_img_list(self):
        if os.path.isdir(self.key):
            self.key = sorted(glob.glob(os.path.join(self.key, '*')))[0]

        # set label show
        if isinstance(self.exclude_names, list):
            show_str = 'Exclude:\n\t' + '\n\t'.join(self.exclude_names)
            self.qlabel_info_exclude_names.setStyleSheet(
                'QLabel {color : red;}')
        else:
            show_str = 'Exclude: None'
            self.qlabel_info_exclude_names.setStyleSheet(
                'QLabel {color : black;}')
        self.qlabel_info_exclude_names.setText(show_str)

        if self.key.endswith(FORMATS):
            # get image list
            self.path, self.img_name = os.path.split(self.key)
            self.imgfiles = []
            if self.path == '':
                self.path = './'
            for img_path in sorted(glob.glob(os.path.join(self.path, '*'))):
                img_name = os.path.split(img_path)[1]
                base, ext = os.path.splitext(img_name)
                if ext in FORMATS:
                    flag_add = True
                    if self.exclude_names is not None:
                        for exclude_name in self.exclude_names:
                            if exclude_name in base:
                                flag_add = False
                    if flag_add:
                        self.imgfiles.append(img_name)
            # natural sort
            self.imgfiles.sort(key=lambda s: [
                int(t) if t.isdigit() else t.lower()
                for t in re.split('(\d+)', s)
            ])
            # get current pos
            try:
                self.dirpos = self.imgfiles.index(self.img_name)
            except ValueError:
                # self.img_name may not in self.imgfiles after refreshing
                self.dirpos = 0
            # update information
            self.key = self.key.replace('\\', '/')
            self.qlabel_img_path.setText(f'{self.key}')

            # save open file history
            try:
                with open('history.txt', 'r') as f:
                    lines = f.readlines()
                    lines = [line.strip() for line in lines]
                    if len(lines) == 5:
                        del lines[-1]
            except Exception:
                lines = []
            # add the new records to the first line
            if self.key not in ['icon.png', './icon.png'] and (self.key
                                                               not in lines):
                lines.insert(0, self.key)
            with open('history.txt', 'w') as f:
                for line in lines:
                    f.write(f'{line}\n')
        else:
            raise ValueError('Wrong key!')
            exit(-1)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F9:
            self.toggle_bg_color()
        elif event.key() == QtCore.Qt.Key_R:
            self.qview.set_zoom(1)
        elif event.key() == QtCore.Qt.Key_Space:
            self.dir_browse(1)
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.dir_browse(-1)

    def keyReleaseEvent(self, event):
        # there is key focus problem, so we use KeyReleaseEvent
        if event.key() == QtCore.Qt.Key_Right:
            self.dir_browse(1)
        elif event.key() == QtCore.Qt.Key_Left:
            self.dir_browse(-1)
        elif event.key() == QtCore.Qt.Key_Up:
            self.qview.zoom_in()
        elif event.key() == QtCore.Qt.Key_Down:
            self.qview.zoom_out()

    def show_image(self, init=False):
        self.qscene.clear()
        self.qimg = QImage(self.key)
        self.qpixmap = QPixmap.fromImage(self.qimg)
        self.qscene.addPixmap(self.qpixmap)
        self.imgw, self.imgh = self.qpixmap.width(), self.qpixmap.height()
        # put image always in the center of a QGraphicsView
        self.qscene.setSceneRect(0, 0, self.imgw, self.imgh)
        self.key = self.key.replace('\\', '/')
        self.qlabel_img_path.setText(f'{self.key}')

        try:
            with Image.open(self.key) as lazy_img:
                self.color_type = lazy_img.mode
        except FileNotFoundError:
            print(f'Cannot open {self.key}')
            return 1

        # update information panel
        self.path, self.img_name = os.path.split(self.key)
        self.file_size = os.path.getsize(self.key) / 1024 / 1024  # in MB
        self.name_label.setText(
            f'[{self.dirpos + 1:d} / {len(self.imgfiles):d}] '
            f'{self.img_name}')
        self.info_label.setText(
            f'  {self.imgh:d} x {self.imgw:d}, {self.file_size:.2f} MB. '
            f'{self.color_type}')

        self.qlabel_info_wh.setText(
            f'\nImage size:\n  Height:\t{self.imgh:d}\n  Width:\t{self.imgw:d}'
        )

        if init:
            if self.imgw < 500:
                self.qview.set_zoom(500 // self.imgw)
            else:
                self.qview.set_zoom(1)
        self.qview.set_transform()

    def dir_browse(self, direc):
        if len(self.imgfiles) > 1:
            self.dirpos += direc
            if self.dirpos > (len(self.imgfiles) - 1):
                self.dirpos = 0
            elif self.dirpos < 0:
                self.dirpos = (len(self.imgfiles) - 1)
            self.key = os.path.join(self.path, self.imgfiles[self.dirpos])

            self.show_image()

    def toggle_bg_color(self):
        """Toggle background color."""
        if self.qview_bg_color == 'white':
            self.qview_bg_color = 'gray'
            self.qscene.setBackgroundBrush(QtCore.Qt.gray)
        else:
            self.qview_bg_color = 'white'
            self.qscene.setBackgroundBrush(QtCore.Qt.white)


class MainWindow(QMainWindow):
    """The main window."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('HandyView')
        self.init_menubar()
        self.init_toolbar()
        self.init_statusbar()
        self.init_central_window()
        # self.add_dock_window()

    def init_menubar(self):
        # create menubar
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(actions.open(self))
        file_menu.addAction(actions.refresh(self))
        file_menu.addAction(actions.exclude_file_name(self))
        file_menu.addAction(actions.history(self))

        # Edit
        edit_menu = menubar.addMenu('&Edit')

        # Draw
        draw_menu = menubar.addMenu('&Draw')

        # Compare
        compare_menu = menubar.addMenu('&Compare')
        compare_menu.addAction(actions.compare(self))

        # View
        self.view_menu = menubar.addMenu('&View')

        # Help
        help_menu = menubar.addMenu('&Help')

    def init_toolbar(self):
        self.toolbar = QToolBar(self)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addAction(actions.open(self))
        self.toolbar.addAction(actions.refresh(self))
        self.toolbar.addAction(actions.exclude_file_name(self))
        self.toolbar.addAction(actions.compare(self))
        self.toolbar.addAction(actions.history(self))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

    def init_statusbar(self):
        self.statusBar().showMessage('Ready')

    def init_central_window(self):
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)

    """
    def add_dock_window(self):
        # Tools
        dock_tool = QDockWidget('Tools', self)
        dock_tool.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea
                                  | QtCore.Qt.RightDockWidgetArea)
        label = QLabel('This is the first dock window.')
        dock_tool.setWidget(label)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_tool)

        # Info
        dock_info = QDockWidget('Info', self)
        dock_info.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea
                                  | QtCore.Qt.RightDockWidgetArea)
        label_info = QLabel('This is the info dock window.')
        dock_info.setWidget(label_info)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_info)

        # add to View menu bar
        self.view_menu.addAction(dock_tool.toggleViewAction())
        self.view_menu.addAction(dock_info.toggleViewAction())
    """

    ##################################
    # Slots
    ##################################

    def open_file_dialog(self):
        try:
            with open('history.txt', 'r') as f:
                history = f.readlines()[0]
                history = history.strip()
        except Exception:
            history = '.'
        key, ok = QFileDialog.getOpenFileName(self, 'Select an image', history)
        if ok:
            self.canvas.key = key
            self.canvas.get_img_list()
            self.canvas.show_image(init=True)

    def refresh_img_list(self):
        self.canvas.get_img_list()

    def open_history(self):
        with open('history.txt', 'r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
        key, ok = QInputDialog().getItem(self, 'Open File History', 'History:',
                                         lines, 0, True)
        if ok:
            self.canvas.key = key
            self.canvas.get_img_list()
            self.canvas.show_image(init=True)

    def exclude_file_name(self):
        exclude_names, ok = QInputDialog.getText(self, 'Exclude file name',
                                                 'Key word (seperate by ,):',
                                                 QLineEdit.Normal, '')
        if ok:
            if exclude_names != '':
                self.canvas.exclude_names = [
                    v.strip() for v in exclude_names.split(',')
                ]
            else:
                self.canvas.exclude_names = None
            self.canvas.get_img_list()
            self.canvas.show_image(init=False)


if __name__ == '__main__':
    import platform
    if platform.system() == 'Windows':
        # set the icon in the task bar
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            'HandyView')
    print('Welcom to HandyView.')

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.png'))

    screen = app.primaryScreen()
    print(f'Screen: {screen.name()}')
    size = screen.size()
    # rect = screen.availableGeometry()

    main = MainWindow()
    main.setGeometry(0, 0, size.width(),
                     size.height())  # (left, top, width, height)
    main.showMaximized()
    sys.exit(app.exec_())
