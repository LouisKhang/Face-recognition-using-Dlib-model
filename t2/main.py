from PyQt6.QtWidgets import QApplication,QMainWindow
from frontPage import MySideBar
# from test2 import MySideBar
from login_window import Ui_LoginWindow
import sys
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_LoginWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
