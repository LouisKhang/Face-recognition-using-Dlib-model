CREATE TABLE dbo.users (
    user_id NVARCHAR(50) PRIMARY KEY ,
	name NVARCHAR(100),
	gender NVARCHAR(10),
    username NVARCHAR(50) NOT NULL,
    password NVARCHAR(50) NOT NULL,
    role NVARCHAR(50),    
    birthday DATE,
    email NVARCHAR(100),
    phone NVARCHAR(20),  -- Cột số điện thoại
    address NVARCHAR(255),  -- Cột địa chỉ
);
drop table users