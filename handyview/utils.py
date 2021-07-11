import cv2
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


def crop_images(img_list,
                rect_pos,
                patch_folder,
                enlarge_ratio=2,
                interpolation='bicubic',
                line_width=0,
                color='yellow',
                rect_folder=None):

    color_tb = {}
    color_tb['yellow'] = (0, 255, 255)
    color_tb['green'] = (0, 255, 0)
    color_tb['red'] = (0, 0, 255)
    color_tb['magenta'] = (255, 0, 255)
    color_tb['matlab_blue'] = (189, 114, 0)
    color_tb['matlab_orange'] = (25, 83, 217)
    color_tb['matlab_yellow'] = (32, 177, 237)
    color_tb['matlab_purple'] = (142, 47, 126)
    color_tb['matlab_green'] = (48, 172, 119)
    color_tb['matlab_liblue'] = (238, 190, 77)
    color_tb['matlab_brown'] = (47, 20, 162)
    color = color_tb[color]

    # make temp folder
    os.makedirs(patch_folder, exist_ok=True)
    if line_width > 0 and not os.path.exists(rect_folder):
        os.makedirs(rect_folder)

    start_h, start_w, len_h, len_w = rect_pos
    for i, path in enumerate(img_list):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        base_name = os.path.splitext(os.path.basename(path))[0]
        # crop patch
        if img.ndim == 2:
            patch = img[start_h:start_h + len_h, start_w:start_w + len_w]
        elif img.ndim == 3:
            patch = img[start_h:start_h + len_h, start_w:start_w + len_w, :]

        # enlarge patch if necessary
        if enlarge_ratio > 1:
            h, w, _ = patch.shape
            if interpolation == 'bicubic':
                interpolation = cv2.INTER_CUBIC
            elif interpolation == 'bilinear':
                interpolation = cv2.INTER_LINEAR
            elif interpolation == 'nearest':
                interpolation = cv2.INTER_NEAREST
            patch = cv2.resize(patch, (w * enlarge_ratio, h * enlarge_ratio), interpolation=interpolation)
        cv2.imwrite(os.path.join(patch_folder, base_name + '_patch.png'), patch)

        # draw rectangle
        if line_width > 0:
            img_rect = cv2.rectangle(img, (start_w, start_h), (start_w + len_w, start_h + len_h), color, line_width)
            cv2.imwrite(os.path.join(rect_folder, base_name + '_rect.png'), img_rect)
