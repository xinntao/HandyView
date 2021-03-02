import glob
import os
import re

FORMATS = ('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.ppm', '.PPM',
           '.bmp', '.BMP', '.gif', '.GIF', '.tiff')


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


def get_img_list(path, include_names=None, exclude_names=None):
    img_list = []
    if path == '':
        path = './'
    # deal with include and exclude names
    for img_path in sorted(glob.glob(os.path.join(path, '*'))):
        img_path = img_path.replace('\\', '/')
        img_name = os.path.split(img_path)[-1]
        base, ext = os.path.splitext(img_name)
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
    # natural sort for numbers in name
    img_list.sort(
        key=lambda s:
        [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)])
    return img_list
