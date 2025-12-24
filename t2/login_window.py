from PyQt6 import QtCore, QtGui, QtWidgets
from database_connection import DatabaseConnection

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        self.LoginWindow = LoginWindow
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.resize(1000, 600)
        self.centralwidget = QtWidgets.QWidget(parent=LoginWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        # Phần bên trái - Hình ảnh
        self.imageLabel = QtWidgets.QLabel(self.centralwidget)
        self.imageLabel.setObjectName("imageLabel")
        self.imageLabel.setStyleSheet("background-color: lightgray;")
        self.imageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Load hình ảnh
        pixmap = QtGui.QPixmap("thuvien_loginpage.jpg")
        self.imageLabel.setPixmap(pixmap.scaled(500, 600, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        self.imageLabel.setFixedWidth(500)
        self.horizontalLayout.addWidget(self.imageLabel)

        self.horizontalLayout.addSpacing(20)

        # Phần bên phải - Form đăng nhập
        self.loginWidget = QtWidgets.QWidget(self.centralwidget)
        self.loginWidget.setObjectName("loginWidget")
        self.loginWidget.setFixedWidth(400)
        self.loginLayout = QtWidgets.QVBoxLayout(self.loginWidget)
        self.loginLayout.setContentsMargins(20, 50, 20, 50)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setVerticalSpacing(20)

        # Tiêu đề "Đăng Nhập"
        self.label_dn = QtWidgets.QLabel("Đăng Nhập-Thủ Thư", self.loginWidget)
        self.label_dn.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_dn.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.loginLayout.addWidget(self.label_dn)

        # Trường Tài Khoản
        self.label_tk = QtWidgets.QLabel("Tài Khoản", self.loginWidget)
        self.lineEdit_tk = QtWidgets.QLineEdit(self.loginWidget)
        self.lineEdit_tk.setMinimumHeight(30)
        self.lineEdit_tk.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 5px;")
        self.formLayout.addRow(self.label_tk, self.lineEdit_tk)

        # Trường Mật khẩu
        self.label_mk = QtWidgets.QLabel("Mật khẩu", self.loginWidget)
        self.lineEdit_mk = QtWidgets.QLineEdit(self.loginWidget)
        self.lineEdit_mk.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEdit_mk.setMinimumHeight(30)
        self.lineEdit_mk.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 5px;")
        self.formLayout.addRow(self.label_mk, self.lineEdit_mk)

        self.loginLayout.addLayout(self.formLayout)

        # Thêm checkbox để chuyển đổi giữa đăng nhập và đăng ký
        self.toggle_checkbox = QtWidgets.QCheckBox("Sinh Viên", self.loginWidget)
        self.toggle_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                margin: 10px 0;
            }
        """)
        self.toggle_checkbox.stateChanged.connect(self.toggle_sign_up)
        self.loginLayout.addWidget(self.toggle_checkbox)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.pushButton = QtWidgets.QPushButton("Đăng Nhập", self.loginWidget)
        self.pushButton.clicked.connect(self.login_Manage)
        self.pushButton.setMinimumHeight(40)
        self.pushButton.setFixedSize(400, 30)
        self.pushButton.setStyleSheet(""" 
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.buttonLayout.addWidget(self.pushButton)
        self.buttonLayout.addStretch()

        self.loginLayout.addLayout(self.buttonLayout)
        self.loginLayout.addStretch()
        self.horizontalLayout.addWidget(self.loginWidget)
        self.horizontalLayout.addSpacing(20)

        LoginWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

        # Kết nối cơ sở dữ liệu qua DatabaseConnection
        self.db_connection = DatabaseConnection(
            server='HOANGNINHKHANG\\SQLEXPRESS',
            database='ndkm2',
            username='sa',
            password='sapassword'
        )
        self.db_connection.connect()

    def toggle_sign_up(self, state):
        if state == QtCore.Qt.CheckState.Checked.value:
            self.label_dn.setText("Đăng Nhập - Sinh Viên")
            self.pushButton.setText("Đăng Nhập")
            self.label_tk.setText("Mã Sinh Viên")
            self.lineEdit_mk.setEnabled(False)
            self.label_mk.setEnabled(False)
            self.pushButton.clicked.disconnect()
            self.pushButton.clicked.connect(self.login_Student)
        else:
            self.label_dn.setText("Đăng Nhập - Thủ Thư")
            self.pushButton.setText("Đăng Nhập")
            self.label_tk.setText("Tài Khoản")
            self.lineEdit_mk.setEnabled(True)
            self.label_mk.setEnabled(True)
            self.pushButton.clicked.disconnect()
            self.pushButton.clicked.connect(self.login_Manage)

    def retranslateUi(self, LoginWindow):
        _translate = QtCore.QCoreApplication.translate
        LoginWindow.setWindowTitle(_translate("LoginWindow", "Đăng Nhập"))

    def login_Manage(self):
        username = self.lineEdit_tk.text()
        password = self.lineEdit_mk.text()

        try:
            conn = self.db_connection
            cursor = conn.get_cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=? AND role='quanly'", (username, password))
            user = cursor.fetchone()

            if user:
                QtWidgets.QMessageBox.information(self.LoginWindow, "Thành công", "Đăng nhập thành công với quyền Quản lý!")
                self.openTrangChu(username, role="quanly")
            else:
                QtWidgets.QMessageBox.warning(self.LoginWindow, "Lỗi", "Tài khoản hoặc mật khẩu không đúng!")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self.LoginWindow, "Lỗi", f"Không thể kết nối hoặc có lỗi xảy ra: {e}")

    def login_Student(self):
        maSV = self.lineEdit_tk.text()

        if not maSV:
            QtWidgets.QMessageBox.warning(self.LoginWindow, "Lỗi", "Vui lòng nhập Mã sinh viên!")
            return

        try:
            conn = self.db_connection
            cursor = conn.get_cursor()
            cursor.execute("SELECT * FROM students WHERE ma_sv=?", (maSV,))
            student = cursor.fetchone()

            if student:
                QtWidgets.QMessageBox.information(self.LoginWindow, "Thành công", "Đăng nhập thành công với quyền Sinh viên!")
                self.openTrangChu(maSV, role="sinhvien")
            else:
                QtWidgets.QMessageBox.warning(self.LoginWindow, "Lỗi", "Mã sinh viên không tồn tại!")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self.LoginWindow, "Lỗi", f"Lỗi khi kiểm tra mã sinh viên: {e}")

    def openTrangChu(self, identifier, role):
        if role == "quanly":
            from frontPage import MySideBar  # Import giao diện quản lý
            self.window = MySideBar(identifier, role)
        elif role == "sinhvien":
            from ControlStudentWindow  import MyControl   # Import giao diện sinh viên
            self.window = MyControl(identifier, role)
        print(f"Identifier: {identifier}, Role: {role}")
        self.window.show()
        self.LoginWindow.close()