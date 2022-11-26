
from typing import Union
from contextlib import contextmanager
import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QScrollArea, QHBoxLayout, QVBoxLayout, QGridLayout


def purge_layout(layout: Union[QVBoxLayout, QHBoxLayout]):
    """Clear all items from the passed layout recursively. Allows you to put the items in a new layout.
    The passed layout is destroyed."""

    for i in reversed(range(layout.count())):
        item = layout.takeAt(i)

        if hasattr(item, 'widget') and item.widget() is not None:
            item.widget().setParent(None)
        elif hasattr(item, 'layout') and item.layout() is not None:
            purge_layout(item.layout())
        else:
            layout.removeItem(item)

    QWidget().setLayout(layout)


def wrap_in_scroll_area(widget: QWidget, parent=None):
    """Add a scroll area to the passed widget and return the scroll area."""

    sarea = QScrollArea(parent)
    sarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    sarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    sarea.setWidget(widget)
    sarea.setWidgetResizable(True)
    return sarea


@contextmanager
def no_truncating():
    """Prevent pandas printing from truncating the output if it is too large, by temporarily disabling some
    restrictions."""

    max_rows = pd.get_option('display.max_rows')
    max_cols = pd.get_option('display.max_columns')
    width = pd.get_option('display.width')

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    try:
        yield

    finally:
        pd.set_option('display.max_rows', max_rows)
        pd.set_option('display.max_columns', max_cols)
        pd.set_option('display.width', width)
