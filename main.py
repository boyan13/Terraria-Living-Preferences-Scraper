
import sys
from PyQt6.QtWidgets import QApplication
from gui_app.app import AppWindow


def main():
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
