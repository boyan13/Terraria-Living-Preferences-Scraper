
from PyQt6.QtWidgets import QWidget, QStackedWidget
from PyQt6.QtCore import Qt


class EnabledStyledBackgroundMixin:
    """A mixin that enables stylesheet styles to propagate by setting the WA_StyledBackground widget attribute."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


class Panel(EnabledStyledBackgroundMixin, QWidget):
    pass


class StackedPanel(EnabledStyledBackgroundMixin, QStackedWidget):
    pass
