import os
import sys
import platform  # for windows task bar
import ctypes  # for windows task bar

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QDockWidget, QFileDialog,
                             QGridLayout, QInputDialog, QLabel, QLineEdit,
                             QMainWindow, QToolBar, QWidget,)

from handyview.canvas import Canvas
from handyview.db import HVDB
from handyview.utils import ROOT_DIR, FORMATS
from handyview.widgets import HLine, MessageDialog, show_msg, HAction
from handyview.preview import SettingsDialog, PreviewWidget


version = '0.4.3'

windowTitle = f'HandyView v{version}'


class MainWindow(QMainWindow):
    """Summary

    Attributes:
        canvas (handyview.Canvas)
        canvas_type (str or None): 'main' or 'compare' or 'preview' or None
        columns (int): number of columns in the preview ↑ columns ↓ thumbnail size
        dockWidget (QDockWidget): info panel
        fresh (bool): True if self.preview_area_width has not been set
        preview_area_width (TYPE): width of the thumbnail area
        hvdb (handyview.HVDB)
        is_full_screen (bool)
        fast_zoom (bool)
        previewWidget (PreviewWidget): instanse of QWidget → thumbnail area
        root_path (TYPE):
        screen (TYPE):
        thumbnails_in_memory (bool): if True, thumbnails will be calculated in memory and will not be cached; False by default
        toolbar (QToolbar)
        windowTitle (str)
    """

    def __init__(self, screen):
        super(MainWindow, self).__init__()
        # get initial path
        try:
            self.root_path = sys.argv[1]
        except IndexError:
            # show the icon image
            self.root_path = os.path.join(ROOT_DIR)
        # initialize HVDB (handyview database), which stores the path info
        # ~ self.hvdb = HVDB(self.root_path)
        self.hvdb = None

        self.screen = screen
        self.is_full_screen = False
        self.canvas_type = None
        self.dockWidget = None

        self.just_started = True
        # for some weird reason self.centralWidget().size().width() returns inconsistent (often much lower) int than actual → getting width once, which will be always work for the screen on the current machine
        self.fresh = True  # means initial image has not been loaded and centralWidget size has not been set and can't yet get actual centralWidget size
        self.preview_area_width = None  # width of the central widget used in scaling thumbnails

        # initialize UI
        self.__init_actions()
        self.__init_menubar()
        self.__init_toolbar()
        self.__init_statusbar()
        self.__init_settings()
        self.setCentralWidget(QWidget())
        self.__init_screen_size()

        self.setWindowTitle(windowTitle)
        self.setWindowIcon(QIcon('icon.ico'))
        self.showMaximized()

    ### initializing gui ###

    def __init_actions(self):
        self.openAction = HAction(self,
                                  'Open',
                                  'open.png',
                                  shortcut='Ctrl+O',
                                  connected=self.open_file_dialog)
        # ~ self.historyAction = HAction(self, 'History', 'history.png',   # not used → disabled, but kept for reference
        # ~                              connected=self.open_history)
        self.refreshAction = HAction(self,
                                     'Refresh',
                                     'refresh.png',
                                     shortcut='F5',
                                     connected=self.refresh_img_list)

        self.goToIndexAction = HAction(self,
                                       'Go to\nImage\nIndex',
                                       'index.png',
                                       shortcut='Ctrl+I',
                                       connected=self.goto_index)
        # include and exclude names
        self.includeFileNamesAction = HAction(self,
                                              'Include Files',
                                              'include.png',
                                              connected=self.include_file_name)

        self.excludeFileNamesAction = HAction(self, 'Exclude Files', 'exclude.png',
                                              connected=self.exclude_file_name)
        # compare and clear compare
        self.compareAction = HAction(self,
                                     'Add\nComparison\nFolder',
                                     'compare.png',
                                     shortcut='F6',
                                     connected=self.compare_folder)
        self.clearCompareAction = HAction(self,
                                          'Clear\nComparison\nFolders',
                                          'clear_comparison.png',
                                          connected=self.clear_compare)
        # canvas layouts
        self.switchMainCanvasAction = HAction(self,
                                              'Main\nView',
                                              'main_canvas.png',
                                              connected=self.switch_main_canvas)
        self.switchCompareCanvasAction = HAction(self,
                                                 'Comparison\nView',
                                                 'compare_canvas.png',
                                                 connected=self.switch_compare_canvas)
        self.switchPreviewCanvasAction = HAction(self,
                                                 'Preview',
                                                 'preview_canvas.png',
                                                 connected=self.switch_preview_canvas)
        self.settingsAction = HAction(self,
                                      'Settings',
                                      'gear-1077550_640.png',
                                      connected=self.getSettings)
        # hash and shortcuts
        self.setFingerPrintAction = HAction(self,
                                            'Fingerprint\n(hash sum)',
                                            'fingerprint.png',
                                            connected=self.set_fingerprint)
        self.helpAction = HAction(self,
                                  'Shortcuts',
                                  'question-mark-1750942_640.png',
                                  connected=self.show_instruction_msg)
        self.toggleInfoPanelAction = HAction(self,
                                             'Show/Hide\nInfo Panel',
                                             'help.png',
                                             connected=self.toggleInfoPanel)

    def __init_menubar(self):
        # create menubar
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(self.openAction)
        file_menu.addAction(self.helpAction)
        file_menu.addSeparator()
        file_menu.addAction(self.refreshAction)
        file_menu.addAction(self.goToIndexAction)
        file_menu.addAction(self.toggleInfoPanelAction)
        file_menu.addSeparator()
        file_menu.addAction(self.includeFileNamesAction)
        file_menu.addAction(self.excludeFileNamesAction)

        # ~ # Edit
        # ~ edit_menu = menubar.addMenu('&Edit')  # noqa: F841

        # ~ # Draw
        # ~ draw_menu = menubar.addMenu('&Draw')  # noqa: F841

        # Compare
        compare_menu = menubar.addMenu('&Compare')
        compare_menu.addAction(self.compareAction)
        compare_menu.addAction(self.clearCompareAction)
        compare_menu.addAction(self.setFingerPrintAction)

        # Layouts
        layout_menu = menubar.addMenu('&Layout')
        layout_menu.addAction(self.switchMainCanvasAction)
        layout_menu.addAction(self.switchCompareCanvasAction)
        layout_menu.addAction(self.switchPreviewCanvasAction)
        layout_menu.addAction(self.settingsAction)

        # Help
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(self.helpAction)

    def __init_toolbar(self):
        self.toolbar = QToolBar('ToolBar', self)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # open and history
        self.toolbar.addAction(self.openAction)
        self.toolbar.addAction(self.helpAction)
        self.toolbar.addSeparator()
        # refresh and index
        self.toolbar.addAction(self.refreshAction)
        self.toolbar.addAction(self.goToIndexAction)
        self.toolbar.addSeparator()
        # include and exclude names
        self.toolbar.addAction(self.includeFileNamesAction)
        self.toolbar.addAction(self.excludeFileNamesAction)
        self.toolbar.addSeparator()
        # compare and clear compare
        self.toolbar.addAction(self.compareAction)
        self.toolbar.addAction(self.clearCompareAction)

        # canvas layout
        self.toolbar.addSeparator()
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.switchMainCanvasAction)
        self.toolbar.addAction(self.switchCompareCanvasAction)
        self.toolbar.addAction(self.switchPreviewCanvasAction)

        # others
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.settingsAction)
        self.toolbar.addAction(self.toggleInfoPanelAction)
        self.toolbar.addAction(self.setFingerPrintAction)

        # help
        self.toolbar.addSeparator()
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.helpAction)

        self.toolbar.setIconSize(QtCore.QSize(45, 45))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

    def __init_statusbar(self):
        self.statusBar().showMessage('Welcome to HandyView.')

    def __init_settings(self):
        self.fast_zoom, self.columns, self.thumbnails_in_memory = SettingsDialog(self).get_settings()

    def __init_canvas(self, path):
        self.hvdb = HVDB(path)
        self.just_started = False
        self.canvas = Canvas(self, self.hvdb)
        self.setCentralWidget(self.canvas)
        self.canvas_type = 'main'

    def __init_screen_size(self):
        size = self.screen.size()
        # ~ rect = self.screen.availableGeometry()
        self.setGeometry(0, 0, size.width(), size.height())  # (left, top, width, height)
        self.set_statusbar(f'Screen: {screen.name()} with size {size.width()} x {size.height()}.')

    def __init_dock_window(self):
        if self.dockWidget:
            self.dockWidget.close()
        # Info
        self.dockWidget = QDockWidget('Information Panel', self)
        self.dockWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.dockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dockWidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        dockedWidget = QWidget()
        self.dockWidget.setWidget(dockedWidget)

        layout = QGridLayout()
        layout.addWidget(self.canvas.zoom_label, 0, 0, 1, 3)
        layout.addWidget(self.canvas.mouse_pos_label, 1, 0, 1, 3)

        color_grid = QGridLayout()
        color_grid.addWidget(self.canvas.mouse_color_title, 0, 0, 1, 1)
        color_grid.addWidget(self.canvas.mouse_color_label, 0, 1, 1, 2)
        color_grid.addWidget(self.canvas.mouse_rgb_label, 1, 0, 1, 3)
        layout.addLayout(color_grid, 2, 0, 1, 3)

        layout.addWidget(HLine(), 3, 0, 1, 3)
        layout.addWidget(self.canvas.selection_pos_label, 4, 0, 1, 3)
        layout.addWidget(HLine(), 5, 0, 1, 3)
        layout.addWidget(self.canvas.include_names_label, 6, 0, 1, 3)
        layout.addWidget(self.canvas.exclude_names_label, 7, 0, 1, 3)
        layout.addWidget(HLine(), 8, 0, 1, 3)
        layout.addWidget(self.canvas.comparison_label, 9, 0, 1, 3)
        # update comparison info (for a second open)
        _, img_len_list = self.hvdb.update_path_list()
        show_str = 'Comparison:\n # for each folder:\n\t' + '\n\t'.join(
            map(str, img_len_list))
        if len(img_len_list) > 1:
            self.canvas.comparison_label.setText(show_str)

        # for compact space
        string = '                                                     '
        blank_qlabel = QLabel(string)  # placeholder string to avoid width auto resizing
        layout.addWidget(blank_qlabel, 10, 0, 20, 3)
        dockedWidget.setLayout(layout)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockWidget)

    ### ###

    def set_statusbar(self, text):
        self.statusBar().showMessage(text)

    def switch_fullscreen(self):
        if self.is_full_screen is False:
            self.showFullScreen()
            self.is_full_screen = True
        else:
            self.showMaximized()
            self.is_full_screen = False

    ### slots: open and history ###

    def open_file_dialog(self):
        try:
            with open(os.path.join(ROOT_DIR, 'history.txt'), 'r') as f:
                path = f.readlines()[0]
                path = path.strip()
        except FileNotFoundError:
            path = self.root_path

        formats = sorted(set([FORMAT.lower() for FORMAT in FORMATS]))
        formats = ['*' + format_ for format_ in formats]
        formats = ' '.join(formats)
        formats = f"Images ({formats})"
        path, ok = QFileDialog.getOpenFileName(
                                              self,
                                              'Select an image',
                                               path,
                                               formats)
        if path and ok:
            self.__init_canvas(path)
            self.__init_dock_window()

    # ~ def open_history(self):  # not used → disabled, but kept for reference
    # ~     with open(os.path.join(ROOT_DIR, 'history.txt'), 'r') as f:
    # ~         lines = f.readlines()
    # ~         lines = [line.strip() for line in lines]
    # ~     key, ok = QInputDialog().getItem(self, 'Open File History', 'History:',
    # ~                                      lines, 0, True)
    # ~     if ok:
    # ~         self.hvdb.init_path = key
    # ~         self.hvdb.initialize()
    # ~         self.canvas.show_image(init=True)

    ### slots: refresh and index ###

    def refresh_img_list(self):
        if self.just_started:
            return None
        # should be used in Main Cavans
        if self.canvas_type != 'main':
            self.switch_main_canvas()

        self.canvas.update_path_list()
        self.canvas.show_image(init=False)

    def goto_index(self):
        if self.just_started:
            return None
        index, ok = QInputDialog.getText(self, 'Go to index', 'Index:',
                                         QLineEdit.Normal, '1')
        if ok:
            if self.canvas_type == 'preview':
                self.switch_main_canvas()
            if index == '':
                index = 0
            elif index.isdigit():
                index = int(index) - 1
            else:
                return
            self.canvas.goto_index(index)

    ### slots: include and exclude names ###

    def include_file_name(self):
        if self.just_started:
            return None
        # show current include names as the default values
        current_include_names = self.hvdb.include_names
        current_exclude_names = self.hvdb.exclude_names
        if current_include_names is None:
            current_include_names = ''
        else:
            current_include_names = ', '.join(current_include_names)

        include_names, ok = QInputDialog.getText(self, 'Include file name',
                                                 'Key word (seprate by ,):',
                                                 QLineEdit.Normal,
                                                 current_include_names)
        if ok:
            if include_names != '':
                self.hvdb.include_names = [
                    v.strip() for v in include_names.split(',')
                ]
                self.hvdb.exclude_names = None
            else:
                self.hvdb.include_names = None
            try:
                self.refresh_img_list()
            except IndexError:  # raised if all images are filtered
                show_msg(self,
                         icon='Information',
                         title="Message",
                         text="The filter you provided filters all images. Keeping the current filter state unchanged.")
                self.hvdb.include_names = current_include_names
                self.hvdb.exclude_names = current_exclude_names

    def exclude_file_name(self):
        if self.just_started:
            return None
        # show current exclude names as the default values
        current_include_names = self.hvdb.include_names
        current_exclude_names = self.hvdb.exclude_names
        if current_exclude_names is None:
            current_exclude_names = ''
        else:
            current_exclude_names = ', '.join(current_exclude_names)

        exclude_names, ok = QInputDialog.getText(self, 'Exclude file name',
                                                 'Key word (seprate by ,):',
                                                 QLineEdit.Normal,
                                                 current_exclude_names)
        if ok:
            if exclude_names != '':
                self.hvdb.exclude_names = [
                    v.strip() for v in exclude_names.split(',')
                ]
                self.hvdb.include_names = None
            else:
                self.hvdb.exclude_names = None
            try:
                self.refresh_img_list()
            except IndexError:  # raised if all images are filtered
                show_msg(self,
                         icon='Information',
                         title="Message",
                         text="The filter you provided filters all images. Keeping the current filter state unchanged.")
                self.hvdb.include_names = current_include_names
                self.hvdb.exclude_names = current_exclude_names

    ### slots: compare and clear compare ###

    def compare_folder(self):
        # Compare folder should be set in Main Cavans
        if self.just_started:
            return None
        if self.canvas_type != 'main':
            self.switch_main_canvas()

        key, ok = QFileDialog.getOpenFileName(
            self, 'Select an image', os.path.join(
                                                  self.hvdb.get_folder(),
                                                  '../'
                                                  )
                                              )
        if ok:
            self.canvas.add_cmp_folder(key)

    def clear_compare(self):
        # Compare folder should be set in Main Cavans
        if self.just_started:
            return None
        if self.canvas_type != 'main':
            self.switch_main_canvas()

        self.canvas.clear_cmp_folder()
        self.hvdb.folder_list = [self.hvdb.folder_list[0]]
        self.hvdb.path_list = [self.hvdb.path_list[0]]
        self.hvdb.fidx = 0

    ### slots: canvas layouts ###

    def switch_main_canvas(self):
        if self.canvas_type == 'main' or self.just_started:
            return None

        self.hvdb.interval = 0
        self.canvas = Canvas(self, self.hvdb)
        self.setCentralWidget(self.canvas)
        self.__init_dock_window()
        self.canvas_type = 'main'

    def switch_compare_canvas(self):
        if self.canvas_type == 'compare' or self.just_started:
            return None
        num_compare = self.hvdb.get_folder_count()
        if num_compare == 1:
            num_view, ok = QInputDialog.getText(
                self, 'Compare Canvas',
                '# Compare Columns: (options: 2, 3, 4)', QLineEdit.Normal,
                '2')
            if ok:
                try:
                    num_view = int(num_view)
                except Exception:
                    show_msg(self,
                             icon='Warning',
                             title='Warning',
                             text='# Compare Columns should be int.')
                if num_view > 4 or num_view < 2:
                    show_msg(self,
                             icon='Warning',
                             title='Warning',
                             text='# Compare Columns should be 2, 3, 4.')
                self.hvdb.interval = num_view - 1
            else:  # default value
                self.hvdb.interval = 1
                num_view = 2
        else:
            if not self.hvdb.is_same_len:
                show_msg(self, 'Critical', 'Error',
                         ('Compare folders have different length, \n'
                          'Cannot enter compare canvas.'))
                return
            self.hvdb.fidx = 0
            num_view = min(self.hvdb.get_folder_count(), 4)
            show_msg(self,
                         'Information', 'Compare Canvas',
                         f'Comparsion folder mode.\n # Compare Columns: {num_view}.'
                     )

        self.dockWidget.hide()
        self.canvas = Canvas(self, self.hvdb, num_view=num_view)
        self.setCentralWidget(self.canvas)
        self.canvas_type = 'compare'

    def switch_preview_canvas(self):
        if self.canvas_type == 'preview' or self.just_started:
            return None

        # for some weird reason self.centralWidget().size().width() returns inconsistent (often much lower) int than actual → getting width once, which will be always work for the screen on the current machine
        if self.fresh:
            self.preview_area_width = self.centralWidget().size().width()
            self.fresh = False

        self.dockWidget.hide()
        self.previewWidget = PreviewWidget(self,
                                           self.hvdb,
                                           self.preview_area_width,
                                           columns=self.columns,
                                           thumbnails_in_memory=self.thumbnails_in_memory
                                           )
        self.canvas_type = 'preview'
        self.setCentralWidget(self.previewWidget)

    ### slots: help ###

    def show_instruction_msg(self):
        from handyview.instruction_text import instruct_text, instruct_text_cn
        msg = MessageDialog(self, instruct_text, instruct_text_cn)
        # msg.setStyleSheet('QLabel{min-width:500 px; font-size: 20px;}')
        msg.setWindowTitle('Instructions')
        msg.exec_()

    def set_fingerprint(self):
        if self.canvas_type == 'preview' or self.just_started:
            pass
        else:
            if self.canvas.show_fingerprint:
                self.canvas.show_fingerprint = False
            else:
                self.canvas.show_fingerprint = True
            self.canvas.show_image()

    def toggleInfoPanel(self):
        if self.dockWidget and self.dockWidget.isHidden():
            self.dockWidget.show()
        elif self.dockWidget and not self.dockWidget.isHidden():
            self.dockWidget.hide()

    def getSettings(self):
        dialog = SettingsDialog(self)
        dialog.recallState()
        if dialog.exec_():
            self.fast_zoom = dialog.fast_zoom
            self.thumbnails_in_memory = dialog.thumbnails_in_memory
            self.columns = dialog.columns


if __name__ == '__main__':
    if platform.system() == 'Windows':
        # set the icon in the task bar
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(windowTitle)
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    mainWindow = MainWindow(screen)
    mainWindow.show()
    sys.exit(app.exec_())
