
from pandas import DataFrame
from PyQt6.QtCore import Qt, QAbstractTableModel


class DataFrameTableModel(QAbstractTableModel):
    """Adapt a pandas DataFrame to a QAbstractTableModel."""

    def __init__(self, df: DataFrame):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parnet=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role in {Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole}:
                return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._df.columns[col]
        elif orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return self._df.index[col]
        else:
            return None
