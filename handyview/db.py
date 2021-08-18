import hashlib
import imagehash
import os
from PIL import Image

from handyview.utils import FORMATS, ROOT_DIR, get_img_list, scandir, sizeof_fmt
from handyview.widgets import show_msg


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
        self._exact_exclude_names = None
        self._interval = 0  # for compare canvas

        # whether path lists in compare folders have the same length
        self.is_same_len = True

        self.folder_list = [None]
        # list of image path list
        # the first list is the main list
        self.path_list = [[]]
        self.file_size_list = [[]]
        self.md5_list = [[]]
        self.phash_list = [[]]

        # for selection pos in crop canvas
        self.selection_pos = [0, 0, 0, 0]

        self.recursive_scan_folder = False

        self.get_init_path_list()

    def get_init_path_list(self):
        """get path list when first launch (double click or from cmd)"""
        # if init_path is a folder, try to get the first image
        if os.path.isdir(self.init_path):
            self.recursive_scan_folder = True
            self.path_list[0] = list(scandir(self.init_path, suffix=FORMATS, recursive=True, full_path=True))
            self.init_path = self.path_list[0][0]

        # fix the path pattern passed from windows system when double click
        self.init_path = self.init_path.replace('\\', '/')

        if self.init_path.endswith(FORMATS):
            folder = os.path.dirname(self.init_path)
            self.folder_list[0] = folder
            # get path list
            if self.recursive_scan_folder is False:
                self.path_list[0] = get_img_list(folder, self._include_names, self._exclude_names,
                                                 self._exact_exclude_names)
            self.file_size_list[0] = [None] * len(self.path_list[0])
            self.md5_list[0] = [None] * len(self.path_list[0])
            self.phash_list[0] = [None] * len(self.path_list[0])
            # get current pidx
            try:
                self._pidx = self.path_list[0].index(self.init_path)
            except ValueError:
                # self.init_path may not in self.path_list after refreshing
                self._pidx = 0
            # save open file history
            self.save_open_history()
        else:
            show_msg('Critical', 'Critical', f'Wrong init path! {self.init_path}')

    def save_open_history(self):
        try:
            with open(os.path.join(ROOT_DIR, 'history.txt'), 'r') as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
                if len(lines) == 5:
                    del lines[-1]
        except Exception:
            lines = []
        # add the new record to the first line
        if self.init_path not in ['icon.png', './icon.png'] and (self.init_path not in lines):
            lines.insert(0, self.init_path)
        with open(os.path.join(ROOT_DIR, 'history.txt'), 'w') as f:
            for line in lines:
                f.write(f'{line}\n')

    def path_browse(self, step):
        if self.get_path_len() > 1:
            self._pidx += step * (self._interval + 1)
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

    def add_cmp_folder(self, cmp_path):
        folder = os.path.dirname(cmp_path)
        self.folder_list.append(folder)
        paths = get_img_list(folder, self._include_names, self._exclude_names, self._exact_exclude_names)
        self.path_list.append(paths)
        self.file_size_list.append([None] * len(paths))
        self.md5_list.append([None] * len(paths))
        self.phash_list.append([None] * len(paths))
        # all the path list should have the same length
        self.is_same_len = True
        img_len_list = [len(self.path_list[0])]
        for img_list in self.path_list[1:]:
            img_len_list.append(len(img_list))
            if len(img_list) != img_len_list[0]:
                self.is_same_len = False
        return self.is_same_len, img_len_list

    def update_path_list(self):
        if self.recursive_scan_folder is False:
            for idx, folder in enumerate(self.folder_list):
                paths = get_img_list(folder, self._include_names, self._exclude_names, self._exact_exclude_names)
                self.path_list[idx] = paths
                self.file_size_list[idx] = [None] * len(paths)
                self.md5_list[idx] = [None] * len(paths)
                self.phash_list[idx] = [None] * len(paths)

        # all the path list should have the same length
        self.is_same_len = True
        img_len_list = [len(self.path_list[0])]
        for img_list in self.path_list[1:]:
            img_len_list.append(len(img_list))
            if len(img_list) != img_len_list[0]:
                self.is_same_len = False
        return self.is_same_len, img_len_list

    def get_folder(self, folder=None, fidx=None):
        if folder is None:
            if fidx is None:
                fidx = self._fidx
            folder = self.folder_list[fidx]
        return folder

    def get_path(self, fidx=None, pidx=None):
        if fidx is None:
            fidx = self._fidx
        if pidx is None:
            pidx = self._pidx
        # check out of boundary
        if fidx > (self.get_folder_len() - 1):
            fidx = 0
        elif fidx < 0:
            fidx = self.get_folder_len() - 1
        if pidx > (self.get_path_len() - 1):
            pidx = 0
        elif pidx < 0:
            pidx = self.get_path_len() - 1

        path = self.path_list[fidx][pidx]
        return path, fidx, pidx

    def get_shape(self, fidx=None, pidx=None):
        path = self.get_path(fidx, pidx)[0]
        try:
            with Image.open(path) as lazy_img:
                width, height = lazy_img.size
        except FileNotFoundError:
            show_msg('Critical', 'Critical', f'Cannot open {path}')
        return width, height

    def get_color_type(self, fidx=None, pidx=None):
        path = self.get_path(fidx, pidx)[0]
        try:
            with Image.open(path) as lazy_img:
                color_type = lazy_img.mode
        except FileNotFoundError:
            show_msg('Critical', 'Critical', f'Cannot open {path}')
        return color_type

    def get_file_size(self, fidx=None, pidx=None):
        path, fidx, pidx = self.get_path(fidx, pidx)
        file_size = self.file_size_list[fidx][pidx]
        if file_size is None:
            file_size = sizeof_fmt(os.path.getsize(path))
            self.file_size_list[fidx][pidx] = file_size
        return file_size

    def get_fingerprint(self, fidx=None, pidx=None):
        path, fidx, pidx = self.get_path(fidx, pidx)
        # md5
        md5 = self.md5_list[fidx][pidx]
        if md5 is None:
            data = open(path, 'rb').read()
            md5 = hashlib.md5(data).hexdigest()
            self.md5_list[fidx][pidx] = md5
        # phash (perceptual hash)
        phash = self.phash_list[fidx][pidx]
        if phash is None:
            phash = imagehash.phash(Image.open(path))
            self.phash_list[fidx][pidx] = phash
        return (md5, phash)

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
        # TODO: move check from handyviewer.py here

    @property
    def exclude_names(self):
        return self._exclude_names

    @exclude_names.setter
    def exclude_names(self, value):
        self._exclude_names = value
        # TODO: move check from handyviewer.py here

    @property
    def exact_exclude_names(self):
        return self._exact_exclude_names

    @exact_exclude_names.setter
    def exact_exclude_names(self, value):
        self._exact_exclude_names = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = value
