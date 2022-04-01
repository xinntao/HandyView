import os
import scipy  # noqa: F401 # used in imagehash.py -> import scipy.fftpack
import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QDockWidget, QFileDialog, QGridLayout, QInputDialog, QLabel, QLineEdit,
                             QMainWindow, QTabWidget, QToolBar, QVBoxLayout, QWidget)

import handyview.actions as actions
from handyview.canvas import Canvas
from handyview.canvas_crop import CanvasCrop
from handyview.db import HVDB
from handyview.utils import ROOT_DIR
from handyview.widgets import HLine, MessageDialog, show_msg


class CenterWidget(QWidget):

    def __init__(self, parent, hvdb):
        super().__init__()
        self.parent = parent
        # create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        tabs = QTabWidget()

        self.canvas = Canvas(self, hvdb)
        self.canvas_crop = CanvasCrop(self, hvdb)
        tabs.addTab(self.canvas, 'View')
        tabs.addTab(self.canvas_crop, 'Crop')
        layout.addWidget(tabs)

    def switch_fullscreen(self):
        self.parent.switch_fullscreen()

    def set_statusbar(self, text):
        self.parent.set_statusbar(text)


class MainWindow(QMainWindow):
    """The main window."""

    def __init__(self):
        super(MainWindow, self).__init__()
        # get initial path
        try:
            init_path = sys.argv[1]
        except IndexError:
            # show the icon image
            init_path = os.path.join(ROOT_DIR, 'icon.png')
        # initialize HVDB (handyview database), which stores the path info
        self.hvdb = HVDB(init_path)

        self.full_screen = False
        self.canvas_type = 'main'
        self.center_canvas = CenterWidget(self, self.hvdb)

        # initialize UI
        self.setWindowTitle('HandyView')
        self.init_menubar()
        self.init_toolbar()
        # self.init_statusbar()
        self.init_central_window()
        self.add_dock_window()

    def init_menubar(self):
        # create menubar
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(actions.open(self))
        file_menu.addAction(actions.history(self))
        file_menu.addSeparator()
        file_menu.addAction(actions.refresh(self))
        file_menu.addAction(actions.goto_index(self))
        file_menu.addSeparator()
        file_menu.addAction(actions.include_file_name(self))
        file_menu.addAction(actions.exclude_file_name(self))

        # Edit
        edit_menu = menubar.addMenu('&Edit')  # noqa: F841

        # Draw
        draw_menu = menubar.addMenu('&Draw')  # noqa: F841

        # Compare
        compare_menu = menubar.addMenu('&Compare')
        compare_menu.addAction(actions.compare(self))
        compare_menu.addAction(actions.clear_compare(self))
        compare_menu.addAction(actions.set_fingerprint(self))

        # Layouts
        layout_menu = menubar.addMenu('&Layout')
        layout_menu.addAction(actions.switch_main_canvas(self))
        layout_menu.addAction(actions.switch_compare_canvas(self))
        layout_menu.addAction(actions.switch_preview_canvas(self))

        # View
        layout_menu = menubar.addMenu('&View')
        layout_menu.addAction(actions.auto_zoom_dialog(self))

        # Help
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(actions.show_instruction_msg(self))

    def init_toolbar(self):
        self.toolbar = QToolBar('ToolBar', self)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # open and history
        self.toolbar.addAction(actions.open(self))
        self.toolbar.addAction(actions.history(self))
        self.toolbar.addSeparator()
        # refresh and index
        self.toolbar.addAction(actions.refresh(self))
        self.toolbar.addAction(actions.goto_index(self))
        self.toolbar.addSeparator()
        # include and exclude names
        self.toolbar.addAction(actions.include_file_name(self))
        self.toolbar.addAction(actions.exclude_file_name(self))
        self.toolbar.addSeparator()
        # compare and clear compare
        self.toolbar.addAction(actions.compare(self))
        self.toolbar.addAction(actions.clear_compare(self))

        # canvas layout
        self.toolbar.addSeparator()
        self.toolbar.addSeparator()
        self.toolbar.addAction(actions.switch_main_canvas(self))
        self.toolbar.addAction(actions.switch_compare_canvas(self))
        self.toolbar.addAction(actions.switch_preview_canvas(self))

        # others
        self.toolbar.addSeparator()
        self.toolbar.addAction(actions.set_fingerprint(self))

        # help
        self.toolbar.addSeparator()
        self.toolbar.addSeparator()
        self.toolbar.addAction(actions.show_instruction_msg(self))

        # auto zoom
        self.toolbar.addAction(actions.auto_zoom(self))

        self.toolbar.setIconSize(QtCore.QSize(45, 45))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

    def init_statusbar(self):
        self.statusBar().showMessage('Welcome to HandyView.')

    def set_statusbar(self, text):
        self.statusBar().showMessage(text)

    def init_central_window(self):
        self.setCentralWidget(self.center_canvas)

    def switch_fullscreen(self):
        if self.full_screen is False:
            self.showFullScreen()
            self.full_screen = True
        else:
            self.showMaximized()
            self.full_screen = False

    def add_dock_window(self):
        # Info
        self.dock_info = QDockWidget('Information Panel', self)
        self.dock_info.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dock_info.setFeatures(QDockWidget.DockWidgetMovable
                                   | QDockWidget.DockWidgetFloatable
                                   | QDockWidget.DockWidgetClosable)
        dockedWidget = QWidget()
        self.dock_info.setWidget(dockedWidget)
        layout = QGridLayout()
        layout.addWidget(self.center_canvas.canvas.zoom_label, 0, 0, 1, 3)
        layout.addWidget(self.center_canvas.canvas.mouse_pos_label, 1, 0, 1, 3)
        color_grid = QGridLayout()
        color_grid.addWidget(self.center_canvas.canvas.mouse_color_title, 0, 0, 1, 1)
        color_grid.addWidget(self.center_canvas.canvas.mouse_color_label, 0, 1, 1, 3)
        color_grid.addWidget(self.center_canvas.canvas.mouse_rgb_label, 1, 0, 1, 3)
        layout.addLayout(color_grid, 2, 0, 1, 3)
        layout.addWidget(HLine(), 3, 0, 1, 3)
        layout.addWidget(self.center_canvas.canvas.selection_pos_label, 4, 0, 1, 3)
        layout.addWidget(HLine(), 5, 0, 1, 3)
        layout.addWidget(self.center_canvas.canvas.include_names_label, 6, 0, 1, 3)
        layout.addWidget(self.center_canvas.canvas.exclude_names_label, 7, 0, 1, 3)
        layout.addWidget(HLine(), 8, 0, 1, 3)
        layout.addWidget(self.center_canvas.canvas.comparison_label, 9, 0, 1, 3)
        # update comparison info (for a second open)
        _, img_len_list = self.hvdb.update_path_list()
        show_str = 'Comparison:\n # for each folder:\n\t' + '\n\t'.join(map(str, img_len_list))
        if len(img_len_list) > 1:
            self.center_canvas.canvas.comparison_label.setText(show_str)

        # for compact space
        blank_qlabel = QLabel()
        layout.addWidget(blank_qlabel, 10, 0, 20, 3)
        dockedWidget.setLayout(layout)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_info)

    # ---------------------------------------
    # slots: open and history
    # ---------------------------------------
    def open_file_dialog(self):
        try:
            with open(os.path.join(ROOT_DIR, 'history.txt'), 'r') as f:
                history = f.readlines()[0]
                history = history.strip()
        except Exception:
            history = '.'
        key, ok = QFileDialog.getOpenFileName(self, 'Select an image', history)
        if ok:
            self.hvdb.init_path = key
            self.hvdb.get_init_path_list()
            self.center_canvas.canvas.show_image(init=True)

    def open_history(self):
        with open(os.path.join(ROOT_DIR, 'history.txt'), 'r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
        key, ok = QInputDialog().getItem(self, 'Open File History', 'History:', lines, 0, True)
        if ok:
            self.hvdb.init_path = key
            self.hvdb.get_init_path_list()
            self.center_canvas.canvas.show_image(init=True)

    # ---------------------------------------
    # slots: refresh and index
    # ---------------------------------------
    def refresh_img_list(self):
        # should be used in Main Cavans
        if self.canvas_type != 'main':
            self.switch_main_canvas()

        self.center_canvas.canvas.update_path_list()
        self.center_canvas.canvas.show_image(init=False)

    def goto_index(self):
        index, ok = QInputDialog.getText(self, 'Go to index', 'Index:', QLineEdit.Normal, '1')
        if ok:
            if index == '':
                index = 0
            elif index.isdigit():
                index = int(index) - 1
            else:
                return
            self.center_canvas.canvas.goto_index(index)

    # ---------------------------------------
    # slots: include and exclude names
    # ---------------------------------------
    def include_file_name(self):
        # show current include names as the default values
        current_include_names = self.hvdb.include_names
        if current_include_names is None:
            current_include_names = ''
        else:
            current_include_names = ', '.join(current_include_names)

        include_names, ok = QInputDialog.getText(self, 'Include file name', 'Key word (seprate by ,):',
                                                 QLineEdit.Normal, current_include_names)
        if ok:
            if include_names != '':
                self.hvdb.include_names = [v.strip() for v in include_names.split(',')]
                self.hvdb.exclude_names = None
            else:
                self.hvdb.include_names = None
            self.refresh_img_list()

    def exclude_file_name(self):
        # show current exclude names as the default values
        current_exclude_names = self.hvdb.exclude_names
        if current_exclude_names is None:
            current_exclude_names = ''
        else:
            current_exclude_names = ', '.join(current_exclude_names)

        exclude_names, ok = QInputDialog.getText(self, 'Exclude file name', 'Key word (seprate by ,):',
                                                 QLineEdit.Normal, current_exclude_names)
        if ok:
            if exclude_names != '':
                self.hvdb.exclude_names = [v.strip() for v in exclude_names.split(',')]
                self.hvdb.include_names = None
            else:
                self.hvdb.exclude_names = None
            self.refresh_img_list()

    # ---------------------------------------
    # slots: compare and clear compare
    # ---------------------------------------
    def compare_folder(self):
        # Compare folder should be set in Main Cavans
        if self.canvas_type != 'main':
            self.switch_main_canvas()

        key, ok = QFileDialog.getOpenFileName(self, 'Select an image', os.path.join(self.hvdb.get_folder(), '../'))
        if ok:
            self.center_canvas.canvas.add_cmp_folder(key)

    def clear_compare(self):
        # Compare folder should be set in Main Cavans
        if self.canvas_type != 'main':
            self.switch_main_canvas()

        self.hvdb.folder_list = [self.hvdb.folder_list[0]]
        self.hvdb.path_list = [self.hvdb.path_list[0]]
        self.hvdb.fidx = 0
        # clear the text description in the dock window
        self.center_canvas.canvas.update_path_list()

    # ---------------------------------------
    # slots: canvas layouts
    # ---------------------------------------

    def switch_main_canvas(self):
        if self.canvas_type != 'main':
            self.hvdb.interval = 0
            self.center_canvas.canvas = Canvas(self, self.hvdb)
            self.setCentralWidget(self.center_canvas.canvas)
            self.add_dock_window()
            self.canvas_type = 'main'

    def switch_compare_canvas(self):
        if self.canvas_type != 'compare':
            num_compare = self.hvdb.get_folder_len()
            if num_compare == 1:
                num_view, ok = QInputDialog.getText(self, 'Compare Canvas', '# Compare Columns: (options: 2, 3, 4)',
                                                    QLineEdit.Normal, '2')
                if ok:
                    try:
                        num_view = int(num_view)
                    except Exception:
                        show_msg(icon='Warning', title='Warning', text='# Compare Columns should be int.')
                    if num_view > 4 or num_view < 2:
                        show_msg(icon='Warning', title='Warning', text='# Compare Columns should be 2, 3, 4.')
                    self.hvdb.interval = num_view - 1
                else:  # when press the 'Cancellation' button
                    self.hvdb.interval = 1
                    num_view = 1
            else:  # for comparing mode
                if not self.hvdb.is_same_len:
                    show_msg('Critical', 'Warning', ('Compare folders have different length, \n'
                                                     'It may introduce misalignment and errors.'))
                self.hvdb.fidx = 0
                num_view = min(self.hvdb.get_folder_len(), 4)
                show_msg('Information', 'Compare Canvas', f'Comparsion folder mode.\n # Compare Columns: {num_view}.')

            if num_view > 1:
                self.dock_info.close()
                self.center_canvas.canvas = Canvas(self, self.hvdb, num_view=num_view)
                self.setCentralWidget(self.center_canvas.canvas)
                self.canvas_type = 'compare'

    def switch_preview_canvas(self):
        show_msg('Information', '^_^', text=('Has not implemented yet.\n' 'Contributions are welcome!\n' '尚未实现, 欢迎贡献!'))

    # ---------------------------------------
    # slots: help
    # ---------------------------------------

    def show_instruction_msg(self):
        from handyview.instruction_text import instruct_text, instruct_text_cn
        msg = MessageDialog(self, instruct_text, instruct_text_cn)
        # msg.setStyleSheet('QLabel{min-width:500 px; font-size: 20px;}')
        msg.setWindowTitle('Instructions')
        msg.exec_()

    def set_fingerprint(self):
        if self.center_canvas.canvas.show_fingerprint:
            self.center_canvas.canvas.show_fingerprint = False
        else:
            self.center_canvas.canvas.show_fingerprint = True
        self.center_canvas.canvas.show_image()

    # ---------------------------------------
    # slots: auto zoom
    # ---------------------------------------
    def auto_zoom(self):
        target_zoom_width = self.center_canvas.canvas.qimg.width() * self.center_canvas.canvas.qviews[0].zoom
        self.center_canvas.canvas.target_zoom_width = int(target_zoom_width)

    def auto_zoom_dialog(self):
        target_zoom_width = self.center_canvas.canvas.qimg.width() * self.center_canvas.canvas.qviews[0].zoom
        target_zoom_width, ok = QInputDialog.getText(self, 'Auto Zoom', 'Fix image width: (0 for cancelling auto zoom)',
                                                     QLineEdit.Normal, str(int(target_zoom_width)))
        if ok:
            self.center_canvas.canvas.target_zoom_width = int(target_zoom_width)


if __name__ == '__main__':
    import platform
    if platform.system() == 'Windows':
        # set the icon in the task bar
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('HandyView')
    print('Welcome to HandyView.')

    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    # rect = screen.availableGeometry()

    mainwindow = MainWindow()
    mainwindow.setWindowIcon(QIcon(os.path.join(ROOT_DIR, 'icon.ico')))
    mainwindow.setGeometry(0, 0, size.width(), size.height())  # (left, top, width, height)
    mainwindow.showMaximized()
    # change status bar info
    # mainwindow.set_statusbar(f'Screen: {screen.name()} with size {size.width()} x {size.height()}.')

    sys.exit(app.exec_())
