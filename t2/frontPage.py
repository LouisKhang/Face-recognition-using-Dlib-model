# Import các thư viện cần thiết
from PyQt6.QtWidgets import (
    QMainWindow, QTableWidgetItem, QMessageBox, QHBoxLayout,QVBoxLayout,  QWidget, QPushButton, QDialog, QTableWidget, QHeaderView
)
from PyQt6.QtGui import QIcon,QPixmap, QImage
from PyQt6.QtCore import QSize, QTimer, Qt, QDate, pyqtSignal
from ui_main import Ui_MainWindow
from database_connection import DatabaseConnection
from DAO_QLSV import DAO_SinhVien
from DAO_ManageAccount import DAO_Account
from StudentDialog1 import StudentDialog
from AccountDialog import AccountDialog
from Update_AccountDialog import UpdateAccountDialog
from UpdateStudentDialog import UpdateStudentDialog
from nhandien import FaceRecognition

import resource_rc
import os
import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas
) 
import yaml
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table,TableStyle
# Lớp chính MySideBar
class MySideBar(QMainWindow, Ui_MainWindow):
    def __init__(self, identifier=None, role=None, parent=None):
        super().__init__(parent)
        self.identifier = identifier
        self.role = role
        self.setupUi(self)
        self.setWindowTitle("Quản lý Sinh viên")

        # Kết nối cơ sở dữ liệu
        self.db = DatabaseConnection('HOANGNINHKHANG\\SQLEXPRESS', 'ndkm2', 'sa', 'sapassword')
        self._connect_to_database()

        # Khởi tạo DAO
        self.dao_sinh_vien = DAO_SinhVien(self.db)
        self.dao_account = DAO_Account(self.db)
#####
        # Thêm dòng này để khởi tạo face_recognition
        self.face_recognition = None
#####
        # Thiết lập giao diện ban đầu
        self._initialize_ui()

        # Kết nối các nút bấm
        self._connect_buttons()

        # Khởi tạo các trang
        self._initialize_student_page()
        self._initialize_account_page()

        self.initialize_face_recognition()
        self.setup_camera()
        
        self.cap = None
        self.camera_active = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Kết nối các nút trong page_4
        self.OpenCamera.clicked.connect(self.start_camera)
        self.CloseCamera.clicked.connect(self.stop_camera)    
        
        self.SignOut_1.clicked.connect(self.signout)
        self.SignOut_2.clicked.connect(self.signout)
        #ketnoinut page_5
        self.no_face_duration = 0  # Thời gian không phát hiện khuôn mặt
        self.timeout_limit = 10  # Giới hạn thời gian không phát hiện (giây)
        self.Find_EnExHistory_Button.clicked.connect(self.filterData)
         #page7
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Tạo layout cho khu vực hiển thị biểu đồ
        layout = QVBoxLayout(self.vunghienthibieudo_page7)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.bt_taothongke.clicked.connect(self.generate_statistics)
        self.bt_hienthibd.clicked.connect(self.show_selected_chart)
    def _connect_to_database(self):
        try:
            self.db.connect()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Kết Nối", f"Không thể kết nối với cơ sở dữ liệu: {e}")
            self.close()  
# 
#-------------------SET UI
# 
    def _initialize_ui(self):
        
        self.icon_only_widget.setHidden(True)
        self.Account_dropdown.setHidden(True)

    def _connect_buttons(self):
        
        button_actions = {
                    self.Student_1: 0,
                    self.Student_2: 0,
                    self.Account: 1,
                    self.LogHistory: 2,
                    self.FaceReg_1: 3,
                    self.FaceReg_2: 3,
                    self.EnExHistory_1: 4,
                    self.EnExHistory_2: 4,
                    self.Statistics_1: 5,
                    self.Statistics_2: 5,
                    self.Settings_1: 6,
                    self.Settings_2: 6,
        }
        for button, page_index in button_actions.items():
            button.clicked.connect(lambda _, idx=page_index: self.stackedWidget.setCurrentIndex(idx))

# 
#-------------------PAGE-STUDENT
# 
    def _initialize_student_page(self):
       
        self.Add_Student_Button.clicked.connect(self.open_add_student_dialog)
        self.load_student_info()
        self.GenderFind_Student_comboBox.currentIndexChanged.connect(self.reload_student_table)
        self.Search_Student.textChanged.connect(self.search_students)

        # Thiết lập độ rộng cột
        column_widths = [100, 200, 80, 150, 100, 150, 310, 150]
        self._set_column_widths(self.StudentInfo_Table, column_widths)

    def _initialize_account_page(self):
        
        self.Add_Account_Button.clicked.connect(self.open_add_account_dialog)
        self.load_account_info()
        self.GenderFind_Account_comboBox.currentIndexChanged.connect(self.reload_account_table)
        self.RolesFind_Account_comboBox.currentIndexChanged.connect(self.reload_account_table)
        self.Search_Account_LineEdit.textChanged.connect(self.search_accounts)

        # Thiết lập độ rộng cột
        column_widths = [100, 200, 80, 120, 120, 120, 120, 120, 155, 100]
        self._set_column_widths(self.AccountInfo_Table, column_widths)

    def _set_column_widths(self, table_widget, widths):
        
        for idx, width in enumerate(widths):
            table_widget.setColumnWidth(idx, width)

    def open_add_student_dialog(self):
        
        dialog = StudentDialog(self, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.reload_student_table()

    def reload_student_table(self):        
        self.load_student_info()

    def load_student_info(self, data=None):        
        self.StudentInfo_Table.setRowCount(0)
        
        # Nếu không có dữ liệu được truyền vào, lấy tất cả sinh viên
        if data is None:
            data = self.dao_sinh_vien.get_all_students()

        for row_index, row_data in enumerate(data):
            self.StudentInfo_Table.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.StudentInfo_Table.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))

            double_button_widget = DoubleButtonWidgetStudents(row_index, row_data, self, self.db)
            double_button_widget.refresh_signal.connect(self.load_student_info)
            self.StudentInfo_Table.setCellWidget(row_index, 7, double_button_widget)

    def search_students(self):        
        search_value = self.Search_Student.text()
        results = self.dao_sinh_vien.tim_kiem_sinh_vien(search_value)
        self.load_student_info(results)
# 
#-------------------PAGE-ACCOUNT
#
    def open_add_account_dialog(self):        
        dialog = AccountDialog(self, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.reload_account_table()

    def reload_account_table(self):        
        self.load_account_info()

    def load_account_info(self, data=None):        
        self.AccountInfo_Table.setRowCount(0)
        if data is None:
            data = self.dao_account.get_all_accounts()
        for row_index, row_data in enumerate(data):
            self.AccountInfo_Table.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.AccountInfo_Table.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))

            double_button_widget = DoubleButtonWidgetAccounts(row_index, row_data, self, self.db)
            double_button_widget.refresh_signal.connect(self.load_account_info)
            self.AccountInfo_Table.setCellWidget(row_index, 9, double_button_widget)
    
    def search_accounts(self):        
        search_value = self.Search_Account_LineEdit.text()
        results = self.dao_account.tim_kiem_Account(search_value)
        self.load_account_info(results)
# 
#-------------------PAGE-FACEREGCOGNIZED
#
    def initialize_face_recognition(self):
        try:
            label_dict_path = "C:\\Users\\PC\\Desktop\\t2_02\\t2\\trainer\\dataset\\model_data.yml"
            encodings_path = "C:\\Users\\PC\\Desktop\\t2_02\\t2\\trainer\\dataset\\model_data.yml"
            # Gán giá trị cho self.face_recognition
            self.face_recognition = FaceRecognition(label_dict_path, encodings_path)

    ## chỉnh lại này: Trong phương thức initialize_face_recognition(), thêm xử lý ngoại lệ và gán giá trị cho self.face_recognition:   
        except Exception as e:
            print(f"Lỗi khởi tạo nhận diện khuôn mặt: {e}")
            # Đảm bảo self.face_recognition không phải là None để tránh lỗi
            self.face_recognition = None
            QMessageBox.warning(self, "Lỗi", f"Không thể khởi tạo nhận diện khuôn mặt: {e}")
    def setup_camera(self):
        self.camera_active = False
        self.cap = None
        self.recognized_faces = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.recognized_faces_dir = "recognized_faces"
        if not os.path.exists(self.recognized_faces_dir):
            os.makedirs(self.recognized_faces_dir)
    
    def start_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Không thể mở camera!")

            print("Camera đã bật.")
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            self.timer.start(30)
            self.camera_active = True
            self.FaceReg_CameraInfo_label.setText("Camera đã bật.")
            self.OpenCamera.setEnabled(False)
            self.CloseCamera.setEnabled(True)

        except Exception as e:
            print(f"Lỗi mở camera: {e}")
            self.FaceReg_CameraInfo_label.setText(f"Lỗi: {e}")


    def stop_camera(self):
        """
        Tắt camera và dừng nhận diện.
        """
        try:
            self.timer.stop()
            if self.cap is not None:
                self.cap.release()
            self.camera_active = False
            self.FaceReg_Camera_label.clear()
#chỉnh lại dòng nay        
            # Kiểm tra xem face_recognition có được khởi tạo không
            if self.face_recognition is not None:
                self.reset_recognition()
            
            self.FaceReg_CameraInfo_label.setText("Camera đã tắt.")
            self.OpenCamera.setEnabled(True)
            self.CloseCamera.setEnabled(False)
        except Exception as e:
            print(f"Lỗi tắt camera: {e}")
            self.FaceReg_CameraInfo_label.setText(f"Lỗi: {e}")

    def update_frame(self):
        try:
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("Không thể đọc khung hình từ camera")

            frame = cv2.flip(frame, 1)

            face = self.face_recognition.detect_face(frame)

            if face is None:
                self.no_face_duration += 1  # Tăng thời gian không phát hiện khuôn mặt
                self.FaceReg_CameraInfo_label.setText("Không phát hiện khuôn mặt")
            else:
                self.no_face_duration = 0  # Reset thời gian khi phát hiện khuôn mặt
                shape = self.face_recognition.shape_predictor(frame, face)
                face_encoding = np.array(
                    self.face_recognition.face_recognition_model.compute_face_descriptor(frame, shape)
                )

                name, confidence = self.face_recognition.identify_face(face_encoding)

                confidence_percentage = confidence * 100  # Chuyển đổi thành phần trăm

                if name != "unknown":
                    if name not in self.recognized_faces:
                        self.handle_recognition(name, frame, face,confidence)
                        self.recognized_faces.append(name)
                    else:
                        self.FaceReg_CameraInfo_label.setText(
                            f"Đang theo dõi: {name} (Độ tin cậy: {confidence_percentage:.2f}%)"
                        )

                    cv2.rectangle(frame, 
                                  (face.left(), face.top()), 
                                  (face.right(), face.bottom()), 
                                  (0, 255, 0), 2)

                    cv2.putText(frame, 
                                f"{name} ({confidence_percentage:.2f}%)", 
                                (face.left(), face.top() - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    self.handle_unknown_face(frame, face, confidence)

                    cv2.rectangle(frame, 
                                  (face.left(), face.top()), 
                                  (face.right(), face.bottom()), 
                                  (0, 0, 255), 2)

                    cv2.putText(frame, 
                                f"Unknown ({confidence_percentage:.2f}%)", 
                                (face.left(), face.top() - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, 
                                    QImage.Format.Format_RGB888)
            self.FaceReg_Camera_label.setPixmap(QPixmap.fromImage(qt_image))

            # Kiểm tra thời gian không phát hiện khuôn mặt
            if self.no_face_duration >= (self.timeout_limit * 30):  # 30 fps x 10 giây
                self.stop_camera()  # Dừng camera
                self.FaceReg_CameraInfo_label.setText("Đã tắt camera do không phát hiện khuôn mặt")

            # Tính toán và hiển thị phần trăm nhận diện thành công
            success_rate = self.face_recognition.calculate_success_rate()
            # self.success_rate_label.setText(f"Phần trăm nhận diện: {success_rate:.2f}%")

        except Exception as e:
            print(f"Lỗi cập nhật khung hình: {e}")


    def handle_recognition(self, ID_SV, frame, face,confidence):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attendance_type = self.attendance_type_combo.currentText()

        try:
            student_info = self.dao_sinh_vien.tim_kiem_sinh_vien_bang_MaSV(ID_SV)
            print(f"Thông tin sinh viên tìm thấy: {student_info}")  # Log dữ liệu trả về
            if student_info:
                if student_info is not None:  # Kiểm tra nếu thông tin sinh viên không phải None
            # Cập nhật giao diện với thông tin sinh viên và độ tin cậy
                    self.update_ui_with_student_info(student_info, confidence)
                

                current_frame = frame.copy()
                face_img_path = os.path.join(self.recognized_faces_dir, f"{ID_SV}_{student_info[1]}_{current_time}.jpg")
                cv2.imwrite(face_img_path, current_frame)

                frame_rgb = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame_rgb.shape
                bytes_per_line = channel * width
                q_img = QImage(frame_rgb.data, width, height, bytes_per_line, 
                                    QImage.Format.Format_RGB888)

                pixmap = QPixmap.fromImage(q_img)
                scaled_pixmap = pixmap.scaled(
                    180, 180,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.FaceReg_CameraStudent_label.setPixmap(scaled_pixmap)

                query = """
                INSERT INTO attendance (ma_sv, ten, attendance_type, timestamp)
                VALUES (?, ?, ?, ?)
                """
                cursor = self.db.get_cursor()
                cursor.execute(query, (student_info[0], student_info[1], attendance_type, current_time))
                self.db.conn.commit()

                self.attendance_status_label.setText(f"Trạng thái: {attendance_type}")
                self.time_label.setText(f"Thời gian: {current_time}")
                self.FaceReg_CameraInfo_label.setText(f"Đã nhận diện thành công: {ID_SV}_{student_info[1]}")

            else:
                self.FaceReg_CameraInfo_label.setText(f"Không tìm thấy thông tin sinh viên: {ID_SV}_{student_info[1]}")

        except Exception as e:
            print(f"Lỗi xử lý nhận diện: {e}")
            self.FaceReg_CameraInfo_label.setText("Lỗi xử lý thông tin sinh viên")
    
    def handle_unknown_face(self, frame, face, confidence):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.ID_FaceReg_Student_lineEdit.setText(" Unknown")
        self.Name_FaceReg_Student_lineEdit.setText("Unknown")
        self.Gender_FaceReg_Student_comboBox.setCurrentIndex(0)
        self.Birth_FaceReg_Student_dateEdit.setDate(QDate.currentDate())
        self.Phone_FaceReg_Student_lineEdit.setText("Unknown")
        self.Email_FaceReg_Student_lineEdit.setText("Unknow")
        self.Address_FaceReg_Student_lineEdit.setText("Unknow")
        self.time_label.setText(f"Thời gian: {current_time}")

        try:
            unknown_dir = os.path.join(self.recognized_faces_dir, "unknown")
            if not os.path.exists(unknown_dir):
                os.makedirs(unknown_dir)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            face_img_path = os.path.join(unknown_dir, f"unknown_{timestamp}.jpg")

            face_img = frame[face.top():face.bottom(), face.left():face.right()]
            cv2.imwrite(face_img_path, face_img)

            face_img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            height, width, channel = face_img_rgb.shape
            bytes_per_line = channel * width
            q_img = QImage(face_img_rgb.data, width, height, bytes_per_line, 
                                QImage.Format.Format_RGB888)
            
            pixmap = QPixmap.fromImage(q_img)
            scaled_pixmap = pixmap.scaled(
                180, 180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.FaceReg_CameraStudent_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"Lỗi lưu ảnh khuôn mặt không xác định: {e}")

        confidence_percentage = confidence * 100  # Chuyển đổi thành phần trăm
        self.FaceReg_CameraInfo_label.setText(
            f"Phát hiện khuôn mặt không xác định (Độ tin cậy: {confidence_percentage:.2f}%)"
        )
        self.FaceReg_CameraInfo_label.setText("Không có thông tin")
    
    def reset_recognition(self):
        self.ID_FaceReg_Student_lineEdit.clear()
        self.Name_FaceReg_Student_lineEdit.clear()
        self.Gender_FaceReg_Student_comboBox.setCurrentIndex(0)
        self.Birth_FaceReg_Student_dateEdit.setDate(QDate.currentDate())
        self.Phone_FaceReg_Student_lineEdit.clear()
        self.Email_FaceReg_Student_lineEdit.clear()
        self.Address_FaceReg_Student_lineEdit.clear()
        self.attendance_status_label.setText("Trạng thái: ")
        self.time_label.setText("Thời gian: ")
        self.FaceReg_CameraStudent_label.clear()
        self.recognized_faces.clear()
####
        if self.face_recognition:
###

            self.face_recognition.true_positives = 0
            self.face_recognition.false_negatives = 0

    def closeEvent(self, event):
        # Dừng camera và ngắt kết nối cơ sở dữ liệu khi đóng ứng dụng
        self.stop_camera()
        if self.db:
            self.db.disconnect()
        event.accept()      
    
    def update_ui_with_student_info(self, student_info, confidence):
        try:
            if len(student_info) != 7:
                self.FaceReg_CameraInfo_label.setText("Dữ liệu sinh viên không hợp lệ.")
                return

            # Gán thông tin vào các lineEdit
            self.ID_FaceReg_Student_lineEdit.setText(student_info[0])  # Mã sinh viên
            self.Name_FaceReg_Student_lineEdit.setText(student_info[1])  # Tên sinh viên
            self.Gender_FaceReg_Student_comboBox.setCurrentText(student_info[2])  # Giới tính

            # Kiểm tra ngày sinh
            if isinstance(student_info[3], datetime.date):  # Kiểm tra nếu là đối tượng datetime.date
                        q_date = QDate(student_info[3].year, student_info[3].month, student_info[3].day)
                        self.Birth_FaceReg_Student_dateEdit.setDate(q_date)

            self.Phone_FaceReg_Student_lineEdit.setText(student_info[4])  # Số điện thoại
            self.Email_FaceReg_Student_lineEdit.setText(student_info[5])  # Email
            self.Address_FaceReg_Student_lineEdit.setText(student_info[6])  # Địa chỉ
            self.FaceReg_CameraInfo_label.setText(f"Đã nhận diện sinh viên: {student_info[1]} với độ tin cậy: {confidence:.2f}")
            
        except Exception as e:
            self.FaceReg_CameraInfo_label.setText(f"Lỗi xử lý thông tin sinh viên: {e}")



# 
#-------------------SIGN-OUT
#
    def signout(self):
        """
        Đăng xuất khỏi ứng dụng, mở cửa sổ đăng nhập và đóng cửa sổ hiện tại.
        """
        from login_window import Ui_LoginWindow
        self.login_window = QMainWindow()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self.login_window)
        self.login_window.show()  


# 
#-------------------EN-EX-HIS
#        
    def filterData(self):
        print("Hàm filterData đã được gọi!")
        try:
            # Kết nối đến cơ sở dữ liệu
            if not self.db.connect():
                QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến cơ sở dữ liệu!")
                return

            # Lấy con trỏ cơ sở dữ liệu
            cursor = self.db.get_cursor()

            # Lấy thông tin lọc từ giao diện
            start_date = self.EnExHistoryFindbatdau_DateEdit.date().toString("yyyy-MM-dd 00:00:00")
            end_date = self.EnExHistoryFindketthuc_DateEdit.date().toString("yyyy-MM-dd 23:59:59")
            mssv = self.nhapmsv_2.text()

            # Debug: In ra giá trị lọc
            print(f"Ngày bắt đầu: {start_date}, Ngày kết thúc: {end_date}, MSSV: {mssv}")

            # Kiểm tra xem ngày bắt đầu và kết thúc đã được điền chưa
            if not start_date or not end_date:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn đầy đủ ngày bắt đầu và kết thúc!")
                return

            # Truy vấn lấy dữ liệu từ bảng `attendance`
            query = """
            WITH PairedAttendance AS (
                SELECT 
                    a1.ma_sv,
                    a1.ten,
                    a1.timestamp AS gio_vao,
                    a2.timestamp AS gio_ra,
                    DATEDIFF(MINUTE, a1.timestamp, a2.timestamp) AS total_minutes
                FROM 
                    attendance a1
                LEFT JOIN 
                    attendance a2 ON a1.ma_sv = a2.ma_sv 
                    AND a2.timestamp > a1.timestamp 
                    AND a2.attendance_type = 'Out'
                    AND a1.attendance_type = 'In'
                    AND a2.timestamp = (
                        SELECT MIN(timestamp) 
                        FROM attendance 
                        WHERE ma_sv = a1.ma_sv 
                        AND attendance_type = 'Out' 
                        AND timestamp > a1.timestamp
                    )
                WHERE 
                    a1.attendance_type = 'In' AND
                    a1.timestamp BETWEEN ? AND ?
                    {student_condition}
            )
            SELECT 
                ma_sv,
                ten,
                gio_vao,
                gio_ra,
                total_minutes
            FROM 
                PairedAttendance
            ORDER BY 
                gio_vao
            """

            # Chuẩn bị tham số và điều kiện lọc
            params = [start_date, end_date]
            student_condition = ""
            
            # Nếu MSSV được điền, thêm điều kiện lọc
            if mssv:
                student_condition = "AND a1.ma_sv = ?"
                params.append(mssv)

            # Thay thế điều kiện sinh viên trong truy vấn
            query = query.format(student_condition=student_condition)

            # Debug: In ra truy vấn và tham số
            print(f"Query: {query}")
            print(f"Params: {params}")

            # Thực thi truy vấn
            cursor.execute(query, params)
            data = cursor.fetchall()
            print(f"Số lượng bản ghi: {len(data)}")

            # Xóa dữ liệu cũ trong bảng
            self.EnExHistory_Table.setRowCount(0)

            # Duyệt qua kết quả và thêm dữ liệu vào bảng
            for row, record in enumerate(data):
                self.EnExHistory_Table.insertRow(row)

                # Thêm STT
                item_stt = QTableWidgetItem(str(row + 1))
                self.EnExHistory_Table.setItem(row, 0, item_stt)

                # Thêm MSSV
                item_mssv = QTableWidgetItem(str(record[0]))
                self.EnExHistory_Table.setItem(row, 1, item_mssv)

                # Thêm Họ tên
                item_name = QTableWidgetItem(str(record[1]))
                self.EnExHistory_Table.setItem(row, 2, item_name)

                # Xác định loại ra/vào
                attendance_type = "Đã ra" if record[3] is not None else "In"
                item_type = QTableWidgetItem(attendance_type)
                self.EnExHistory_Table.setItem(row, 3, item_type)

                # Thêm Giờ vào
                item_gio_vao = QTableWidgetItem(str(record[2]) if record[2] else '')
                self.EnExHistory_Table.setItem(row, 4, item_gio_vao)

                # Thêm Giờ ra
                item_gio_ra = QTableWidgetItem(str(record[3]) if record[3] else '')
                self.EnExHistory_Table.setItem(row, 5, item_gio_ra)

                # Thêm Thời gian
                item_total_time = QTableWidgetItem(str(record[4]) if record[4] else '')
                self.EnExHistory_Table.setItem(row, 6, item_total_time)

                # Thêm cột trống (tùy chỉnh nếu cần)
                item_extra = QTableWidgetItem('')
                self.EnExHistory_Table.setItem(row, 7, item_extra)

        except Exception as query_error:
            print(f"Lỗi thực thi truy vấn: {query_error}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi thực thi truy vấn: {query_error}")
    def export_table_to_pdf(self):
        # Kiểm tra xem bảng có dữ liệu không
        if self.EnExHistory_Table.rowCount() == 0:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để xuất PDF!")
            return

        # Đường dẫn cố định
        export_dir = r"./PDF"
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(export_dir, exist_ok=True)

        # Tạo tên file duy nhất (ví dụ: sử dụng timestamp)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"export_{timestamp}.pdf"
        file_path = os.path.join(export_dir, file_name)
        try:
            # Tạo danh sách dữ liệu từ bảng
            table_data = []
            
            # Thêm header
            headers = []
            for col in range(self.EnExHistory_Table.columnCount()):
                headers.append(self.EnExHistory_Table.horizontalHeaderItem(col).text())
            table_data.append(headers)
            
            # Thêm dữ liệu từng dòng
            for row in range(self.EnExHistory_Table.rowCount()):
                row_data = []
                for col in range(self.EnExHistory_Table.columnCount()):
                    item = self.EnExHistory_Table.item(row, col)
                    row_data.append(item.text() if item else '')
                table_data.append(row_data)
            
            # Tạo PDF
            pdf_doc = SimpleDocTemplate(file_path, pagesize=letter)
            
            # Tạo bảng
            table = Table(table_data)
            
            # Định dạng style cho bảng
            style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
                ('ALIGN', (0,1), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ])
            table.setStyle(style)
            
            # Tạo nội dung PDF
            elements = [table]
            
            # Xuất PDF
            pdf_doc.build(elements)
            
            # Thông báo thành công
            #QMessageBox.information(self, "Thành công", f"Đã xuất file PDF tại:\n{file_path}")
            # Thông báo thành công
            QMessageBox.information(None, "Thành công", f"Đã xuất file PDF ")
        except Exception as e:
            # Thông báo lỗi
            QMessageBox.critical(None, "Lỗi", f"Không thể xuất PDF")
        
            
            
##### 
####statistic
####
    def generate_statistics(self):
        """Fetch statistics based on the selected date range."""
        try:
            from_date = self.dateEditpage_7.date().toString("yyyy-MM-dd")
            to_date = self.dateEdit_2page_7.date().toString("yyyy-MM-dd")

            if not self.db.connect():
                QMessageBox.critical(self, "Lỗi", "Không thể kết nối cơ sở dữ liệu!")
                return
            
            # Khởi tạo con trỏ
            cursor = self.db.get_cursor()

            # Fetch attendance data
            attendance_query = """
            SELECT ma_sv, ten, timestamp
            FROM attendance
            WHERE CAST(timestamp AS DATE) BETWEEN ? AND ?
            """
            cursor.execute(attendance_query, (from_date, to_date))
            self.attendance_records = cursor.fetchall() or []

            # Fetch login data
            login_query = """
            SELECT username, login_time, success
            FROM login_history
            WHERE CAST(login_time AS DATE) BETWEEN ? AND ?
            """
            cursor.execute(login_query, (from_date, to_date))
            self.login_records = cursor.fetchall() or []

            QMessageBox.information(self, "Thành công", "Đã tải dữ liệu thống kê")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tạo thống kê: {e}")


    def show_selected_chart(self):
        # Check if 'attendance_records' exists; if not, generate statistics
        if not hasattr(self, 'attendance_records'):
            self.generate_statistics()

        # Clear the previous chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Get the selected value from comboBox and strip whitespace
        selected_chart = self.comboBoxpage_7.currentText().strip()

        # Print the selected chart and available options for debugging
        print(f"Selected chart: '{selected_chart}'")  # Current selection
        print("Available chart options:")
        for i in range(self.comboBoxpage_7.count()):
            print(self.comboBoxpage_7.itemText(i))  # All options in comboBox

        # Attendance frequency by week
        if selected_chart == "Tần suất ra vào theo tuần":
            weekly_counts = [0] * 7
            for record in self.attendance_records:
                day_of_week = record[2].weekday()
                weekly_counts[day_of_week] += 1

            ax.bar(["CN", "T2", "T3", "T4", "T5", "T6", "T7"], weekly_counts, color='cyan')
            ax.set_title("Tần suất ra vào theo tuần", fontsize=16)
            ax.set_ylabel("Số lượt", fontsize=12)
            ax.set_xlabel("Ngày trong tuần", fontsize=12)

        # Attendance frequency by day
        elif selected_chart == "Tần suất ra vào theo ngày":
            daily_counts = {}
            for record in self.attendance_records:
                date = record[2].date()
                daily_counts[date] = daily_counts.get(date, 0) + 1

            dates = list(daily_counts.keys())
            counts = list(daily_counts.values())
            ax.plot(dates, counts, marker='o', color='magenta')
            ax.set_title("Tần suất ra vào theo ngày", fontsize=16)
            ax.set_xlabel("Ngày", fontsize=12)
            ax.set_ylabel("Số lượt", fontsize=12)
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # Attendance frequency by month
        elif selected_chart == "Tần suất ra vào theo tháng":
            monthly_counts = {}
            for record in self.attendance_records:
                month = record[2].strftime("%Y-%m")
                monthly_counts[month] = monthly_counts.get(month, 0) + 1

            months = list(monthly_counts.keys())
            counts = list(monthly_counts.values())
            ax.bar(months, counts, color='orange')
            ax.set_title("Tần suất ra vào theo tháng", fontsize=16)
            ax.set_xlabel("Tháng", fontsize=12)
            ax.set_ylabel("Số lượt", fontsize=12)
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # Peak hours for library entry
        elif selected_chart == "Giờ cao điểm ra vào thư viện":
            hourly_counts = [0] * 24
            for record in self.attendance_records:
                hour = record[2].hour
                hourly_counts[hour] += 1

            ax.plot(range(24), hourly_counts, marker='o', color='green')
            ax.set_title("Giờ cao điểm vào thư viện", fontsize=16)
            ax.set_xlabel("Giờ", fontsize=12)
            ax.set_ylabel("Số lượt", fontsize=12)

        # Top students entering the library by week
        elif selected_chart == "Top sinh viên vào thư viện theo tuần":
            weekly_student_counts = {}
            for record in self.attendance_records:
                student_name = record[1]
                week = record[2].isocalendar()[1]
                year = record[2].year
                key = (year, week, student_name)
                weekly_student_counts[key] = weekly_student_counts.get(key, 0) + 1

            top_students = {}
            for (year, week, student_name), count in weekly_student_counts.items():
                top_students[student_name] = top_students.get(student_name, 0) + count

            sorted_top_students = sorted(top_students.items(), key=lambda x: x[1], reverse=True)[:5]
            names, counts = zip(*sorted_top_students)

            ax.bar(names, counts, color='purple')
            ax.set_title("Top sinh viên vào thư viện theo tuần", fontsize=16)
            ax.set_xlabel("Sinh viên", fontsize=12)
            ax.set_ylabel("Số lần vào thư viện", fontsize=12)
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # New: Top users logged in
        elif selected_chart == "Top người dùng đăng nhập":
            if not hasattr(self, 'login_records'):
                QMessageBox.warning(self, "Cảnh báo", "Chưa có dữ liệu đăng nhập. Vui lòng tạo thống kê trước.")
                return

            top_login_counts = {}
            for record in self.login_records:
                username = record[0]
                top_login_counts[username] = top_login_counts.get(username, 0) + (1 if record[2] else 0)

            sorted_top_logins = sorted(top_login_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            usernames, login_counts = zip(*sorted_top_logins)

            ax.bar(usernames, login_counts, color='blue')
            ax.set_title("Top người dùng đăng nhập", fontsize=16)
            ax.set_xlabel("Người dùng", fontsize=12)
            ax.set_ylabel("Số lần đăng nhập", fontsize=12)
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        else:
            print(f"Unknown chart selection: '{selected_chart}'")

        # Set layout and draw the chart
        plt.tight_layout()
        self.canvas.draw()


## login history
    def create_login_history_tab(self):
        """Create the tab to display login history."""
        history_tab = QWidget()
        layout = QVBoxLayout()

        # Create the QTableWidget
        self.Table_history = QTableWidget()  # Sử dụng self.Table_history thay vì self.login_history_list
        self.Table_history.setColumnCount(4)  # 4 columns: STT, Username, Login Time, Success
        self.Table_history.setHorizontalHeaderLabels(["STT", "Tên Đăng Nhập", "Thời gian đăng nhập", "Thành công"])
        
        # Enable sorting by columns
        self.Table_history.setSortingEnabled(True)
        
        # Adjust column widths
        self.Table_history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Add the QTableWidget to the layout
        layout.addWidget(self.Table_history)

        # Create a button to load login history
        self.hienthi_history = QPushButton("Hiển thị lịch sử")
        self.hienthi_history.clicked.connect(self.load_login_history)  # Kết nối nút với phương thức load_login_history
        layout.addWidget(self.hienthi_history)

        # Set the layout for the history tab
        history_tab.setLayout(layout)

        # Set the central widget for the main window
        self.setCentralWidget(history_tab)

    def load_login_history(self):
        try:
            # Calculate date range: last 30 days
            start_date = datetime.datetime.now() - datetime.timedelta(days=30)
            end_date = datetime.datetime.now()

            # Initialize cursor from the database
            cursor = self.db.get_cursor()

            # SQL query to fetch login history
            login_query = """
            SELECT id, username, login_time, success
            FROM login_history
            WHERE CAST(login_time AS DATE) BETWEEN ? AND ?
            """
            cursor.execute(login_query, (start_date, end_date))

            # Fetch results or an empty list if none
            rows = cursor.fetchall() or []

            # Populate the table with fetched data
            self.Table_history.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                self.Table_history.setItem(row_index, 0, QTableWidgetItem(str(row[0])))  # ID
                self.Table_history.setItem(row_index, 1, QTableWidgetItem(row[1]))        # Username
                self.Table_history.setItem(row_index, 2, QTableWidgetItem(str(row[2])))  # Login Time
                self.Table_history.setItem(row_index, 3, QTableWidgetItem(str(row[3])))  # Success (0 or 1)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tải lịch sử đăng nhập: {e}")
            print(f"Error loading login history: {e}")
    

# Widget chung cho các bảng
class DoubleButtonWidgetStudents(QWidget):
    refresh_signal = pyqtSignal()  # Tín hiệu làm mới bảng

    def __init__(self, row_index, row_data, parent, db_conn):
        super().__init__(parent)
        self.row_index = row_index
        self.row_data = row_data
        self.db_conn = db_conn

        # Tạo layout chứa các nút
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Tạo nút "Sửa"
        self.edit_button = QPushButton("Sửa", self)
        self.edit_button.setIcon(QIcon("./image/edit.png"))
        self.edit_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.edit_button.setIconSize(QSize(16, 16))
        self.edit_button.clicked.connect(self.edit_student)

        # Tạo nút "Xóa"
        self.delete_button = QPushButton("Xóa", self)
        self.delete_button.setIcon(QIcon("./image/delete.png"))
        self.delete_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.delete_button.setIconSize(QSize(16, 16))
        self.delete_button.clicked.connect(self.delete_student)

        # Thêm nút vào layout
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        
    def edit_student(self):
        dialog = UpdateStudentDialog(self.row_index, self.row_data, self.db_conn, self.parent())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_signal.emit()  # Gửi tín hiệu làm mới bảng

    def delete_student(self):
        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Bạn có chắc muốn xóa sinh viên {self.row_data[0]} không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db_conn.get_cursor()
                cursor.execute("DELETE FROM students WHERE ma_sv = ?", (self.row_data[0],))
                self.db_conn.conn.commit()  # Gọi commit từ đối tượng kết nối thực
                QMessageBox.information(self, "Thành công", "Đã xóa sinh viên thành công.")
                self.refresh_signal.emit()  # Gửi tín hiệu làm mới bảng
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa sinh viên: {e}")

class DoubleButtonWidgetAccounts(QWidget):
    refresh_signal = pyqtSignal()  # Tín hiệu làm mới bảng

    def __init__(self, row_index, row_data, parent, db_conn):
        super().__init__(parent)
        self.row_index = row_index
        self.row_data = row_data
        self.db_conn = db_conn

        # Tạo layout chứa các nút
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Tạo nút "Sửa"
        self.edit_button = QPushButton("Sửa", self)
        self.edit_button.setIcon(QIcon("./image/edit.png"))
        self.edit_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.edit_button.setIconSize(QSize(16, 16))
        self.edit_button.clicked.connect(self.edit_account)

        # Tạo nút "Xóa"
        self.delete_button = QPushButton("Xóa", self)
        self.delete_button.setIcon(QIcon("./image/delete.png"))
        self.delete_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.delete_button.setIconSize(QSize(16, 16))
        self.delete_button.clicked.connect(self.delete_account)

        # Thêm nút vào layout
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)

    def edit_account(self):
        dialog = UpdateAccountDialog(self.row_index, self.row_data, self.db_conn, self.parent())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_signal.emit()  # Gửi tín hiệu làm mới bảng

    def delete_account(self):
        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Bạn có chắc muốn xóa tài khoản {self.row_data[0]} không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db_conn.get_cursor()
                cursor.execute("DELETE FROM users WHERE user_id = ?", (self.row_data[0],))
                self.db_conn.conn.commit()
                QMessageBox.information(self, "Thành công", "Đã xóa tài khoản thành công.")
                self.refresh_signal.emit()  # Gửi tín hiệu làm mới bảng
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa tài khoản: {e}")
