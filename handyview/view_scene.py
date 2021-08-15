"""
We use the Graphics View Framework (https://doc.qt.io/qt-5/graphicsview.html)
for our HandyView.
"""
from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, QRect, QSize
from PyQt5.QtGui import (QColor, QFont, QFontMetrics, QTransform, QPixmap,
                         QImage, QPainter)
from PyQt5.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                             QRubberBand)


class HVView(QGraphicsView):
    """A customized QGraphicsView for HandyView.

    Ref:
        Selection Rect: https://stackoverflow.com/questions/47102224/pyqt-draw-selection-rectangle-over-picture  # noqa: E501

    Attributes:
        parent (Canvas ← subclass of QWidget):
        show_info (bool): if True the qgraphicsview is in main view and mainWindow.dockWidget will be updated

        font (QFont): font of self.shown_text
        shown_text (list(str)): text shown in the top left over the image

        rect_top_left (tuple): redundant, not used
        rotate (int): rotation angle ← used in self.setTransform ← redundant, works without QTransform.rotate(self.rotate)

        rubber_band_changable (bool):
        rubber_band (QRubberBand): selection rectangle
        rubber_band_origin (QPoint): location of the mouse press to start drawing the selection rectangle

        text_height (int QFontMetrics.height()):
        zoom (int): zoom ratio
        fast_zoom (bool):

            fast_zoom=True: save as in v0.4.2
            - faster
            - photos look good
            - images with text/lines/vector graphics show artifacts upon zoom
            - cursor position coordinates reflect actual image dimensions regardless of zoom state
            - pressing CTRL+R will temporarily disable fast zoom

            fast_zoom=False:
            - slower
            - both photos and images with text/lines/vector graphics look perfect
            - cursor position coordinates reflect resized image dimensions unless Zoom is 1.0
    """
    zoom_signal = QtCore.pyqtSignal(float)  # used in comparison view: when when one HVView zoom changes, zoom state is emitted and connected to set zoom of other HVView's in the layout

    def __init__(self, scene, parent=None, show_info=True, fast_zoom=True):
        """Summary

        Args:
            scene (QGraphicsScene):
            parent (None or Canvas ← subclass of QWidget, optional):
            show_info (bool, optional): if True the qgraphicsview is in main view and mainWindow.dockWidget will be updated
            fast_zoom(bool, optional)
        """
        super(HVView, self).__init__(scene, parent)
        self.parent = parent
        self.show_info = show_info
        self.fast_zoom = fast_zoom
        self.is_precise_zoom_set = False
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

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
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    def set_shown_text(self, text):
        # text is a list, each item will be shown in a line
        self.shown_text = text

    ### reimplemented protected method ###

    def drawForeground(self, painter, rect):
        ''' draws self.shown_text as foreground '''

        painter.resetTransform()  # not scale shown text
        painter.setFont(self.font)
        painter.setPen(QColor(0, 128, 0))
        margin = 2
        for idx, text in enumerate(self.shown_text):
            painter.drawText(margin,
                             margin + self.text_height * (idx + 1),
                             text
                             )

    ### reimplemented protected methods: events ###

    def mousePressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            # Show rubber band
            self.rubber_band_origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.rubber_band_origin,
                                               QSize()
                                               )
                                         )
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
        if self.show_info:  # redundant qscene overwrites the outcome of this function
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
                    self.show_rect_position(ori_x_scene, ori_y_scene, x_scene,
                                            y_scene)
                # Show rubber band
                if self.rubber_band_changable:
                    topLeftPoint = self.rubber_band_origin
                    bottomRightPoint = event.pos()
                    qRect = QRect(topLeftPoint, bottomRightPoint).normalized()
                    self.rubber_band.setGeometry(qRect)
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
        forward = mouse > 0
        backward = mouse < 0
        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            # When Ctrl pressed, zoom in / out
            if forward:
                self.zoom_in(emit_signal=True)
            elif backward:
                self.zoom_out(emit_signal=True)
        elif modifiers == (QtCore.Qt.ControlModifier
                           | QtCore.Qt.ShiftModifier):
            # only modify the the zoom in the current view
            # used in compare views
            if forward:
                self.zoom_in(emit_signal=False)
            elif backward:
                self.zoom_out(emit_signal=False)
        elif modifiers == QtCore.Qt.ShiftModifier:
            if forward:
                self.parent.dir_browse(-10)
            elif backward:
                self.parent.dir_browse(10)
        else:
            # Otherwise, show the next or previous image
            if forward:
                self.parent.dir_browse(-1)
            elif backward:
                self.parent.dir_browse(1)

    ### methods used in displaying info panel ###

    def show_mouse_position(self, x_pos, y_pos):  # redundant qscene overwrites the outcome of this function
        """Show mouse position under the scene position (ignore the zoom)."""
        if self.fast_zoom:
            self.parent.mouse_pos_label.setText(
                ('Cursor position:\n (ignoring zoom)\n'
                 f' Height(y): {y_pos:.1f}\n Width(x):  {x_pos:.1f}'))
        else:
            self.parent.mouse_pos_label.setText(
                ('Cursor position:\n (counting zoom)\n'
                 f' Height(y): {y_pos:.1f}\n Width(x):  {x_pos:.1f}'))

        # if cursor is out of image, the text will be red
        if (0 < x_pos < self.scene().width
                and 0 < y_pos < self.scene().height):
            self.parent.mouse_pos_label.setStyleSheet(
                'QLabel {color : black;}')
        else:
            self.parent.mouse_pos_label.setStyleSheet('QLabel {color : red;}')

    def show_mouse_color(self, x_pos, y_pos):  # redundant qscene overwrites the outcome of this function
        """Show mouse color with RGBA values."""
        pixel = self.scene().qImage.pixel(int(x_pos), int(y_pos))
        pixel_color = QColor(pixel)
        self.parent.mouse_color_label.fill(pixel_color)
        rgba = pixel_color.getRgb()  # 8 bit RGBA
        self.parent.mouse_rgb_label.setText(
            f' ({rgba[0]:3d}, {rgba[1]:3d}, {rgba[2]:3d}, '
            f'{rgba[3]:3d})')

    def show_rect_position(self, x_start, y_start, x_end, y_end):
        """ Shows selection rectangle position in the info panel"""

        x_len = x_end - x_start
        y_len = y_end - y_start
        self.parent.selection_pos_label.setText(
            'Rect Pos: (H, W)\n'
            f' Start: {int(y_start)}, {int(x_start)}\n'
            f' End  : {int(y_end)}, {int(x_end)}\n'
            f' Len  : {int(y_len)}, {int(x_len)}')
        width, height = self.scene().width, self.scene().height
        if (0 < x_start < width and 0 < y_start < height and 0 < x_end < width
                and 0 < y_end < height):
            self.parent.selection_pos_label.setStyleSheet(
                'QLabel {color : black;}')
        else:
            self.parent.selection_pos_label.setStyleSheet(
                'QLabel {color : red;}')

    ### zoom methods ###

    def zoom_in(self, scale=1.05, emit_signal=False):
        self.zoom *= scale
        if emit_signal:
            self.zoom_signal.emit(self.zoom)
        if self.show_info:
            self.parent.zoom_label.setText(f'Zoom: {self.zoom:.2f}')
        self.perform_zoom()

    def zoom_out(self, scale=1.05, emit_signal=False):
        self.zoom /= scale
        if emit_signal:
            self.zoom_signal.emit(self.zoom)
        if self.show_info:
            self.parent.zoom_label.setText(f'Zoom: {self.zoom:.2f}')
        self.perform_zoom()

    def set_zoom(self, ratio):
        self.zoom = ratio
        if self.show_info:
            self.parent.zoom_label.setText(f'Zoom: {self.zoom:.2f}')
        self.perform_zoom()

    def __fast_zoom(self):
        if self.is_precise_zoom_set:
            self.scene().reset_zoom()
            self.is_precise_zoom_set = False
        qTransform = QTransform()
        qTransform.scale(self.zoom, self.zoom)
        qTransform.rotate(self.rotate)  # redundant, not necessary
        self.setTransform(qTransform)

    def precise_zoom(self):
        ''' preceision zoom for displaying documents, text and line/vector graphics '''

        scroll_state = self.__get_scroll_state()
        self.scene().zoom_image(self.zoom)
        self.is_precise_zoom_set = True
        if self.isTransformed():
            self.resetTransform()
        self.__set_scroll_state(scroll_state)

    def __get_scroll_state(self):
        """ copied from https://stackoverflow.com/questions/8939315/maintaining-view-scroll-position-in-qgraphicsview-when-swapping-images
        Returns a tuple of scene extents percentages.
        """
        centerPoint = self.mapToScene(self.viewport().width()/2,
                                      self.viewport().height()/2)
        sceneRect = self.sceneRect()
        centerWidth = centerPoint.x() - sceneRect.left()
        centerHeight = centerPoint.y() - sceneRect.top()
        sceneWidth =  sceneRect.width()
        sceneHeight = sceneRect.height()

        sceneWidthPercent = centerWidth / sceneWidth if sceneWidth != 0 else 0
        sceneHeightPercent = centerHeight / sceneHeight if sceneHeight != 0 else 0
        return sceneWidthPercent, sceneHeightPercent

    def __set_scroll_state(self, scroll_state):
        """ copied from https://stackoverflow.com/questions/8939315/maintaining-view-scroll-position-in-qgraphicsview-when-swapping-images
        """
        sceneWidthPercent, sceneHeightPercent = scroll_state
        x = (sceneWidthPercent * self.sceneRect().width() +
             self.sceneRect().left())
        y = (sceneHeightPercent * self.sceneRect().height() +
             self.sceneRect().top())
        self.centerOn(x, y)




        # ~ self.translate(50.0, 50.0)

    def perform_zoom(self):
        if self.fast_zoom:
            self.__fast_zoom()
        else:
            self.precise_zoom()


class HVScene(QGraphicsScene):
    """A customized QGraphicsScene for HandyView.

    Attributes:
        width (int): image width
        height (int): image height
        parent (Canvas ← subclass of QWidget):
        show_info (bool): True if the scene is in main view
    """

    def __init__(self, parent=None, show_info=True):
        super(HVScene, self).__init__()
        self.parent = parent
        self.show_info = show_info
        self.is_resized = False

    @property
    def width(self):
        return self.qPixmap.width()

    @property
    def height(self):
        return self.qPixmap.height()

    # ~ def set_image(self, qImage, width, height):  # no need to feed PIL.image width and height into HVScene because QPixel and QImage .width() and .height() return the same dimensions
    # ~     qPixmap = QPixmap.fromImage(qImage)
    # ~     self.clear()
    # ~     self.addPixmap(qPixmap)

    # ~     # width and heights are the same for all below
    # ~     print(f"width → {width}")
    # ~     print(f"height → {height}")
    # ~     print(f"qImage.width() → {qImage.width()}")
    # ~     print(f"qImage.height() → {qImage.height()}")
    # ~     print(f"qPixmap.width() → {qPixmap.width()}")
    # ~     print(f"qPixmap.height() → {qPixmap.height()}")

    # ~     self.set_width_height(width, height)
    # ~     # put image always in the center of a QGraphicsView
    # ~     self.setSceneRect(0, 0, width, height)

    def set_image(self, img_path):
        self.clear()
        self.qImage = QImage(img_path)
        self.qPixmap = QPixmap.fromImage(self.qImage)
        self.addPixmap(self.qPixmap)
        # put image always in the center of a QGraphicsView
        self.setSceneRect(0, 0, self.qImage.width(), self.qImage.height())

        self.img_path = img_path
        self.orig_width = self.qImage.width()
        self.orig_height = self.qImage.height()

    def zoom_image(self, zoom_factor):
        """
            zoom_factor (float):
        """

        # resetting zoom to 1 every time it is passed to give accurate
        # image sizing in pixels; otherwise the pixels may be off by a few
        # due to floating point precision
        if round(zoom_factor, 3) == 1.0:
            zoom_factor = 1
        # ~ print(f"zoom_factor → {zoom_factor}")
        # ~ print(f"original width → {self.orig_width} original height → {self.orig_height}")

        width = int(self.orig_width * zoom_factor)
        height = int(self.orig_height * zoom_factor)
        qSize = QSize(width, height)
        # ~ print(f"width → {width} height → {height}")

        self.clear()
        self.qImage = QImage(self.img_path)
        self.qPixmap = QPixmap.fromImage(self.qImage)
        self.qPixmap = self.qPixmap.scaled(qSize,
                                           QtCore.Qt.KeepAspectRatio,
                                           QtCore.Qt.SmoothTransformation)
        self.addPixmap(self.qPixmap)
        # put image always in the center of a QGraphicsView
        self.setSceneRect(0, 0, self.qPixmap.width(), self.qPixmap.height())
        self.is_resized = True

    def reset_zoom(self):
        self.set_image(self.img_path)
        self.is_resized = False

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

    def setBackgroundWhite(self):
        self.setBackgroundBrush(QtCore.Qt.white)

    def setBackgroundGrey(self):
        rgb = 211, 211, 211
        self.setBackgroundBrush(QColor(*rgb))

    def show_mouse_position(self, x_pos, y_pos):
        """Show mouse position under the scene position (ignore the zoom)."""
        if self.is_resized:
            self.parent.mouse_pos_label.setText(
                ('Cursor position:\n (counting zoom)\n'
                 f' Height(y): {y_pos:.1f}\n Width(x):  {x_pos:.1f}'))
        else:
            self.parent.mouse_pos_label.setText(
                ('Cursor position:\n (ignoring zoom)\n'
                 f' Height(y): {y_pos:.1f}\n Width(x):  {x_pos:.1f}'))

        # if cursor is out of image, the text will be red
        if (0 < x_pos < self.width and 0 < y_pos < self.height):
            self.parent.mouse_pos_label.setStyleSheet('QLabel {color : black;}')
        else:
            self.parent.mouse_pos_label.setStyleSheet('QLabel {color : red;}')

    def show_mouse_color(self, x_pos, y_pos):
        """Show mouse color with RGBA values."""
        if self.is_resized:
            qImage = self.qPixmap.toImage()
            qRgb = qImage.pixel(int(x_pos), int(y_pos))
        else:
            qRgb = self.qImage.pixel(int(x_pos), int(y_pos))

        pixel_color = QColor(qRgb)
        self.parent.mouse_color_label.fill(pixel_color)
        rgba = pixel_color.getRgb()  # 8 bit RGBA
        self.parent.mouse_rgb_label.setText(
            f' ({rgba[0]:3d}, {rgba[1]:3d}, {rgba[2]:3d}, '
            f'{rgba[3]:3d})')
