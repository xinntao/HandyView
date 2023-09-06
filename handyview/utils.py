import os
import re
import sys
from PIL import Image, ImageDraw

FORMATS = ('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP', '.gif', '.GIF', '.tiff',
           '.TIFF', '.webp', '.WEBP')

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


def scandir(dir_path, suffix=None, recursive=False, full_path=False):
    """Scan a directory to find the interested files.

    Args:
        dir_path (str): Path of the directory.
        suffix (str | tuple(str), optional): File suffix that we are
            interested in. Default: None.
        recursive (bool, optional): If set to True, recursively scan the
            directory. Default: False.
        full_path (bool, optional): If set to True, include the dir_path.
            Default: False.

    Returns:
        A generator for all the interested files with relative pathes.
    """

    if (suffix is not None) and not isinstance(suffix, (str, tuple)):
        raise TypeError('"suffix" must be a string or tuple of strings')

    root = dir_path

    def _scandir(dir_path, suffix, recursive):
        try:
            for entry in os.scandir(dir_path):
                if not entry.name.startswith('.') and entry.is_file():
                    if full_path:
                        return_path = entry.path
                    else:
                        return_path = os.path.relpath(entry.path, root)

                    if suffix is None:
                        yield return_path
                    elif return_path.endswith(suffix):
                        yield return_path
                else:
                    if recursive:
                        yield from _scandir(entry.path, suffix=suffix, recursive=recursive)
                    else:
                        continue
        except Exception:
            return_path = os.path.relpath(entry.path, root)

    return _scandir(dir_path, suffix=suffix, recursive=recursive)


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
        for img_path in sorted(scandir(folder, suffix=None, recursive=False, full_path=True)):
            img_path = img_path.replace('\\', '/')
            base, ext = os.path.splitext(os.path.basename(img_path))
            if ext in FORMATS:
                basename = f'{base}{ext}'
                if basename not in exact_exclude_names:
                    img_list.append(img_path)
    else:
        # deal with include and exclude names
        for img_path in sorted(scandir(folder, suffix=None, recursive=False, full_path=True)):
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
    # in BGR
    # color_tb['yellow'] = (0, 255, 255)
    # color_tb['green'] = (0, 255, 0)
    # color_tb['red'] = (0, 0, 255)
    # color_tb['magenta'] = (255, 0, 255)
    # color_tb['matlab_blue'] = (189, 114, 0)
    # color_tb['matlab_orange'] = (25, 83, 217)
    # color_tb['matlab_yellow'] = (32, 177, 237)
    # color_tb['matlab_purple'] = (142, 47, 126)
    # color_tb['matlab_green'] = (48, 172, 119)
    # color_tb['matlab_liblue'] = (238, 190, 77)
    # color_tb['matlab_brown'] = (47, 20, 162)
    # in RGB
    color_tb['yellow'] = (255, 255, 0)
    color_tb['green'] = (0, 255, 0)
    color_tb['red'] = (255, 0, 0)
    color_tb['magenta'] = (255, 0, 255)
    color_tb['matlab_blue'] = (0, 114, 189)
    color_tb['matlab_orange'] = (217, 83, 25)
    color_tb['matlab_yellow'] = (237, 177, 32)
    color_tb['matlab_purple'] = (126, 47, 142)
    color_tb['matlab_green'] = (119, 172, 48)
    color_tb['matlab_liblue'] = (77, 190, 238)
    color_tb['matlab_brown'] = (162, 20, 47)
    color = color_tb[color]

    # make temp folder
    os.makedirs(patch_folder, exist_ok=True)
    if line_width > 0 and not os.path.exists(rect_folder):
        os.makedirs(rect_folder)

    start_h, start_w, len_h, len_w = rect_pos
    for i, path in enumerate(img_list):
        img = Image.open(path)
        base_name = os.path.splitext(os.path.basename(path))[0]
        # crop patch
        patch = img.crop((start_w, start_h, start_w + len_w, start_h + len_h))

        # enlarge patch if necessary
        if enlarge_ratio > 1:
            w, h = patch.size
            if interpolation == 'bicubic':
                interpolation = Image.BICUBIC
            elif interpolation == 'bilinear':
                interpolation = Image.BILINEAR
            elif interpolation == 'nearest':
                interpolation = Image.NEAREST
            patch = patch.resize((w * enlarge_ratio, h * enlarge_ratio), resample=interpolation)
        patch.save(os.path.join(patch_folder, base_name + '_patch.png'))

        # draw rectangle
        if line_width > 0:
            img_rect = img.convert('RGB')
            draw = ImageDraw.Draw(img_rect)
            draw.rectangle(((start_w, start_h), (start_w + len_w, start_h + len_h)), outline=color, width=line_width)
            img_rect.save(os.path.join(rect_folder, base_name + '_rect.png'))
