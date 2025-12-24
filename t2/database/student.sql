CREATE TABLE students (
    ma_sv NVARCHAR(50) PRIMARY KEY,
    ten NVARCHAR(100),
    gioi_tinh NVARCHAR(10),
    ngay_sinh DATE,
    email NVARCHAR(100),
    sdt VARCHAR(20),
    dia_chi NVARCHAR(200)
)
drop table students