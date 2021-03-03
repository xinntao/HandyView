import glob
# import itertools
import os
import sys
from PIL import Image
from utils import FORMATS, get_img_list, sizeof_fmt
from widgets import show_msg

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    CURRENT_PATH = sys._MEIPASS
else:
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class HVDB():
    """HandyView database.

    fidx: folder list
    pidx: path list


    """

    def __init__(self, init_path):
        self.init_path = init_path
        self._fidx = 0  # folder index
        self._pidx = 0  # path index
        self._include_names = None
        self._exclude_names = None

        self.folder_list = [None]
        # list of image path list
        # the first list is the main list
        self.path_list = [[]]

        self.get_init_path_list()

    def get_init_path_list(self):
        """get path list when first launch (double click or from cmd)"""
        # if init_path is a folder, try to get the first image
        if os.path.isdir(self.init_path):
            # self.init_path = sorted(
            #     list(
            #         itertools.chain(
            #             *(glob.glob(os.path.join(self.init_path, f'*.{ext}'))
            #               for ext in FORMATS))))
            self.init_path = sorted(
                glob.glob(os.path.join(self.init_path, '*')))[0]
        # TODO: update

        # fix the path pattern passed from windows system when double click
        self.init_path = self.init_path.replace('\\', '/')  # TODO: remove?

        if self.init_path.endswith(FORMATS):
            folder = os.path.dirname(self.init_path)
            self.folder_list[0] = folder
            # get path list
            self.path_list[0] = get_img_list(folder, self._include_names,
                                             self._exclude_names)
            # get current pidx
            try:
                self._pidx = self.path_list[0].index(self.init_path)
            except ValueError:
                # self.init_path may not in self.path_list after refreshing
                self._pidx = 0
            # save open file history
            self.save_open_history()
        else:
            show_msg('Critical', 'Critical',
                     f'Wrong init path! {self.init_path}')

    def save_open_history(self):
        try:
            with open(os.path.join(CURRENT_PATH, 'history.txt'), 'r') as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
                if len(lines) == 5:
                    del lines[-1]
        except Exception:
            lines = []
        # add the new record to the first line
        if self.init_path not in ['icon.png', './icon.png'] and (self.init_path
                                                                 not in lines):
            lines.insert(0, self.init_path)
        with open(os.path.join(CURRENT_PATH, 'history.txt'), 'w') as f:
            for line in lines:
                f.write(f'{line}\n')

    def path_browse(self, step):
        if self.get_path_len() > 1:
            self._pidx += step
            if self._pidx > (self.get_path_len() - 1):
                self._pidx = 0
            elif self._pidx < 0:
                self._pidx = self.get_path_len() - 1

    def folder_browse(self, step):
        if self.get_folder_len() > 1:
            self._fidx += step
            if self._fidx > (self.get_folder_len() - 1):
                self._fidx = 0
            elif self._fidx < 0:
                self._fidx = self.get_folder_len() - 1
            # if folders have different images, may rise index error
            try:
                self.get_path()
            except IndexError:
                self._pidx = self.get_path_len() - 1

    def update_cmp_path_list(self, cmp_path):
        folder = os.path.dirname(cmp_path)
        self.folder_list.append(folder)
        self.path_list.append(
            get_img_list(folder, self._include_names, self._exclude_names))
        # all the path list should have the same length
        is_same_len = True
        img_len_list = [len(self.path_list[0])]
        for img_list in self.path_list[1:]:
            img_len_list.append(len(img_list))
            if len(img_list) != img_len_list[0]:
                is_same_len = False
        return is_same_len, img_len_list

    def get_folder(self, folder=None, fidx=None):
        if folder is None:
            if fidx is None:
                fidx = self._fidx
            folder = self.folder_list[fidx]
        return folder

    def get_path(self, path=None, fidx=None, pidx=None):
        if path is None:
            if fidx is None:
                fidx = self._fidx
            if pidx is None:
                pidx = self._pidx
            path = self.path_list[fidx][pidx]
        return path

    def get_shape(self, path=None, fidx=None, pidx=None):
        path = self.get_path(path, fidx, pidx)
        try:
            with Image.open(path) as lazy_img:
                width, height = lazy_img.size
        except FileNotFoundError:
            show_msg('Critical', 'Critical', f'Cannot open {path}')
        return width, height

    def get_color_type(self, path=None, fidx=None, pidx=None):
        path = self.get_path(path, fidx, pidx)
        try:
            with Image.open(path) as lazy_img:
                color_type = lazy_img.mode
        except FileNotFoundError:
            show_msg('Critical', 'Critical', f'Cannot open {path}')
        return color_type

    def get_file_size(self, path=None, fidx=None, pidx=None):
        # TODO: use a list for cache
        path = self.get_path(path, fidx, pidx)
        file_size = sizeof_fmt(os.path.getsize(path))
        return file_size

    def get_folder_len(self):
        return len(self.folder_list)

    def get_path_len(self, fidx=None):
        if fidx is None:
            fidx = self._fidx
        return len(self.path_list[fidx])

    @property
    def fidx(self):
        return self._fidx

    @fidx.setter
    def fidx(self, value):
        if value > (self.get_folder_len() - 1):
            self._fidx = self.get_folder_len() - 1
        elif value < 0:
            self._fidx = 0
        else:
            self._fidx = value

    @property
    def pidx(self):
        return self._pidx

    @pidx.setter
    def pidx(self, value):
        if value > (self.get_path_len() - 1):
            self._pidx = self.get_path_len() - 1
        elif value < 0:
            self._pidx = 0
        else:
            self._pidx = value

    @property
    def include_names(self):
        return self._include_names

    @include_names.setter
    def include_names(self, value):
        self._include_names = value
        # TODO: out of boundary check

    @property
    def exclude_names(self):
        return self._exclude_names

    @exclude_names.setter
    def exclude_names(self, value):
        self._exclude_names = value
        # TODO: out of boundary check
