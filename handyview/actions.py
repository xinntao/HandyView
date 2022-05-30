from os import path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

from handyview.utils import ROOT_DIR


def new_action(parent, text, icon_name=None, shortcut=None, slot=None, checkable=False):
    """Factory producing differnet actions.

    Args:
        parent (class): Parent class.
        text (str): Shown text.
        icon_name (str): Icon name in the path. Default: None.
        shortcut (str): Keyboard shortcut. Default: None.
        slot (func): Slot function. Default: None.
        checkable (bool): Default: False.
    """
    action = QAction(text, parent)
    if icon_name:
        action.setIcon(QIcon(osp.join(ROOT_DIR, f'icons/{icon_name}')))
    if shortcut:
        action.setShortcut(shortcut)
    # trigger
    action.triggered.connect(slot)
    if checkable:
        action.setCheckable(True)
    return action


# ---------------------------------------
# open and history
# ---------------------------------------


def open(parent):
    """Show system open file dialog to open file."""
    return new_action(parent, 'Open', icon_name='open.png', shortcut='Ctrl+O', slot=parent.open_file_dialog)


def history(parent):
    """Show open history."""
    return new_action(parent, 'History', icon_name='history.png', slot=parent.open_history)


# ---------------------------------------
# refresh and index
# ---------------------------------------


def refresh(parent):
    """Refresh image lists."""
    return new_action(parent, 'Refresh', icon_name='refresh', shortcut='F5', slot=parent.refresh_img_list)


def goto_index(parent):
    """Jump to the input index of images."""
    return new_action(parent, 'Index', icon_name='index.png', shortcut='Ctrl+I', slot=parent.goto_index)


# ---------------------------------------
# include and exclude names
# ---------------------------------------


def include_file_name(parent):
    """Include file name."""
    return new_action(parent, 'Include', icon_name='include.png', slot=parent.include_file_name)


def exclude_file_name(parent):
    """Exclude file name."""
    return new_action(parent, 'Exclude', icon_name='exclude.png', slot=parent.exclude_file_name)


# ---------------------------------------
# compare and clear compare
# ---------------------------------------


def compare(parent):
    """Compare."""
    return new_action(parent, 'Compare', icon_name='compare.png', shortcut='F6', slot=parent.compare_folder)


def clear_compare(parent):
    """Clear comparison."""
    return new_action(parent, 'Clear Comp', icon_name='clear_comparison.png', slot=parent.clear_compare)


# ---------------------------------------
# canvas layouts
# ---------------------------------------


def switch_main_canvas(parent):
    return new_action(parent, 'Main', icon_name='main_canvas.png', slot=parent.switch_main_canvas)


def switch_compare_canvas(parent):
    return new_action(parent, 'Compare', icon_name='compare_canvas.png', slot=parent.switch_compare_canvas)


def switch_preview_canvas(parent):
    return new_action(parent, 'Preview', icon_name='preview_canvas.png', slot=parent.switch_preview_canvas)


# ---------------------------------------
# canvas tabs
# ---------------------------------------


def select_basic_tab(parent):
    return new_action(parent, 'Basic', icon_name='main_canvas.png', slot=parent.select_basic_tab)


def select_crop_tab(parent):
    return new_action(parent, 'Crop', icon_name='compare_canvas.png', slot=parent.select_crop_tab)


def select_video_tab(parent):
    return new_action(parent, 'Video', icon_name='preview_canvas.png', slot=parent.select_video_tab)


# ---------------------------------------
# help
# ---------------------------------------


def show_instruction_msg(parent):
    return new_action(parent, 'Help', icon_name='help.png', slot=parent.show_instruction_msg)


def set_fingerprint(parent):
    return new_action(parent, 'Fingerprint', icon_name='fingerprint.png', slot=parent.set_fingerprint)


# ---------------------------------------
# auto zoom
# ---------------------------------------
def auto_zoom(parent):
    return new_action(parent, 'Auto Zoom', icon_name='auto_zoom.png', slot=parent.auto_zoom)


def auto_zoom_dialog(parent):
    return new_action(parent, 'Auto Zoom', icon_name='auto_zoom.png', slot=parent.auto_zoom_dialog)
