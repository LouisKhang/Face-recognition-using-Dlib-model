class DAO_Account:
    """
    Lớp Data Access Object (DAO) quản lý thao tác với bảng `users`.
    """
    def __init__(self, connection):
        """
        Khởi tạo DAO với đối tượng DatabaseConnection.
        """
        self.connection = connection  # Đối tượng DatabaseConnection

    def get_cursor(self):
        """
        Lấy đối tượng cursor từ DatabaseConnection.
        """
        return self.connection.get_cursor()

    def kiem_tra_ma_id(self, ma_id):
        """
        Kiểm tra xem mã quản lý có tồn tại trong cơ sở dữ liệu hay không.
        """
        cursor = self.get_cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (ma_id,))
        result = cursor.fetchone()
        return result is not None  # Trả về True nếu mã tồn tại

    def them_account(self, ma_id, ten, username, password, role, gioi_tinh, ngay_sinh, email, sdt, dia_chi):
        """
        Thêm một tài khoản mới vào cơ sở dữ liệu.
        """
        if self.kiem_tra_ma_id(ma_id):
            print("Mã quản lý đã tồn tại. Vui lòng nhập mã khác.")
            return False

        cursor = self.get_cursor()
        query = """INSERT INTO users (user_id, name, gender, username, password, role, birthday, email, phone, address)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, (ma_id, ten, gioi_tinh, username, password, role, ngay_sinh, email, sdt, dia_chi))
        self.connection.conn.commit()
        print("Thêm tài khoản thành công")
        return True

    def tim_kiem_Account(self, search_value):
        """
        Tìm kiếm tài khoản theo mã quản lý hoặc tên.
        """
        cursor = self.get_cursor()
        query = """SELECT user_id, name, gender, username, role, birthday, email, phone, address
                   FROM users 
                   WHERE user_id LIKE ? OR name LIKE ? OR """
        search_param = f"%{search_value}%"
        cursor.execute(query, (search_param, search_param))
        results = cursor.fetchall()
        return results

    def cap_nhat_Account(self, ma_id, ten, username, password, role, gioi_tinh, ngay_sinh, email, sdt, dia_chi):
        """
        Cập nhật thông tin tài khoản.
        """
        cursor = self.get_cursor()
        update_query = """
            UPDATE users
            SET name = ?, gender = ?, username = ?, password = ?, role = ?, birthday = ?, email = ?, phone = ?, address = ?
            WHERE user_id = ?
        """
        try:
            cursor.execute(update_query, (ten, gioi_tinh, username, password, role, ngay_sinh, email, sdt, dia_chi, ma_id))
            self.connection.conn.commit()
            print("Cập nhật tài khoản thành công")
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật tài khoản: {e}")
            return False

    def xoa_account(self, ma_id):
        """
        Xóa một tài khoản khỏi cơ sở dữ liệu.
        """
        try:
            cursor = self.get_cursor()
            query = "DELETE FROM users WHERE user_id = ?"
            cursor.execute(query, (ma_id,))
            self.connection.conn.commit()
            print("Xóa tài khoản thành công")
            return True
        except Exception as e:
            print(f"Lỗi khi xóa tài khoản: {e}")
            return False

    def get_all_accounts(self):
        """
        Lấy toàn bộ thông tin tài khoản từ cơ sở dữ liệu.
        """
        cursor = self.get_cursor()
        query = """SELECT user_id, name, gender, username, role, birthday, email, phone, address FROM users"""
        cursor.execute(query)
        results = cursor.fetchall()
        return results
