class DAO_SinhVien:
    """
    Lớp Data Access Object (DAO) quản lý thao tác với bảng `students`.
    """
    def __init__(self, connection):
        """
        Khởi tạo DAO với đối tượng DatabaseConnection.
        """
        if not hasattr(connection, "get_cursor"):
            raise ValueError("Đối tượng kết nối phải là một DatabaseConnection.")
        self.connection = connection  # Đối tượng DatabaseConnection

    def get_cursor(self):
        """
        Lấy đối tượng cursor từ DatabaseConnection.
        """
        return self.connection.get_cursor()

    def kiem_tra_ma_sv(self, ma_sv):
        """
        Kiểm tra xem mã sinh viên có tồn tại trong cơ sở dữ liệu hay không.
        """
        cursor = self.get_cursor()
        cursor.execute("SELECT ma_sv FROM students WHERE ma_sv = ?", (ma_sv,))
        result = cursor.fetchone()
        return result is not None  # True nếu mã sinh viên tồn tại

    def them_sinh_vien(self, ma_sv, ten, gioi_tinh, ngay_sinh, email, sdt, dia_chi):
        """
        Thêm một sinh viên mới vào cơ sở dữ liệu.
        """
        if self.kiem_tra_ma_sv(ma_sv):
            print("Mã sinh viên đã tồn tại. Vui lòng nhập mã khác.")
            return False

        cursor = self.get_cursor()
        query = """INSERT INTO students (ma_sv, ten, gioi_tinh, ngay_sinh, email, sdt, dia_chi)
                   VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, (ma_sv, ten, gioi_tinh, ngay_sinh, email, sdt, dia_chi))
        self.connection.conn.commit()
        print("Thêm sinh viên thành công")
        return True

    def tim_kiem_sinh_vien(self, search_value):
        """
        Tìm kiếm sinh viên theo mã sinh viên hoặc tên.
        """
        cursor = self.get_cursor()
        query = """SELECT ma_sv, ten, gioi_tinh, ngay_sinh, sdt, email, dia_chi 
                   FROM students 
                   WHERE ma_sv LIKE ? OR ten LIKE ? """
        search_param = f"%{search_value}%"
        cursor.execute(query, (search_param, search_param))
        results = cursor.fetchall()
        return results

    def tim_kiem_sinh_vien_bang_MaSV(self, ma_sv):
        """
        Tìm kiếm sinh viên theo mã sinh viên.
        """
        cursor = self.get_cursor()
        query = """SELECT ma_sv, ten, gioi_tinh, ngay_sinh, sdt, email, dia_chi 
                   FROM students 
                   WHERE ma_sv = ?"""
        cursor.execute(query, (ma_sv,))
        result = cursor.fetchone()
        return result

    def cap_nhat_sinh_vien(self, ma_sv, ten, gioi_tinh, ngay_sinh, sdt, email, dia_chi):
        """
        Cập nhật thông tin sinh viên.
        """
        cursor = self.get_cursor()
        update_query = """
            UPDATE students
            SET ten = ?, gioi_tinh = ?, ngay_sinh = ?, sdt = ?, email = ?, dia_chi = ?
            WHERE ma_sv = ?
        """
        try:
            cursor.execute(update_query, (ten, gioi_tinh, ngay_sinh, sdt, email, dia_chi, ma_sv))
            self.connection.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật sinh viên: {e}")
            return False

    def xoa_sinh_vien(self, ma_sv):
        """
        Xóa một sinh viên khỏi cơ sở dữ liệu.
        """
        try:
            cursor = self.get_cursor()
            query = "DELETE FROM students WHERE ma_sv = ?"
            cursor.execute(query, (ma_sv,))
            self.connection.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi khi xóa sinh viên: {e}")
            return False

    def get_all_students(self):
        """
        Lấy toàn bộ thông tin sinh viên từ cơ sở dữ liệu.
        """
        cursor = self.get_cursor()
        query = """SELECT ma_sv, ten, gioi_tinh, ngay_sinh, sdt, email, dia_chi FROM students"""
        cursor.execute(query)
        results = cursor.fetchall()
        return results
