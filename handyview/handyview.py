import actions as actions
import glob
import os
import re
import sys
from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QDockWidget, QFileDialog,
                             QGridLayout, QInputDialog, QLabel, QLineEdit,
                             QMainWindow, QPushButton, QToolBar, QWidget)
from view_scene import HVScene, HVView
from widgets import ColorLabel, HLine, HVLable

FORMATS = ('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.ppm', '.PPM',
           '.bmp', '.BMP', '.gif', '.GIF', 'tiff')

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    CURRENT_PATH = sys._MEIPASS
else:
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class Canvas(QWidget):
    """The main canvas to show the image, information panel."""

    def __init__(self, parent):
        super(Canvas, self).__init__()
        try:
            self.key = sys.argv[1]
        except IndexError:
            self.key = os.path.join(CURRENT_PATH,
                                    'icon.png')  # show the icon image

        self.include_names = None
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
            self.qscene = HVScene(self)
            self.qview = HVView(self.qscene, self)

            # goto edit and botton
            self.goto_edit = QLineEdit()
            self.goto_edit.setPlaceholderText('Index. Default: 1')
            goto_btn = QPushButton('GO', self)
            goto_btn.clicked.connect(self.goto_button_clicked)
            # name label showing image index and image path
            self.name_label = HVLable('', self, 'green', 'Times', 15)

            # info label showing image shape, size and color type
            self.info_label = QLabel(self)
            self.info_label.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.info_label.setStyleSheet('QLabel {color : blue;}')
            self.info_label.setFont(QFont('Times', 12))
            # zoom label showing zoom ratio
            self.qlabel_info_zoom_ration = QLabel(self)  # zoom ratio
            self.qlabel_info_zoom_ration.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_info_zoom_ration.setStyleSheet(
                'QLabel {color : green;}')
            self.qlabel_info_zoom_ration.setFont(QFont('Times', 12))
            # mouse position and mouse rgb value
            self.qlabel_info_mouse_pos = QLabel(self)
            self.qlabel_info_mouse_pos.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_info_mouse_pos.setFont(QFont('Times', 12))
            self.qlabel_info_mouse_pos.setText(
                'Cursor position:\n (ignore zoom)\n'
                ' Height(y): 0.0\n Width(x):  0.0')
            self.qlabel_info_mouse_rgb_value = QLabel(self)
            self.qlabel_info_mouse_rgb_value.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_info_mouse_rgb_value.setFont(QFont('Times', 12))
            self.qlabel_info_mouse_rgb_value.setText(' (255, 255, 255, 255)')
            # pixel color at the mouse position
            self.qlable_color_title = QLabel('RGBA:', self)
            self.qlable_color_title.setFont(QFont('Times', 12))
            self.qlabel_color = ColorLabel(color=(255, 255, 255))

            # include and exclude names
            self.qlabel_info_include_names = QLabel(self)
            self.qlabel_info_include_names.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_info_include_names.setFont(QFont('Times', 12))
            self.qlabel_info_exclude_names = QLabel(self)
            self.qlabel_info_exclude_names.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_info_exclude_names.setFont(QFont('Times', 12))

            # draw rectangle position and length
            self.qlabel_rect_pos = QLabel(self)
            self.qlabel_rect_pos.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse)
            self.qlabel_rect_pos.setFont(QFont('Times', 12))
            self.qlabel_rect_pos.setText('Rect Pos: (H, W)\n Top-Left: 0, 0\n'
                                         ' Btm-Rite: 0, 0\n Length  : 0, 0')
            # layeouts
            info_grid = QGridLayout()
            # int row, int column, int rowSpan, int columnSpan
            info_grid.addWidget(self.goto_edit, 0, 0, 1, 1)
            info_grid.addWidget(goto_btn, 0, 1, 1, 1)
            main_layout.addWidget(self.name_label, 0, 0, 1, 50)
            main_layout.addLayout(info_grid, 1, 0, 1, 10)

            # main view
            main_layout.addWidget(self.qview, 0, 0, -1, 50)
            # bottom QLabel, show image path
            self.qlabel_img_path = QLabel(self)
            main_layout.addWidget(self.qlabel_img_path, 61, 0, 1, 50)

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
        if isinstance(self.include_names, list):
            show_str = 'Include:\n\t' + '\n\t'.join(self.include_names)
            self.qlabel_info_include_names.setStyleSheet(
                'QLabel {color : blue;}')
        else:
            show_str = 'Include: None'
            self.qlabel_info_include_names.setStyleSheet(
                'QLabel {color : black;}')
        self.qlabel_info_include_names.setText(show_str)

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
                    if self.include_names is not None:
                        flag_add = False
                        for include_name in self.include_names:
                            if include_name in base:
                                flag_add = True
                    elif self.exclude_names is not None:
                        flag_add = True
                        for exclude_name in self.exclude_names:
                            if exclude_name in base:
                                flag_add = False
                    else:
                        flag_add = True

                    if flag_add:
                        self.imgfiles.append(img_name)
            # natural sort
            self.imgfiles.sort(key=lambda s: [
                int(t) if t.isdigit() else t.lower()
                for t in re.split(r'(\d+)', s)
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
                with open(os.path.join(CURRENT_PATH, 'history.txt'), 'r') as f:
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
            with open(os.path.join(CURRENT_PATH, 'history.txt'), 'w') as f:
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
            f'Info: \n'
            f' Height: {self.imgh:d}\n Width:  {self.imgw:d}\n'
            f' Size: {self.file_size:.2f} MB\n Type: {self.color_type}')

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
        self.add_dock_window()

    def init_menubar(self):
        # create menubar
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(actions.open(self))
        file_menu.addAction(actions.refresh(self))
        file_menu.addAction(actions.include_file_name(self))
        file_menu.addAction(actions.exclude_file_name(self))
        file_menu.addAction(actions.history(self))

        # Edit
        edit_menu = menubar.addMenu('&Edit')  # noqa: F841

        # Draw
        draw_menu = menubar.addMenu('&Draw')  # noqa: F841

        # Compare
        compare_menu = menubar.addMenu('&Compare')
        compare_menu.addAction(actions.compare(self))

        # View
        self.view_menu = menubar.addMenu('&View')

        # Help
        help_menu = menubar.addMenu('&Help')  # noqa: F841

    def init_toolbar(self):
        self.toolbar = QToolBar(self)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addAction(actions.open(self))
        self.toolbar.addAction(actions.refresh(self))
        self.toolbar.addAction(actions.include_file_name(self))
        self.toolbar.addAction(actions.exclude_file_name(self))
        self.toolbar.addAction(actions.compare(self))
        self.toolbar.addAction(actions.history(self))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

    def init_statusbar(self):
        self.statusBar().showMessage('Ready')

    def init_central_window(self):
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)

    def add_dock_window(self):
        # Info
        dock_info = QDockWidget('Information Panel', self)
        dock_info.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea
                                  | QtCore.Qt.RightDockWidgetArea)
        dock_info.setFeatures(QDockWidget.DockWidgetMovable
                              | QDockWidget.DockWidgetFloatable)
        dockedWidget = QWidget()
        dock_info.setWidget(dockedWidget)
        layout = QGridLayout()
        layout.addWidget(self.canvas.info_label, 0, 0, 1, 3)
        layout.addWidget(self.canvas.qlabel_info_zoom_ration, 1, 0, 1, 3)
        layout.addWidget(self.canvas.qlabel_info_mouse_pos, 2, 0, 1, 3)
        # layout.addWidget(self.canvas.info_label)
        # layout.addWidget(self.canvas.qlabel_info_zoom_ration)
        # layout.addWidget(self.canvas.qlabel_info_mouse_pos)
        color_grid = QGridLayout()
        color_grid.addWidget(self.canvas.qlable_color_title, 0, 0, 1, 1)
        color_grid.addWidget(self.canvas.qlabel_color, 0, 1, 1, 3)
        color_grid.addWidget(self.canvas.qlabel_info_mouse_rgb_value, 1, 0, 1,
                             3)
        layout.addLayout(color_grid, 3, 0, 1, 3)
        layout.addWidget(HLine(), 4, 0, 1, 3)
        layout.addWidget(self.canvas.qlabel_rect_pos, 5, 0, 1, 3)
        layout.addWidget(HLine(), 6, 0, 1, 3)
        layout.addWidget(self.canvas.qlabel_info_include_names, 7, 0, 1, 3)
        layout.addWidget(self.canvas.qlabel_info_exclude_names, 8, 0, 1, 3)

        blank_qlabel = QLabel()
        layout.addWidget(blank_qlabel, 7, 0, 20, 3)
        dockedWidget.setLayout(layout)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_info)

    ##################################
    # Slots
    ##################################

    def open_file_dialog(self):
        try:
            with open(os.path.join(CURRENT_PATH, 'history.txt'), 'r') as f:
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
        with open(os.path.join(CURRENT_PATH, 'history.txt'), 'r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
        key, ok = QInputDialog().getItem(self, 'Open File History', 'History:',
                                         lines, 0, True)
        if ok:
            self.canvas.key = key
            self.canvas.get_img_list()
            self.canvas.show_image(init=True)

    def exclude_file_name(self):
        # show current exclude names as the default values
        current_exclude_names = self.canvas.exclude_names
        if current_exclude_names is None:
            current_exclude_names = ''
        else:
            current_exclude_names = ', '.join(current_exclude_names)
            current_exclude_names += ', '

        exclude_names, ok = QInputDialog.getText(self, 'Exclude file name',
                                                 'Key word (seperate by ,):',
                                                 QLineEdit.Normal,
                                                 current_exclude_names)
        if ok:
            if exclude_names != '':
                self.canvas.exclude_names = [
                    v.strip() for v in exclude_names.split(',')
                ]
                self.canvas.include_names = None
            else:
                self.canvas.exclude_names = None
            self.canvas.get_img_list()
            self.canvas.show_image(init=False)

    def include_file_name(self):
        # show current include names as the default values
        current_include_names = self.canvas.include_names
        if current_include_names is None:
            current_include_names = ''
        else:
            current_include_names = ', '.join(current_include_names)
            current_include_names += ', '

        include_names, ok = QInputDialog.getText(self, 'Include file name',
                                                 'Key word (seperate by ,):',
                                                 QLineEdit.Normal,
                                                 current_include_names)
        if ok:
            if include_names != '':
                self.canvas.include_names = [
                    v.strip() for v in include_names.split(',')
                ]
                self.canvas.exclude_names = None
            else:
                self.canvas.include_names = None
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
    app.setWindowIcon(QIcon('icon.icon'))

    screen = app.primaryScreen()
    print(f'Screen: {screen.name()}')
    size = screen.size()
    # rect = screen.availableGeometry()

    main = MainWindow()
    main.setWindowIcon(QIcon('icon.ico'))
    main.setGeometry(0, 0, size.width(),
                     size.height())  # (left, top, width, height)
    main.showMaximized()
    sys.exit(app.exec_())
