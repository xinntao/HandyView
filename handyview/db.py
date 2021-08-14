import glob
import hashlib
import imagehash
import itertools
import os
import re
from PIL import Image

from handyview.utils import FORMATS, ROOT_DIR, sizeof_fmt
from handyview.widgets import show_msg


class HVDB():
    """HandyView database.

    fidx(int): folder index
    __fidx(int): folder index
    pidx(int): path index
    __pidx(int): path index

    Attributes:
        init_path (str): e.g. 'D:\HandyView-0.4.3'
        folder_list (list(list)): e.g. ['D:\\HandyView-0.4.3'], folder beyond idx=0 are comparison folders
        path_list (list(list)): e.g. [['D:\\HandyView-0.4.3\\icon.png', 'D:\\HandyView-0.4.3\\icon_2.png']]
        file_size_list (list(list)): e.g. [[None, None]]
        md5_list (list(list)): e.g. [[None, None]]
        phash_list (list(list)): e.g. [[None, None]]
        is_same_len (bool):
        _include_names(str): partial or full image basename
        _exclude_names(str): partial or full image basename
        _exact_exclude_names(str): image filename

        _interval(int): for compare canvas
    """

    def __init__(self, init_path):
        self.init_path = init_path
        self.folder_list = [None]

        self.__fidx = 0  # folder index
        self.__pidx = 0  # path index
        self.__include_names = None
        self.__exclude_names = None
        self.__exact_exclude_names = None
        self._interval = 0  # for compare canvas

        # whether path lists in compare folders have the same length
        self.is_same_len = True

        # list of image path list
        # the first list is the main list
        self.path_list = [[]]
        self.file_size_list = [[]]
        self.md5_list = [[]]
        self.phash_list = [[]]
        self.initialize()

    @property
    def fidx(self):
        return self.__fidx

    @fidx.setter
    def fidx(self, value):
        if value > (self.get_folder_count() - 1):
            self.__fidx = self.get_folder_count() - 1
        elif value < 0:
            self.__fidx = 0
        else:
            self.__fidx = value

    @property
    def pidx(self):
        return self.__pidx

    @pidx.setter
    def pidx(self, value):
        if value > (self.get_image_count() - 1):
            self.__pidx = self.get_image_count() - 1
        elif value < 0:
            self.__pidx = 0
        else:
            self.__pidx = value

    @property
    def include_names(self):
        return self.__include_names

    @include_names.setter
    def include_names(self, value):
        self.__include_names = value
        # TODO: move check from handyviewer.py here

    @property
    def exclude_names(self):
        return self.__exclude_names

    @exclude_names.setter
    def exclude_names(self, value):
        self.__exclude_names = value
        # TODO: move check from handyviewer.py here

    @property
    def exact_exclude_names(self):
        return self.__exact_exclude_names

    @exact_exclude_names.setter
    def exact_exclude_names(self, value):
        self.__exact_exclude_names = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = value

    def __get_first_image_path(self, path):
        if os.path.isdir(path):
            found_image_files = [glob.glob(os.path.join(path, f'*{ext}')) for ext in FORMATS]
            while [] in found_image_files:  # will have a bunch of empty lists for not found extension types
                found_image_files.remove([])
            path = sorted(
                          list(
                               itertools.chain(*found_image_files)
                               )
                          )[0]

        return os.path.normpath(path)  # fix the path pattern passed from windows system when double click ← YGT: some method os.path change path delimeter to '\\' by default

    def __set_init_path(self):
        self.init_path = self.__get_first_image_path(self.init_path)

    def __get_filtered_image_paths(self,
                                  folder,
                                  include_names=None,
                                  exclude_names=None,
                                  exact_exclude_names=None):
        """Get the image list in a folder.
        It also considers 'include' and 'exclude' strings.

        Args:
            folder (str): Folder path.
            include_names (list[str]): image base names.
            exclude_names (list[str]): image base names
            exact_exclude_names (list[str]): not currently used by the app

        Returns:
            list[str]: Image path list.

        Deleted Parameters:
            exclude_names: (list[str]): Excluded strings in image base names.
        """
        if not folder:
            folder = './'

        img__paths__basenames__filenames = list()
        for file_path in sorted(glob.glob(os.path.join(folder, '*'))):
            file_path = os.path.normpath(file_path)
            basename, ext = os.path.splitext(os.path.basename(file_path))
            if ext in FORMATS:
                img__paths__basenames__filenames.append(
                                                        (file_path,
                                                         basename,
                                                         f'{basename}{ext}',
                                                         )
                                                        )
        if exact_exclude_names:
            img_paths = [path for path, basename, filename in img__paths__basenames__filenames if filename not in exact_exclude_names]
        else:
            img_paths = list()
            for path, basename, filename in img__paths__basenames__filenames:
                if include_names:
                    included = any([True for include_name in include_names if include_name in basename])
                    flag_add = included
                elif exclude_names:
                    excluded = any([True for exclude_name in exclude_names if exclude_name in basename])
                    flag_add = not excluded
                else:
                    flag_add = True
                if flag_add:
                    img_paths.append(path)

        # natural sort for numbers in names
        img_paths.sort(
                       key=lambda string:
                       [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', string)])
        return img_paths

    def __set_path_list_and_db_placeholders(self, idx, paths):
        """ placeholder = [None] * len(paths) """
        try:
            self.path_list[idx]
        except IndexError:  # raised in self.add_cmp_folder because idx will not exist, and need to append to lists instead of replacing
            self.path_list.insert(idx, paths)
            # for each image path in the image list, fills the below properties with None placeholders
            self.file_size_list.insert(idx, [None] * len(paths))
            self.md5_list.insert(idx, [None] * len(paths))
            self.phash_list.insert(idx, [None] * len(paths))
        else:  # replacing
            self.path_list[idx] = paths
            # for each image path in the image list, fills the below properties with None placeholders
            self.file_size_list[idx] = [None] * len(paths)
            self.md5_list[idx] = [None] * len(paths)
            self.phash_list[idx] = [None] * len(paths)

    def __initialize_folder(self, idx, path, path_is_folder=False):
        if not path_is_folder:
            folder = os.path.dirname(path)
        else:
            folder = path

        try:
            self.folder_list[idx] = folder
        except IndexError:  # will be raised by seld.add_cmp_folder because idx == folder count
            self.folder_list.insert(idx, folder)
        # get path list
        image_paths = self.__get_filtered_image_paths(folder,
                                                      self.__include_names,
                                                      self.__exclude_names,
                                                      self.__exact_exclude_names)
        # ~ print(f"image_paths = {image_paths}")
        self.__set_path_list_and_db_placeholders(idx, image_paths)

    def __validate_folders_have_same_image_counts(self):
        self.is_same_len = True
        image_counts = [len(self.path_list[0])]
        main_path_image_count = image_counts[0]
        for img_path_list in self.path_list[1:]:
            image_counts.append(len(img_path_list))
            if len(img_path_list) != main_path_image_count:
                self.is_same_len = False
        return self.is_same_len, image_counts

    def __check_idx(self, idx, count_func):
        """ checks if fidx or pidx is outside of available indices, and resets it """

        is_idx_outside = idx > (count_func() - 1)
        is_idx_negative = idx < 0
        if is_idx_outside:
            idx = 0  # reset idx to first
        elif is_idx_negative:
            idx = count_func() - 1  # reset idx to last
        return idx  # resets idx if outside of availability

    def __save_open_history(self):
        path = os.path.join(ROOT_DIR, 'history.txt')
        max_history_items = 5
        try:
            with open(path, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []
        else:
            lines = [line.strip() for line in lines]
            if len(lines) == max_history_items:
                del lines[-1]

        # add the new record to the first line
        # ~ if self.init_path not in ['icon.png', './icon.png'] and (self.init_path not in lines):
        if self.init_path not in lines:
            lines.insert(0, self.init_path)
        # shuffles the path to the first position if already present
        elif self.init_path in lines:
            ix = lines.index(self.init_path)
            lines.pop(ix)
            lines.insert(0, self.init_path)
        with open(path, 'w') as f:
            for line in lines:
                f.write(f'{line}\n')

    def initialize(self):
        """get path list when first launch (double click or from cmd)"""
        # if init_path is a folder, try to get the first image
        self.__set_init_path()

        if not self.init_path.endswith(FORMATS):
            show_msg(self, 'Critical', 'Critical',
                     f'Wrong init path! {self.init_path}')
            return None

        idx = 0
        self.__initialize_folder(idx, self.init_path)

        # get current pidx
        try:
            self.__pidx = self.path_list[0].index(self.init_path)
        except ValueError:
            # self.init_path may not in self.path_list after refreshing
            self.__pidx = 0
        # save open file history
        self.__save_open_history()

    def add_cmp_folder(self, cmp_path):
        idx = len(self.folder_list)
        self.__initialize_folder(idx, cmp_path)

        return self.__validate_folders_have_same_image_counts()

    def update_path_list(self):
        for idx, folder in enumerate(self.folder_list):
            self.__initialize_folder(idx, folder, path_is_folder=True)

        return self.__validate_folders_have_same_image_counts()

    def get_folder_count(self):  # returns count=main folder + comparison folders
        return len(self.folder_list)

    def get_image_count(self, fidx=None):  # returns image count
        if fidx is None:
            fidx = self.__fidx
        return len(self.path_list[fidx])

    def path_browse(self, step):
        if self.get_image_count() > 1:
            self.__pidx += step * (self._interval + 1)
            self.__pidx = self.__check_idx(self.__pidx, self.get_image_count)

    def folder_browse(self, step):
        if self.get_folder_count() > 1:
            self.__fidx += step
            self.__fidx = self.__check_idx(self.__fidx, self.get_folder_count)
            # if folders have different images, may rise index error
            try:
                self.get_img_path()
            except IndexError:
                self.__pidx = self.get_image_count() - 1

    def get_folder(self, fidx=None):
        if fidx is None:
            fidx = self.__fidx

        folder = self.folder_list[fidx]
        return folder

    def get_img_path(self, fidx=None, pidx=None):
        if fidx is None:
            fidx = self.__fidx
        if pidx is None:
            pidx = self.__pidx

        fidx = self.__check_idx(fidx, self.get_folder_count)
        pidx = self.__check_idx(pidx, self.get_image_count)

        path = self.path_list[fidx][pidx]
        return path, fidx, pidx

    def get_shape(self, fidx=None, pidx=None):
        path, _, _ = self.get_img_path(fidx, pidx)
        try:
            with Image.open(path, mode='r') as lazy_img:
                width, height = lazy_img.size
        except FileNotFoundError:
            show_msg(self, 'Critical', 'Critical', f'Cannot open {path}')
        return width, height

    def get_color_type(self, fidx=None, pidx=None):
        path, _, _ = self.get_img_path(fidx, pidx)
        try:
            with Image.open(path, mode='r') as lazy_img:
                color_type = lazy_img.mode
        except FileNotFoundError:
            show_msg(self, 'Critical', 'Critical', f'Cannot open {path}')
        return color_type

    def get_file_size(self, fidx=None, pidx=None):
        path, fidx, pidx = self.get_img_path(fidx, pidx)
        file_size = self.file_size_list[fidx][pidx]
        if file_size is None:
            file_size = sizeof_fmt(os.path.getsize(path))
            self.file_size_list[fidx][pidx] = file_size
        return file_size

    def get_fingerprint(self, fidx=None, pidx=None):
        path, fidx, pidx = self.get_img_path(fidx, pidx)
        # md5
        md5 = self.md5_list[fidx][pidx]
        if md5 is None:
            with open(path, 'rb') as file_obj:
                data = file_obj.read()
            md5 = hashlib.md5(data).hexdigest()
            self.md5_list[fidx][pidx] = md5
        # phash (perceptual hash)
        phash = self.phash_list[fidx][pidx]
        if phash is None:
            with Image.open(path, mode='r') as lazy_img:
                phash = imagehash.phash(lazy_img)
            self.phash_list[fidx][pidx] = phash
        return (md5, phash)

    def get_image_paths(self):  # used in PreviewWidget
        # ~ print(f"self.folder_list = {self.folder_list}")
        main_view_folder = self.folder_list[0]
        # ~ main_view_folder = os.path.normpath(main_view_folder)
        # ~ print(f"main_view_folder = {main_view_folder}")
        return self.__get_filtered_image_paths(main_view_folder,
                                               self.__include_names,
                                               self.__exclude_names,
                                               self.__exact_exclude_names)
