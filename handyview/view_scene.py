"""
We use the Graphics View Framework (https://doc.qt.io/qt-5/graphicsview.html)
for our HandyView.
"""
from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, QRect, QSize
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QTransform
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QRubberBand


class HVView(QGraphicsView):
    """A customized QGraphicsView for HandyView.

    Ref:
    Selection Rect: https://stackoverflow.com/questions/47102224/pyqt-draw-selection-rectangle-over-picture  # noqa: E501
    """
    zoom_signal = QtCore.pyqtSignal(float)

    def __init__(self, scene, parent=None, show_info=True):
        super(HVView, self).__init__(scene, parent)
        self.parent = parent
        self.show_info = show_info
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)

        self.zoom = 1
        self.rotate = 0

        self.font = QFont('times', 15)
        font_metrics = QFontMetrics(self.font)
        self.text_height = font_metrics.height()

        # For selection rect (using rubber band)
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        # the origin position of rubber band
        self.rubber_band_origin = QPoint()
        # indicate whether rubber band could be changed under mouseMoveEvent
        self.rubber_band_changable = False
        self.rect_top_left = (0, 0)
        self.setViewportUpdateMode(0)

    def set_shown_text(self, text):
        # text is a list, each item will be shown in a line
        self.shown_text = text

    def drawForeground(self, painter, rect):
        painter.resetTransform()  # not scale shown text
        painter.setFont(self.font)
        painter.setPen(QColor(0, 128, 0))
        margin = 2
        for idx, text in enumerate(self.shown_text):
            painter.drawText(margin, margin + self.text_height * (idx + 1), text)

    def mousePressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            # Show rubber band
            self.rubber_band_origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.rubber_band_origin, QSize()))
            self.rubber_band.show()
            self.rubber_band_changable = True

            # Show selection rect position
            if self.show_info:
                scene_pos = self.mapToScene(event.pos())  # convert to scene position
                x_scene, y_scene = scene_pos.x(), scene_pos.y()
                self.show_rect_position(x_scene, y_scene, x_scene, y_scene)
        else:
            QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """Only works when mouse button is pressed.
        TODO: how to work when there is no mouse button is pressed.
        """
        # Show mouse position and color when mouse move with button pressed
        if self.show_info:
            scene_pos = self.mapToScene(event.pos())
            x_scene, y_scene = scene_pos.x(), scene_pos.y()
            self.show_mouse_position(x_scene, y_scene)
            self.show_mouse_color(x_scene, y_scene)

        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            if event.buttons() == QtCore.Qt.LeftButton:
                # Show selection rect position
                if self.show_info:
                    ori_scene_pos = self.mapToScene(self.rubber_band_origin)
                    ori_x_scene, ori_y_scene = ori_scene_pos.x(), ori_scene_pos.y()
                    self.show_rect_position(ori_x_scene, ori_y_scene, x_scene, y_scene)
                # Show rubber band
                if self.rubber_band_changable:
                    self.rubber_band.setGeometry(QRect(self.rubber_band_origin, event.pos()).normalized())
        else:
            QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            self.rubber_band_changable = False
        else:
            QGraphicsView.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        mouse = event.angleDelta().y() / 120
        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            # When Ctrl pressed, zoom in / out
            if mouse > 0:
                self.zoom_in(emit_signal=True)
            elif mouse < 0:
                self.zoom_out(emit_signal=True)
        elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            # only modify the current view zoom ration
            if mouse > 0:
                self.zoom_in(emit_signal=False)
            elif mouse < 0:
                self.zoom_out(emit_signal=False)
        elif modifiers == QtCore.Qt.ShiftModifier:
            if mouse > 0:
                self.parent.dir_browse(-10)
            elif mouse < 0:
                self.parent.dir_browse(10)
        else:
            # Otherwise, show the next or previous image
            if mouse > 0:
                self.parent.dir_browse(-1)
            elif mouse < 0:
                self.parent.dir_browse(1)

    def show_mouse_position(self, x_pos, y_pos):
        """Show mouse position under the scene position (ignore the zoom)."""
        self.parent.mouse_pos_label.setText(('Cursor position:\n (ignore zoom)\n'
                                             f' Height(y): {y_pos:.1f}\n Width(x):  {x_pos:.1f}'))

        # if cursor is out of image, the text will be red
        if (0 < x_pos < self.scene().width and 0 < y_pos < self.scene().height):
            self.parent.mouse_pos_label.setStyleSheet('QLabel {color : black;}')
        else:
            self.parent.mouse_pos_label.setStyleSheet('QLabel {color : red;}')

    def show_mouse_color(self, x_pos, y_pos):
        """Show mouse color with RGBA values."""
        pixel = self.parent.qimg.pixel(int(x_pos), int(y_pos))
        pixel_color = QColor(pixel)
        self.parent.mouse_color_label.fill(pixel_color)
        rgba = pixel_color.getRgb()  # 8 bit RGBA
        self.parent.mouse_rgb_label.setText(f' ({rgba[0]:3d}, {rgba[1]:3d}, {rgba[2]:3d}, {rgba[3]:3d})')

    def show_rect_position(self, x_start, y_start, x_end, y_end):
        """Show selection rect position."""
        x_len = x_end - x_start
        y_len = y_end - y_start
        self.parent.selection_pos_label.setText('Rect Pos: (H, W)\n'
                                                f' Start: {int(y_start)}, {int(x_start)}\n'
                                                f' End  : {int(y_end)}, {int(x_end)}\n'
                                                f' Len  : {int(y_len)}, {int(x_len)}')
        self.parent.db.selection_pos = [int(y_start), int(x_start), int(y_len), int(x_len)]
        width, height = self.scene().width, self.scene().height
        if (0 < x_start < width and 0 < y_start < height and 0 < x_end < width and 0 < y_end < height):
            self.parent.selection_pos_label.setStyleSheet('QLabel {color : black;}')
        else:
            self.parent.selection_pos_label.setStyleSheet('QLabel {color : red;}')

    def zoom_in(self, scale=1.05, emit_signal=False):
        self.zoom *= scale
        if emit_signal:
            self.zoom_signal.emit(self.zoom)
        if self.show_info:
            self.parent.zoom_label.setText(f'Zoom: {self.zoom:.2f}')
        self.set_transform()

    def zoom_out(self, scale=1.05, emit_signal=False):
        self.zoom /= scale
        if emit_signal:
            self.zoom_signal.emit(self.zoom)
        if self.show_info:
            self.parent.zoom_label.setText(f'Zoom: {self.zoom:.2f}')
        self.set_transform()

    def set_zoom(self, ratio):
        self.zoom = ratio
        if self.show_info:
            self.parent.zoom_label.setText(f'Zoom: {self.zoom:.2f}')
        self.set_transform()

    def set_transform(self):
        self.setTransform(QTransform().scale(self.zoom, self.zoom).rotate(self.rotate))


class HVScene(QGraphicsScene):
    """A customized QGraphicsScene for HandyView.
    """

    def __init__(self, parent=None, show_info=True):
        super(HVScene, self).__init__()
        self.parent = parent
        self.show_info = show_info
        self.width = None
        self.height = None

    def set_width_height(self, width, height):
        self.width = width
        self.height = height

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            # scroll bar
            QGraphicsScene.keyPressEvent(self, event)
        else:
            # use canvas keyPressEvent for direction keys
            self.parent.keyPressEvent(event)

    def mouseMoveEvent(self, event):
        """It only works when NO mouse button is pressed."""
        # Show mouse position and color when mouse move without button pressed
        if self.show_info:
            x_pos, y_pos = event.scenePos().x(), event.scenePos().y()
            self.show_mouse_position(x_pos, y_pos)
            self.show_mouse_color(x_pos, y_pos)

    def show_mouse_position(self, x_pos, y_pos):
        """Show mouse position under the scene position (ignore the zoom)."""
        self.parent.mouse_pos_label.setText(('Cursor position:\n (ignore zoom)\n'
                                             f' Height(y): {y_pos:.1f}\n Width(x):  {x_pos:.1f}'))

        # if cursor is out of image, the text will be red
        if (0 < x_pos < self.width and 0 < y_pos < self.height):
            self.parent.mouse_pos_label.setStyleSheet('QLabel {color : black;}')
        else:
            self.parent.mouse_pos_label.setStyleSheet('QLabel {color : red;}')

    def show_mouse_color(self, x_pos, y_pos):
        """Show mouse color with RGBA values."""
        pixel = self.parent.qimg.pixel(int(x_pos), int(y_pos))
        pixel_color = QColor(pixel)
        self.parent.mouse_color_label.fill(pixel_color)
        rgba = pixel_color.getRgb()  # 8 bit RGBA
        self.parent.mouse_rgb_label.setText(f' ({rgba[0]:3d}, {rgba[1]:3d}, {rgba[2]:3d}, {rgba[3]:3d})')
