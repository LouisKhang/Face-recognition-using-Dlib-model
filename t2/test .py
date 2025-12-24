from PyQt6.QtWidgets import QApplication,QMainWindow
from frontPage import MySideBar
from login_window import Ui_LoginWindow
import sys
def main():
    app = QApplication(sys.argv)
    window = MySideBar()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()