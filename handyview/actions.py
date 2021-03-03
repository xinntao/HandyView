from os import path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

from handyview.utils import ROOT_DIR


def new_action(parent,
               text,
               icon_name=None,
               shortcut=None,
               slot=None,
               checkable=False):
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


# Actions for Menu bar and Tool bar


def open(parent):
    """Show system open file dialog to open file."""
    return new_action(
        parent,
        'Open',
        icon_name='open.png',
        shortcut='Ctrl+O',
        slot=parent.open_file_dialog)


def refresh(parent):
    """Refresh the image list."""
    return new_action(
        parent,
        'Refresh',
        icon_name='refresh',
        shortcut='F5',
        slot=parent.refresh_img_list)


def compare(parent):
    """Compare."""
    return new_action(
        parent,
        'Compare',
        icon_name='compare.png',
        shortcut='F6',
        slot=parent.compare_folder)


def clear_compare(parent):
    """Clear comparison."""
    return new_action(
        parent,
        'Clear comparison',
        icon_name='clear_comparison.png',
        slot=parent.clear_compare)


def history(parent):
    """History."""
    return new_action(
        parent, 'History', icon_name='history.png', slot=parent.open_history)


def exclude_file_name(parent):
    """Exclude file name."""
    return new_action(
        parent,
        'Exclude',
        icon_name='exclude.png',
        slot=parent.exclude_file_name)


def include_file_name(parent):
    """Include file name."""
    return new_action(
        parent,
        'Include',
        icon_name='include.png',
        slot=parent.include_file_name)


def show_instruction_msg(parent):
    return new_action(
        parent,
        'Instruct',
        icon_name='instructions.png',
        slot=parent.show_instruction_msg)


# ---------------------------------------
# Canvas
# ---------------------------------------


def switch_main_canvas(parent):
    return new_action(
        parent,
        'Main',
        icon_name='main_canvas.png',
        slot=parent.switch_main_canvas)


def switch_compare_canvas(parent):
    return new_action(
        parent,
        'Compare',
        icon_name='compare_canvas.png',
        slot=parent.switch_compare_canvas)


def switch_preview_canvas(parent):
    return new_action(
        parent,
        'Preview',
        icon_name='preview_canvas.png',
        slot=parent.switch_preview_canvas)
