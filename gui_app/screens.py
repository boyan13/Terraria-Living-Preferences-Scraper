
import pandas as pd

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtWidgets import QWidget, QPushButton, QProgressBar, QTableView, QLabel, QGridLayout

from gui_lib.basic import Panel
from gui_lib.quick_layouts import QuickHBox, QuickVBox


class StartScreen(Panel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.start_button = QPushButton('Start', self)  # Needs to be externally connected to an event
        QuickHBox(self).add((self.start_button, Qt.AlignmentFlag.AlignCenter))


class LoadingScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.max_value = 0  # The progress bar is 100 when this value is reached. (set in  init_progress())
        self.step = 0  # Increment progress bar by this amount (calculated in init_progress())
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedSize(250, 30)
        self.progress_bar.setValue(0)
        QuickHBox(self).add((self.progress_bar, Qt.AlignmentFlag.AlignCenter))

    def init_progress(self, max_value):
        """Reset the progress bar to 0, set a new max value, and calculate the increment step to use."""
        self.progress_bar.reset()  # Reset progress bar
        self.progress_bar.setValue(0)  # Initialize at 0
        self.max_value = max_value  # Set max value
        self.step = round(100 / self.max_value)  # Calculate the increment step

    def increment_progress(self):
        """Increment the progress bar based on the predefined step."""
        self.progress_bar.setValue(self.progress_bar.value() + self.step)


class TableScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.tables_count = 0  # The amount of currently displayed tables
        self.grid = QGridLayout(self)
        self.grid.setSpacing(15)
        self.grid.setContentsMargins(30, 0, 30, 0)

    def add_table(self, table_title: str, table_model: QAbstractTableModel):
        """Add a table to be displayed in this view."""

        label = QLabel(table_title, self)  # Create a table name label
        table = QTableView(self)  # Create a table view
        table.setModel(table_model)  # Assign the table model to the table view
        table.setMinimumSize(300, 200)  # Restrict minimum size
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)  # Allow column stretch

        # Add to layout
        i = self.tables_count // 3  # Determine row position
        j = self.tables_count % 3  # Determine col position
        self.grid.addLayout(QuickVBox().add(label, table), i, j)  # Add to grid layout
        self.tables_count += 1  # Increment amount of tables we are currently displaying
