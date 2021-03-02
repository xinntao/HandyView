import actions as actions
import os
import sys
from canvas import Canvas, CanvasCompare
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QDockWidget, QFileDialog,
                             QGridLayout, QInputDialog, QLabel, QLineEdit,
                             QMainWindow, QToolBar, QWidget)
from widgets import HLine, MessageDialog

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    CURRENT_PATH = sys._MEIPASS
else:
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


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
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(actions.show_instruction_msg(self))

    def init_toolbar(self):
        self.toolbar = QToolBar(self)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addAction(actions.open(self))
        self.toolbar.addAction(actions.refresh(self))
        self.toolbar.addAction(actions.include_file_name(self))
        self.toolbar.addAction(actions.exclude_file_name(self))
        self.toolbar.addAction(actions.compare(self))
        self.toolbar.addAction(actions.history(self))
        # canvas layout
        self.toolbar.addSeparator()
        self.toolbar.addAction(actions.switch_main_canvas(self))
        self.toolbar.addAction(actions.switch_compare_canvas(self))
        self.toolbar.addAction(actions.switch_preview_canvas(self))
        # instructions
        self.toolbar.addSeparator()
        self.toolbar.addSeparator()
        self.toolbar.addAction(actions.show_instruction_msg(self))

        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

    def init_statusbar(self):
        self.statusBar().showMessage('Welcome to HandyView.')

    def set_statusbar(self, text):
        self.statusBar().showMessage(text)

    def init_central_window(self):
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)

    def add_dock_window(self):
        # Info
        self.dock_info = QDockWidget('Information Panel', self)
        self.dock_info.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea
                                       | QtCore.Qt.RightDockWidgetArea)
        # not show close button
        self.dock_info.setFeatures(QDockWidget.DockWidgetMovable
                                   | QDockWidget.DockWidgetFloatable
                                   | QDockWidget.DockWidgetClosable)
        dockedWidget = QWidget()
        self.dock_info.setWidget(dockedWidget)
        layout = QGridLayout()
        layout.addWidget(self.canvas.info_label, 0, 0, 1, 3)
        layout.addWidget(self.canvas.zoom_label, 1, 0, 1, 3)
        layout.addWidget(self.canvas.mouse_pos_label, 2, 0, 1, 3)
        color_grid = QGridLayout()
        color_grid.addWidget(self.canvas.mouse_color_title, 0, 0, 1, 1)
        color_grid.addWidget(self.canvas.mouse_color_label, 0, 1, 1, 3)
        color_grid.addWidget(self.canvas.mouse_rgb_label, 1, 0, 1, 3)
        layout.addLayout(color_grid, 3, 0, 1, 3)
        layout.addWidget(HLine(), 4, 0, 1, 3)
        layout.addWidget(self.canvas.selection_pos_label, 5, 0, 1, 3)
        layout.addWidget(HLine(), 6, 0, 1, 3)
        layout.addWidget(self.canvas.include_names_label, 7, 0, 1, 3)
        layout.addWidget(self.canvas.exclude_names_label, 8, 0, 1, 3)
        layout.addWidget(self.canvas.comparison_label, 9, 0, 1, 3)

        # for compact space
        blank_qlabel = QLabel()
        layout.addWidget(blank_qlabel, 7, 0, 20, 3)
        dockedWidget.setLayout(layout)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_info)

    # ---------------------------------------
    # Canvas Slots
    # ---------------------------------------
    def switch_main_canvas(self):
        self.setCentralWidget(self.canvas)

    def switch_compare_canvas(self):
        self.dock_info.close()
        self.canvas_compare = CanvasCompare(self, num_scene=2)
        self.setCentralWidget(self.canvas_compare)

    def switch_preview_canvas(self):
        self.dock_info.close()
        self.canvas_compare = CanvasCompare(self, num_scene=3)
        self.setCentralWidget(self.canvas_compare)

    # --------
    # Slots
    # --------

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
            self.canvas.get_main_img_list()
            self.canvas.show_image(init=True)

    def refresh_img_list(self):
        self.canvas.get_main_img_list()
        self.canvas.show_image(init=False)
        # TODO: update comparison image list

    def compare_folder(self):
        key, ok = QFileDialog.getOpenFileName(
            self, 'Select an image', os.path.join(self.canvas.path, '../'))
        if ok:
            self.canvas.update_cmp_img_list(key)

    def open_history(self):
        with open(os.path.join(CURRENT_PATH, 'history.txt'), 'r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
        key, ok = QInputDialog().getItem(self, 'Open File History', 'History:',
                                         lines, 0, True)
        if ok:
            self.canvas.key = key
            self.canvas.get_main_img_list()
            self.canvas.show_image(init=True)

    def exclude_file_name(self):
        # show current exclude names as the default values
        current_exclude_names = self.canvas.exclude_names
        if current_exclude_names is None:
            current_exclude_names = ''
        else:
            current_exclude_names = ', '.join(current_exclude_names)

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
            self.refresh_img_list()

        # show exclude names in the information panel
        if isinstance(self.canvas.exclude_names, list):
            show_str = 'Exclude:\n\t' + '\n\t'.join(self.canvas.exclude_names)
            self.canvas.exclude_names_label.setStyleSheet(
                'QLabel {color : red;}')
        else:
            show_str = 'Exclude: None'
            self.canvas.exclude_names_label.setStyleSheet(
                'QLabel {color : black;}')
        self.canvas.exclude_names_label.setText(show_str)

    def include_file_name(self):
        # show current include names as the default values
        current_include_names = self.canvas.include_names
        if current_include_names is None:
            current_include_names = ''
        else:
            current_include_names = ', '.join(current_include_names)

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
            self.refresh_img_list()

        # show include names in the information panel
        if isinstance(self.canvas.include_names, list):
            show_str = 'Include:\n\t' + '\n\t'.join(self.canvas.include_names)
            self.canvas.include_names_label.setStyleSheet(
                'QLabel {color : blue;}')
        else:
            show_str = 'Include: None'
            self.canvas.include_names_label.setStyleSheet(
                'QLabel {color : black;}')
        self.canvas.include_names_label.setText(show_str)

    def show_instruction_msg(self):
        instruct_text = r'''
        Mouse wheel : Previous/Next image
        Ctrl + Mouse wheel: Zoom in/out

        A D: Previous/Next image
        W S: Zoom in/out
        Direction key ← → : Horizontal scrolling
        Direction key ↑ ↓ : Vertical scrolling
        F9 : Change background color (white or gray)
        R : Reset zoom ration to 1
        Space : Next image
        Backspace: Previous image
        '''
        instruct_text_cn = r'''
        鼠标滚轮 : 上一张/下一张 图像
        Ctrl + 鼠标滚轮: 放大/缩小

        A D: 上一张/下一张 图像
        W S: 放大/缩小
        方向键 ← → : 水平滚动
        方向键 ↑ ↓ : 垂直滚动
        F9 : 切换背景颜色 (白色/灰色)
        R : 重置放大比率为1
        Space : 下一张 图像
        Backspace: 上一张 图像
        '''
        msg = MessageDialog(self, instruct_text, instruct_text_cn)
        msg.setStyleSheet('QLabel{min-width:500 px; font-size: 20px;}')
        msg.setWindowTitle('Instructions')
        msg.exec_()


if __name__ == '__main__':
    import platform
    if platform.system() == 'Windows':
        # set the icon in the task bar
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            'HandyView')
    print('Welcome to HandyView.')

    app = QApplication(sys.argv)

    screen = app.primaryScreen()
    size = screen.size()
    # rect = screen.availableGeometry()

    main = MainWindow()
    main.setWindowIcon(QIcon('icon.ico'))
    main.setGeometry(0, 0, size.width(),
                     size.height())  # (left, top, width, height)
    main.showMaximized()

    # change status bar info
    main.set_statusbar(
        f'Screen: {screen.name()} with size {size.width()} x {size.height()}.')
    sys.exit(app.exec_())
