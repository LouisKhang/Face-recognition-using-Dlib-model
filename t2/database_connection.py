import pyodbc
class DatabaseConnection:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.conn = None

    def connect(self):
        try:
            self.conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password}"
            )


            print("Kết nối thành công đến SQL Server")
            return True  # Thêm dòng này
        except Exception as e:
            print(f"Không thể kết nối đến SQL Server: {e}")
            return False  # Thêm dòng này

    def get_cursor(self):
        """
        Lấy đối tượng cursor từ kết nối.
        """
        if not self.conn:
            raise Exception("Kết nối cơ sở dữ liệu đã bị đóng.")
        return self.conn.cursor()

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print("Đã ngắt kết nối từ SQL Server")
