
from PyQt6.QtWidgets import QWidget, QLayout, QHBoxLayout, QVBoxLayout


class QuickBoxLayoutMixin:
    """A quick annex to the default QBoxLayout class. This mixin lets you specify spacing and contents margins in the
    constructor or defaults them to 0 (in the standard implementation they are defaulted to different values depending
    on the OS). An add() method is also added that provides a unified API for adding elements to the layout, and for
    convenience this method returns the self (useful in list comprehensions or one-line layout definitions) """

    def __init__(self, parent=None, spacing=0, contents_margins=(0, 0, 0, 0)):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.setContentsMargins(*contents_margins)

    def add(self, *items):
        """Unified adder method for adding items to the layout. Depending on the type of each argument, a different
        native add method is called (addWidget for widgets, addLayout for layouts, addSpacing for floats, addStretch
        for ints). If you wish to bundle an argument with an alignment flag you can wrap it in a tuple. You can also
        pass a stretch parameter.

        Example add(QWidget(), 10.0, 1, QLayout(), (QWidget(), Qt.AlignmentFlag.AlignVCenter, 1), etc.)"""

        for item in items:

            # Case: tuple=3 (widget, alignment, stretch), addWidget
            if type(item) is tuple and len(item) == 3 and isinstance(item[0], QWidget):
                widget, alignment, stretch = item
                self.addWidget(widget, alignment=alignment, stretch=stretch)

            # Case: tuple=2 (widget, alignment), addWidget
            elif type(item) is tuple and len(item) == 2 and isinstance(item[0], QWidget):
                widget, alignment = item
                self.addWidget(widget, alignment=alignment)

            # Case: tuple=2 (layout, stretch), addLayout
            elif type(item) is tuple and len(item) == 2 and isinstance(item[0], QLayout):
                layout, stretch = item
                self.addLayout(layout, stretch=stretch)

            # Case widget, addWidget
            elif isinstance(item, QWidget):
                self.addWidget(item)

            # Case layout, addLayout
            elif isinstance(item, QLayout):
                self.addLayout(item)

            # Case float, addSpacing [cast to int]
            elif type(item) is float:
                self.addSpacing(int(item))

            # Case int, addStretch
            elif type(item) is int:
                self.addStretch(item)

        return self


class QuickHBox(QuickBoxLayoutMixin, QHBoxLayout):
    pass


class QuickVBox(QuickBoxLayoutMixin, QVBoxLayout):
    pass
