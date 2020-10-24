from os import path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

ROOT_DIR = osp.join(osp.abspath(__file__), '../')


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
        slot=parent.refresh_img_list)


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
