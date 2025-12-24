from PyQt6.QtWidgets import (
    QMainWindow, QTableWidgetItem, QMessageBox, QHBoxLayout,QVBoxLayout,  QWidget, QPushButton, QDialog
)
from PyQt6.QtGui import QIcon,QPixmap, QImage
from PyQt6.QtCore import QSize, QTimer, Qt, QDate, pyqtSignal
from StudentWindow import Ui_MainWindow
from database_connection import DatabaseConnection
from DAO_QLSV import DAO_SinhVien

class MyControl(QMainWindow, Ui_MainWindow):
    def __init__(self, identifier=None, role=None, parent=None):    
        super().__init__(parent)
        print("Initializing MyControl")
        self.identifier = identifier
        self.role = role
        self.setupUi(self)
        print("UI setup complete")

        try:
            self.db = DatabaseConnection('HOANGNINHKHANG\SQLEXPRESS', 'ndkm2', 'sa', 'sapassword')
            print("DatabaseConnection initialized")
            self._connect_to_database()
            self.dao_sinh_vien = DAO_SinhVien(self.db)
            print("DAO_SinhVien initialized successfully")
        except Exception as e:
            print(f"Error initializing DAO_SinhVien: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi khởi tạo DAO_SinhVien: {e}")

        try:
            self.load_student_info()
        except Exception as e:
            print(f"Error loading student info: {e}")
            
    def _initialize_student_page(self):
        self.load_student_infoTable()


        # Thiết lập độ rộng cột
        column_widths = [100, 200, 80, 150, 100, 150, 310, 150]
        self._set_column_widths(self.StudentInfo_Table, column_widths)

    def logout(self):
        self.close()
        # Quay lại màn hình đăng nhập
        from login_window import Ui_LoginWindow
        self.login_window = QMainWindow()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self.login_window)
        self.login_window.show()
        
    def load_student_info(self):
        try:
            # Kiểm tra kết nối
            if not self.db.connect():
                QMessageBox.critical(self, "Lỗi Kết Nối", "Không thể kết nối đến cơ sở dữ liệu!")
                return

            # Lấy thông tin sinh viên từ CSDL
            student_info = self.dao_sinh_vien.tim_kiem_sinh_vien_bang_MaSV(self.identifier)
            
            if not student_info:
                QMessageBox.warning(self, "Không Tìm Thấy", "Không tìm thấy thông tin sinh viên!")
                return

            # Điền thông tin vào các trường LineEdit
            self.ID_Student_lineEdit.setText(student_info[0])
            self.Name_Student_lineEdit.setText(student_info[1])
            self.Gender_Student_lineEdit.setText(student_info[2])

            # Ngày sinh
            if isinstance(student_info[3], QDate):
                self.Birth_Student_dateEdit.setDate(student_info[3])
            else:
                date = QDate.fromString(student_info[3].strftime("%Y-%m-%d"), "yyyy-MM-dd")
                self.Birth_Student_dateEdit.setDate(date)

            self.Phone_Student_lineEdit.setText(student_info[4])
            self.Email_Student_lineEdit.setText(student_info[5])
            self.Address_Student_lineEdit.setText(student_info[6])

            QMessageBox.information(self, "Thành Công", "Đã tải thông tin sinh viên!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tải thông tin sinh viên: {e}")

    # def load_student_info(self, data=None):        
    #     self.StudentInfo_Table.setRowCount(0)
        
    #     # Nếu không có dữ liệu được truyền vào, lấy tất cả sinh viên
    #     if data is None:
    #         data = self.dao_sinh_vien.tim_kiem_sinh_vien_bang_MaSV(self.identifier)

    #     for row_index, row_data in enumerate(data):
    #         self.StudentInfo_Table.insertRow(row_index)
    #         for col_index, cell_data in enumerate(row_data):
    #             self.StudentInfo_Table.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))

    #         self.StudentInfo_Table.setCellWidget(row_index, 7)
    
    def _connect_to_database(self):
        try:
            self.db.connect()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Kết Nối", f"Không thể kết nối với cơ sở dữ liệu: {e}")
            self.close()  
# 