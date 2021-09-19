import glob
import os
import re
import sys

FORMATS = ('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP', '.gif', '.GIF', '.tiff',
           '.TIFF')

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    ROOT_DIR = sys._MEIPASS
else:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sizeof_fmt(size, suffix='B'):
    """Get human readable file size.
    Args:
        size (int): File size.
        suffix (str): Suffix. Default: 'B'.
    Return:
        str: Formated file siz.
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(size) < 1024.0:
            return f'{size:3.1f} {unit}{suffix}'
        size /= 1024.0
    return f'{size:3.1f} Y{suffix}'


def get_img_list(folder, include_names=None, exclude_names=None, exact_exclude_names=None):
    """Get the image list in a folder.
    It also considers 'include' and 'exclude' strings.

    Args:
        folder (str): Folder path.
        include_names (list[str]): Included strings in image base names.
        exclude_names: (list[str]): Excluded strings in image base names.

    Returns:
        list[str]: Image list.
    """
    img_list = []
    if folder == '':
        folder = './'
    if exact_exclude_names is not None:
        for img_path in sorted(glob.glob(os.path.join(folder, '*'))):
            img_path = img_path.replace('\\', '/')
            base, ext = os.path.splitext(os.path.basename(img_path))
            if ext in FORMATS:
                basename = f'{base}{ext}'
                if basename not in exact_exclude_names:
                    img_list.append(img_path)
    else:
        # deal with include and exclude names
        for img_path in sorted(glob.glob(os.path.join(folder, '*'))):
            img_path = img_path.replace('\\', '/')
            base, ext = os.path.splitext(os.path.basename(img_path))
            if ext in FORMATS:
                if include_names is not None:
                    flag_add = False
                    for include_name in include_names:
                        if include_name in base:
                            flag_add = True
                elif exclude_names is not None:
                    flag_add = True
                    for exclude_name in exclude_names:
                        if exclude_name in base:
                            flag_add = False
                else:
                    flag_add = True
                if flag_add:
                    img_list.append(img_path)
    # natural sort for numbers in names
    img_list.sort(key=lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)])
    return img_list
