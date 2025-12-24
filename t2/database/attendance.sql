CREATE TABLE attendance (
    id INT PRIMARY KEY IDENTITY(1,1),
    ma_sv NVARCHAR(50) NOT NULL,
    ten NVARCHAR(100) NOT NULL,
    attendance_type NVARCHAR(10) NOT NULL,
    timestamp DATETIME DEFAULT GETDATE(),
    face_image VARBINARY(MAX)
);
