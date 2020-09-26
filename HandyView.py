import os
import sys
import glob
import re
from PIL import Image

from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QTransform, QColor, QImage, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                             QGraphicsScene)
from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QGroupBox,
                             QLabel, QToolBar)
from PyQt5.QtWidgets import QDockWidget, QFileDialog

import actions as actions


class HandyScene(QGraphicsScene):

    def __init__(self, parent=None):
        super(HandyScene, self).__init__()
        self.parent = parent

    def mouseMoveEvent(self, event):
        # show mouse position on the original image
        # zoom will not influence
        x_pos = event.scenePos().x()
        y_pos = event.scenePos().y()
        self.parent.qlabel_info_mouse_pos.setText(
            ('Cursor position: (ignore zoom) \n'
            "\tx (width):\t{:.1f}\n\ty (height):\t{:.1f}".format(\
            x_pos, y_pos)))
        # if out of image, the text will be red
        if x_pos < 0 or y_pos < 0 or x_pos > self.parent.imgw or y_pos > self.parent.imgh:
            self.parent.qlabel_info_mouse_pos.setStyleSheet(
                'QLabel {color : red; }')
        else:  # normal
            self.parent.qlabel_info_mouse_pos.setStyleSheet(
                'QLabel {color : black; }')
            # show rgb values
            c = self.parent.qimg.pixel(int(x_pos), int(y_pos))
            c_rgb = QColor(c).getRgb()  # 8bit RGBA: (255, 23, 0, 255)
            self.parent.qlabel_info_mouse_rgb_value.setText('RGB: ({:3d}, {:3d}, {:3d})'.format(\
                c_rgb[0], c_rgb[1], c_rgb[2]))


# https://stackoverflow.com/questions/16105349/remove-scroll-functionality-on-mouse-wheel-qgraphics-view
class HandyView(QGraphicsView):

    def __init__(self, scene, parent=None):
        super(HandyView, self).__init__(scene, parent)
        self.parent = parent
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        # self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.qsetHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)
        self.zoom = 1
        self.rotvals = (0, -90, -180, -270)
        self.rotate = 0

    def wheelEvent(self, event):
        moose = event.angleDelta().y() / 120
        if moose > 0:
            self.zoom_in()
        elif moose < 0:
            self.zoom_out()

    def zoom_in(self):
        self.zoom *= 1.05
        self.parent.qlabel_info_zoom_ration.setText(
            '\n# Zoom ration:\t{:.1f}'.format(self.zoom))
        self.set_transform()

    def zoom_out(self):
        self.zoom /= 1.05
        self.parent.qlabel_info_zoom_ration.setText(
            '\n# Zoom ration:\t{:.1f}'.format(self.zoom))
        self.set_transform()

    def set_zoom(self, ratio):
        self.zoom = ratio
        self.parent.qlabel_info_zoom_ration.setText(
            '\n# Zoom ration:\t{:.1f}'.format(self.zoom))
        self.set_transform()

    def set_transform(self):
        self.setTransform(QTransform().scale(self.zoom,
                                             self.zoom).rotate(self.rotate))


class Canvas(QWidget):

    def __init__(self, parent=None):
        super(Canvas, self).__init__()

        try:
            self.key = sys.argv[1]
        except IndexError:
            print('\nHandyView \nUsage[from terminal]: HandyView img_path\n')
            sys.exit(1)

        self.formats = ('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG',
                        '.ppm', '.PPM', '.bmp', '.BMP', '.gif', '.GIF', 'tiff')
        try:
            open(self.key, 'r')
        except IOError:
            print('There was an error opening {}'.format(self.key))
            sys.exit(1)

        if self.key.endswith(self.formats):

            # layout
            main_layout = QGridLayout(self)
            # QgraphicsView - QGraphicsScene - QPixmap
            self.qscene = HandyScene(self)
            self.qview = HandyView(self.qscene, self)

            main_layout.addWidget(self.qview, 0, 0, 30, 5)
            # bottom QLabel, show image path
            self.qlabel_img_path = QLabel(self)
            main_layout.addWidget(self.qlabel_img_path, 30, 0, 1, 5)
            # information panel; multiple QLabels, using setText to update
            self.info_group = QGroupBox('Information Panel')
            self.qlabel_info_img_name = QLabel(self)  # image name
            self.qlabel_info_mouse_pos = QLabel(self)
            self.qlabel_info_mouse_rgb_value = QLabel(self)
            self.qlabel_info_wh = QLabel(self)  # image width and height
            self.qlabel_info_color_type = QLabel(self)  # image color type
            self.qlabel_info_zoom_ration = QLabel(self)  # zoom ratio
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
            # real-time mouse position(relate to original images)
            infor_group_layout = QVBoxLayout()
            infor_group_layout.setAlignment(QtCore.Qt.AlignTop)
            infor_group_layout.addWidget(self.qlabel_info_img_name)
            infor_group_layout.addWidget(self.qlabel_info_mouse_pos)
            infor_group_layout.addWidget(self.qlabel_info_mouse_rgb_value)
            infor_group_layout.addWidget(self.qlabel_info_wh)
            infor_group_layout.addWidget(self.qlabel_info_color_type)
            infor_group_layout.addWidget(self.qlabel_info_zoom_ration)
            self.info_group.setLayout(infor_group_layout)
            main_layout.addWidget(self.info_group, 15, 5, 15, 1)

            self.qview_bg_color = 'white'

            self.get_img_list()
            self.show_image(init=True)
        else:
            print('Unsupported file format.')
            sys.exit(1)

    def get_img_list(self):
        # get image list
        self.path, self.img_name = os.path.split(self.key)
        self.imgfiles = []
        if self.path == '':
            self.path = './'
        for img_path in glob.glob(self.path + '/*'):
            _, img_name = os.path.split(img_path)
            base, ext = os.path.splitext(img_name)
            if ext in self.formats:
                self.imgfiles.append(img_name)
        # natural sort
        self.imgfiles.sort(key=lambda s: [
            int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', s)
        ])
        # get current pos
        self.dirpos = self.imgfiles.index(self.img_name)

    def keyPressEvent(self, event):
        # should be the focus problem
        if event.key() == QtCore.Qt.Key_F9:
            self.toggle_bg_color()
        elif event.key() == QtCore.Qt.Key_R:
            self.qview.set_zoom(1)
        elif event.key() == QtCore.Qt.Key_Space:
            self.dir_browse(1)
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.dir_browse(-1)

    def keyReleaseEvent(self, event):
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
        self.qlabel_img_path.setText('{}\n{:3d} / {:3d}'.\
            format(self.key, self.dirpos + 1, len(self.imgfiles)))
        # update information panel
        self.path, self.img_name = os.path.split(self.key)
        # self.qlabel_info_img_name.setText('# Image name:\n   {}'.format(self.img_name))

        self.qlabel_info_wh.setText('\n# Image size:\n\tHeight:\t{:d}\n\tWeight:\t{:d}'\
            .format(self.imgh, self.imgw))
        with Image.open(self.key) as lazy_img:
            self.qlabel_info_color_type.setText('\n# Color type:\t{}'.format(
                lazy_img.mode))

        if init:
            if self.imgw < 500:
                self.qview.set_zoom(500 // self.imgw)
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
        file_menu.addAction(actions.new(self))

        # Edit
        edit_menu = menubar.addMenu('&Edit')
        edit_menu.addAction(actions.resize(self))
        edit_menu.addAction(actions.crop(self))

        # Draw
        draw_menu = menubar.addMenu('&Draw')

        # Compare
        compare_menu = menubar.addMenu('&Compare')

        # View
        self.view_menu = menubar.addMenu('&View')

        # Help
        help_menu = menubar.addMenu('&Help')

    def init_statusbar(self):
        self.statusBar().showMessage('Ready')

    def init_toolbar(self):
        self.toolbar = QToolBar(self)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addAction(actions.open(self))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

    def init_central_window(self):
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)

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

    ##################################
    # Slots
    ##################################

    def open_file_dialog(self):
        key = QFileDialog.getOpenFileName(self, 'Select an image', '.')[0]
        if key.endswith(self.canvas.formats):
            self.canvas.key = key
        self.canvas.get_img_list()
        self.canvas.show_image(init=True)


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
    main = MainWindow()
    main.showMaximized()
    sys.exit(app.exec_())
