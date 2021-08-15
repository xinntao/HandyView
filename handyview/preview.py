import os
import zlib
import json
from PIL import Image
from io import BytesIO

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QGridLayout, QWidget, QPushButton, QHBoxLayout,
                             QScrollArea, QProgressDialog, QMessageBox, QDialog)
from PyQt5.uic import loadUi


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('./handyview/SettingsDialog.ui', self)

        self.settings_file = "settings.json"
        self.clearCachePushButton.clicked.connect(self.__clearCache)
        self.accepted.connect(self.__recordState)

        self.setWindowTitle("Preview Options")

    def recallState(self):
        self.get_settings()
        if not self.fast_zoom:
            self.fastZoomCheckBox.setChecked(False)
        self.sizeSlider.setValue(self.columns)
        if self.thumbnails_in_memory:
            self.cacheThumbnailsCheckBox.setChecked(False)

    def get_settings(self):
        try:
            with open('./' + self.settings_file, 'r') as file_object:
                settings = json.load(file_object)
        except FileNotFoundError:
            self.fast_zoom = True
            self.columns = 10
            self.thumbnails_in_memory = False
        else:
            self.fast_zoom = settings['fast_zoom']
            self.columns = settings['columns']
            self.thumbnails_in_memory = settings['thumbnails_in_memory']
        return self.fast_zoom, self.columns, self.thumbnails_in_memory

    def __recordState(self):
        self.fast_zoom = self.fastZoomCheckBox.isChecked()
        self.columns = self.sizeSlider.value()
        self.thumbnails_in_memory = not self.cacheThumbnailsCheckBox.isChecked()

        settings = dict(fast_zoom=self.fast_zoom,
                        thumbnails_in_memory=self.thumbnails_in_memory,
                        columns=self.columns
                        )
        with open('./' + self.settings_file, 'w') as file_object:
            json.dump(settings, file_object, indent=4)

    def __clearCache(self):
        cache_folder = "./thumbnails cache/"
        filenames = [f for f in os.listdir(cache_folder) if os.path.isfile(os.path.join(cache_folder, f))]
        # ~ [print(filename) for filename in filenames]
        [os.remove(cache_folder + filename) for filename in filenames]


class HThumbnailButton(QPushButton):
    def __init__(self, parent, path):
        super().__init__(parent)
        self.path = path


class PreviewWidget(QWidget):
    """
    thumbnails_in_memory=True
    - thumbnails will be generated in memory each time preview mode is started
    - images with transparent backgounds will show white  background in their thumbnails
    - slower thumbnail generation for large number of file

    thumbnails_in_memory=False:
    - thumbnails will be saved to the drive
    - thumbnails will not be re-generated unless thumbnail size is increased
    - images with transparent backgounds will show white  background in their thumbnails
    - faster thumbnail generation for large number of file after initial thumbnail generation is complete
    - thumbnails are automatically re-generated if the image files change/are edited (i.e. adler32 sum is different)
    """

    def __init__(self, parent, HVDB, width, columns=10, thumbnails_in_memory=False):  # have to pass width here from mainWindow because calling .size() on widgets from here give incorrectly small size for some weird reason
        super().__init__(parent)

        self.parent = parent
        self.hvdb = HVDB

        self.paths = self.hvdb.get_image_paths()
        self.columns = columns
        self.column_width = int(width / self.columns)  # button size accepts int
        # ~ print(f"width → {width}")
        # ~ print(f"self.column_width → {self.column_width}")
        self.cache_folder = "./thumbnails cache/"
        self.json_checksums_file = "checksums.json"
        os.makedirs(os.path.dirname(self.cache_folder), exist_ok=True)  # create dir if not exists

        self.interrupt = False

        if thumbnails_in_memory:
            self.__populateInMemory()
        else:
            self.__populateFromCache()

    def __initLayout(self):
        self.layout = QHBoxLayout(self)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.thumbnail_layout = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout.addWidget(self.scrollArea)

    def __initProgressDialog(self):
        self.progressDialog = QProgressDialog("Preparing thumbnails...",
                                              "Cancel",
                                              0,
                                              len(self.paths),
                                              self,
                                              )
        self.progressDialog.setWindowTitle("Preparing thumbnails...")
        self.progressDialog.setWindowModality(QtCore.Qt.WindowModal)  # if modality is not set, the progress dialog will be blank
        self.progressDialog.canceled.connect(self.__interrupt)
        self.progressDialog.setMinimumDuration(0)

    def __interrupt(self):
        self.interrupt = True
        QMessageBox.about(self,
                          "Message",
                          "Thumbnail generation is cancelled by user: thumbnails will not appear for all images."
                          )

    def __populateInMemory(self):
        self.__initLayout()
        self.__initProgressDialog()

        row = 0
        column = 0
        progress = 0
        size = self.column_width, self.column_width
        for path in self.paths:
            if column == self.columns:
                column = 0
                row += 1

            memory_path = BytesIO()

            try:
                # JPEG writes less data to HDD and is a litter faster than BMP
                # thumbnails are about the same size in memory regardless of extension
                # BMP shows transparent background for vector images
                # PNG is very slow
                with Image.open(path) as image:
                    image = image.convert("RGB")
                    image.thumbnail(size)
                    with BytesIO() as memory_path:
                        image.save(memory_path, format="JPEG")
                        thumbnail = memory_path.getvalue()
            except MemoryError:
                QMessageBox.about(self,
                                  "Message",
                                  "Memory is full: thumbnails will not appear for all images."
                                  )
                self.progressDialog.reject()
                break
            else:
                button = HThumbnailButton(self, path)
                self.thumbnail_layout.addWidget(button, row, column)
                button.setFixedSize(QtCore.QSize(self.column_width,
                                                 self.column_width
                                                 )
                                    )
                pixmap = QPixmap()
                pixmap.loadFromData(thumbnail)
                icon = QIcon(pixmap)
                button.setIcon(icon)
                button.setIconSize(button.size())
                button.clicked.connect(self.__clicked)
                # ~ button.setFlat(True)  # sets button to be invisible → becomes visible on press
                column += 1
                progress += 1
                self.progressDialog.setValue(progress)
                if self.interrupt:
                    break

    def __populateFromCache(self):
        self.__initLayout()
        self.__initProgressDialog()

        self.__set_checksums()

        row = 0
        column = 0
        progress = 0
        size = self.column_width, self.column_width
        for path in self.paths:
            try:
                # keeping track of checksums for each file: if a file is changed, checksum will be different, and thumbnail will be regenerated
                with open(path, 'rb') as file_obj:
                    data = file_obj.read()
            except MemoryError:
                QMessageBox.about(self,
                                  "Message",
                                  "Memory is full: thumbnails will not appear for all images."
                                  )
                self.progressDialog.reject()
                break
            else:
                if column == self.columns:
                    column = 0
                    row += 1

                checksum = zlib.adler32(data)  # adler32 was chosen for its speed
                basename, ext = os.path.splitext(os.path.basename(path))
                filename = basename + ext + "_thumbnail" + ".jpeg"
                thumbnail_path = self.cache_folder + filename

                stored_checksum, columns = self.checksums.get(filename, (None, None))
                if stored_checksum and stored_checksum == checksum and columns <= self.columns:
                    pass  # same file and thumbnail file doesn't need to be upsampled
                else:
                    self.checksums.update({filename: (checksum, self.columns)})

                    # JPEG writes less data to HDD and is a litter faster than BMP
                    # thumbnails are about the same size in memory regardless of extension
                    # BMP shows transparent background for vector images
                    # PNG is very slow
                    with Image.open(path) as image:
                        image = image.convert("RGB")
                        image.thumbnail(size)
                        image.save(thumbnail_path, format="JPEG")

                button = HThumbnailButton(self, path)
                self.thumbnail_layout.addWidget(button, row, column)
                button.setFixedSize(QtCore.QSize(self.column_width,
                                                 self.column_width
                                                 )
                                    )
                icon = QIcon(thumbnail_path)
                button.setIcon(icon)
                button.setIconSize(button.size())
                button.clicked.connect(self.__clicked)
                # ~ button.setFlat(True)  # sets button to be invisible → becomes visible on press
                column += 1
                progress += 1
                self.progressDialog.setValue(progress)

                # saving checksums after each iteration: if the operation is interrupted, the checksums will be present for the newly generated thumbnails and thumbnail generation will restart where the operation left off
                self.__write_checksums()
                if self.interrupt:
                    break

    def __set_checksums(self):
        try:
            with open(self.cache_folder + self.json_checksums_file, 'r') as file_object:
                self.checksums = json.load(file_object)
        except FileNotFoundError:
            self.checksums = dict()
            self.__write_checksums()

    def __write_checksums(self):
        with open(self.cache_folder + self.json_checksums_file, 'w') as file_object:
            json.dump(self.checksums, file_object, indent=4)

    def __clicked(self):
        path = self.sender().path
        idx = self.paths.index(path)
        self.parent.switch_main_canvas()
        self.parent.canvas.goto_index(idx)
