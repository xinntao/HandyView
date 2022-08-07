import gc
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt, QUrl
from PyQt5.QtGui import QColor
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import QApplication, QFileDialog, QGridLayout, QHBoxLayout, QPushButton, QSlider, QStyle, QWidget

from handyview.utils import ROOT_DIR
from handyview.view_scene import HVScene, HVView


class CanvasVideo(QWidget):
    """Canvas for comparing videos.

    Now only support comparing two videos
    """

    def __init__(self, parent):
        super(CanvasVideo, self).__init__()
        self.parent = parent

        self.info_text = []
        self.flag_show_info = True

        # initialize widgets and layout
        self.init_widgets_layout()
        self.qview_bg_color = 'white'
        self.show_fingerprint = False

        # for auto zoom ratio
        self.target_zoom_width = 0

    def init_player(self):
        if not hasattr(self, 'player1'):
            # the first video player
            self.videoitem1 = QGraphicsVideoItem()
            self.player1 = QMediaPlayer(self)
            self.player1.setVideoOutput(self.videoitem1)
            # the second video player
            self.videoitem2 = QGraphicsVideoItem()
            self.player2 = QMediaPlayer(self)
            self.player2.setVideoOutput(self.videoitem2)

            # signal-slot
            self.player1.stateChanged.connect(self.mediaStateChanged)
            self.player1.positionChanged.connect(self.positionChanged)
            self.player1.durationChanged.connect(self.durationChanged)

            # add to scene
            self.scene_text = self.qscenes[0].addText('')
            self.qscenes[0].addItem(self.videoitem1)
            self.qscenes[0].addItem(self.videoitem2)

            self.flag_front_player = '1'
            self.pause_pos = 0

    def open_files(self):
        # init players
        self.init_player()
        # open the first video file
        self.video_file = self._open_one_file()
        self.player1.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_file)))
        height, width = self.videoitem1.size().height(), self.videoitem1.size().width()
        self.qscenes[0].set_width_height(width, height)
        # put video always in the center of a QGraphicsView
        self.qscenes[0].setSceneRect(0, 0, width, height)

        # open the second video file
        self.video_file2 = self._open_one_file()
        self.player2.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_file2)))

        self.playButton.setEnabled(True)
        self.syncButton.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.infoButton.setEnabled(True)

        self.show_video(init=True)
        self.show_video_info()

    def _open_one_file(self):
        # get open file name
        try:
            with open(os.path.join(ROOT_DIR, 'history.txt'), 'r') as f:
                history = f.readlines()[0]
                history = history.strip()
        except Exception:
            history = '.'
        key, ok = QFileDialog.getOpenFileName(self, 'Open Video', history)
        if ok:
            # save history
            try:
                with open(os.path.join(ROOT_DIR, 'history.txt'), 'r') as f:
                    lines = f.readlines()
                    lines = [line.strip() for line in lines]
                    if len(lines) == 5:
                        del lines[-1]
            except Exception:
                lines = []
            # add the new record to the first line
            if key not in lines:
                lines.insert(0, key)
            with open(os.path.join(ROOT_DIR, 'history.txt'), 'w') as f:
                for line in lines:
                    f.write(f'{line}\n')
            return key

    def init_widgets_layout(self):
        # QGraphicsView - QGraphicsScene - QPixmap
        self.qscenes = []
        self.qviews = []
        show_info = False
        self.qscenes.append(HVScene(self, show_info=show_info))
        self.qviews.append(HVView(self.qscenes[0], self, show_info=show_info))

        # ---------------------------------------
        # layouts
        # ---------------------------------------
        main_layout = QGridLayout(self)
        # QGridLayout:
        # int row, int column, int rowSpan, int columnSpan
        main_layout.addWidget(self.qviews[0], 0, 0, -1, 50)

        self.infoButton = QPushButton()
        self.infoButton.setEnabled(False)
        self.infoButton.setFixedSize(QSize(80, 80))
        self.infoButton.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        self.infoButton.clicked.connect(self.show_video_info)

        self.clearButton = QPushButton()
        self.clearButton.setEnabled(False)
        self.clearButton.setFixedSize(QSize(80, 80))
        self.clearButton.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.clearButton.clicked.connect(self.clear_players)

        self.syncButton = QPushButton()
        self.syncButton.setEnabled(False)
        self.syncButton.setFixedSize(QSize(80, 80))
        self.syncButton.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.syncButton.clicked.connect(self.sync_two_players)

        self.playButton = QPushButton()
        self.playButton.setFixedSize(QSize(80, 80))
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.syncButton)
        controlLayout.addWidget(self.positionSlider)

        # controlLayout2 = QVBoxLayout()
        # controlLayout2.setContentsMargins(0, 0, 0, 0)

        # controlLayout2.addWidget(self.playButton)
        # controlLayout2.addLayout(controlLayout)
        main_layout.addWidget(self.clearButton, 59, 0, 1, 1)
        main_layout.addWidget(self.infoButton, 58, 0, 1, 1)
        main_layout.addLayout(controlLayout, 60, 0, -1, 49)

        self.qviews[0].set_shown_text(['Click Open to open ·two· videos for comparison!', 'bug 出没 - 还在测试中'])

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.key() == QtCore.Qt.Key_F9:
            self.toggle_bg_color()
        elif event.key() == QtCore.Qt.Key_R:
            for qview in self.qviews:
                qview.set_zoom(1)
        elif event.key() == QtCore.Qt.Key_C:
            print('Enter C')
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

    def show_video_info(self):
        if self.flag_show_info is True:
            # if not self.info_text:
            if self.player1.metaData('Resolution') is not None:
                resolution_str1 = (f"Resolution : {self.player1.metaData('Resolution').width()} "
                                   f"x {self.player1.metaData('Resolution').height()}")
            else:
                resolution_str1 = ('Resolution : None')
            if self.player2.metaData('Resolution') is not None:
                resolution_str2 = (f"Resolution : {self.player2.metaData('Resolution').width()} "
                                   f"x {self.player2.metaData('Resolution').height()}")
            else:
                resolution_str2 = ('Resolution : None')

            self.info_text = [
                f'Title      : {os.path.basename(self.video_file)}',
                resolution_str1,
                f"Duration   : {str(self.player1.metaData('Duration'))}",
                f"FrameRate  : {str(self.player1.metaData('VideoFrameRate'))}",
                f"BitRate    : {str(self.player1.metaData('VideoBitRate'))}",
                f"Video Codec: {str(self.player1.metaData('VideoCodec'))}",
                '',
                f'Title      : {os.path.basename(self.video_file2)}',
                resolution_str2,
                f"Duration   : {str(self.player2.metaData('Duration'))}",
                f"FrameRate  : {str(self.player2.metaData('VideoFrameRate'))}",
                f"BitRate    : {str(self.player2.metaData('VideoBitRate'))}",
                f"Video Codec: {str(self.player2.metaData('VideoCodec'))}",
            ]
            self.qviews[0].set_shown_text(self.info_text)
            self.flag_show_info = False
        else:
            self.qviews[0].set_shown_text(['Click InfoButtion to show video information'])
            self.flag_show_info = True

        self.qscenes[0].update()  # update the shown text

    def clear_players(self):
        if hasattr(self, 'player1'):
            self.player1.stop()
            self.player2.stop()
            self.qscenes[0].clear()
            del self.videoitem1
            del self.videoitem2
            del self.player1
            del self.player2
            gc.collect()
            self.playButton.setEnabled(False)
            self.syncButton.setEnabled(False)
            self.clearButton.setEnabled(False)
            self.infoButton.setEnabled(False)
            self.positionSlider.setRange(0, 0)

            # clear the shown text
            self.qviews[0].set_shown_text([])
            self.qscenes[0].update()

    def sync_two_players(self):
        position = self.player1.position()
        self.player1.setPosition(position)
        self.player2.setPosition(position)

    def play(self):
        """only control player 1"""
        if self.player1.state() == QMediaPlayer.PlayingState:
            self.pause_pos = self.player1.position()
            print(self.pause_pos, self.player1.duration(), self.player2.duration())
            self.player1.pause()
            self.player2.pause()
        else:
            self.player1.play()
            self.player2.play()

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.player1.setPosition(position)
        self.player2.setPosition(position)

    def mediaStateChanged(self, state):
        if self.player1.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def compare_folders(self, step):
        self.show_video()

    def show_video(self, init=False):
        if hasattr(self, 'player1'):
            if self.flag_front_player == '1':
                self.scene_text.setPlainText(os.path.basename(self.video_file))
                self.flag_front_player = '2'
                self.qscenes[0].setFocusItem(self.videoitem2)
                self.videoitem2.stackBefore(self.videoitem1)
                # refresh frame in pause state
                # TODO: still have problem
                if self.player1.state() != QMediaPlayer.PlayingState:
                    self.setPosition(self.pause_pos)
            else:
                self.scene_text.setPlainText(os.path.basename(self.video_file2))
                self.flag_front_player = '1'
                self.qscenes[0].setFocusItem(self.videoitem1)
                self.videoitem1.stackBefore(self.videoitem2)
                # refresh frame in pause state
                # TODO: still have problem
                if self.player1.state() != QMediaPlayer.PlayingState:
                    self.setPosition(self.pause_pos)

            self.qviews[0].set_transform()

    def dir_browse(self, step):
        self.show_video()

    def toggle_bg_color(self):
        if self.qview_bg_color == 'white':
            self.qview_bg_color = 'lightgray'
            for qscene in self.qscenes:
                qscene.setBackgroundBrush(QColor(211, 211, 211))
        else:
            self.qview_bg_color = 'white'
            for qscene in self.qscenes:
                qscene.setBackgroundBrush(QtCore.Qt.white)
