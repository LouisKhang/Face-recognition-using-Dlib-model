CREATE TABLE dbo.login_history (
    id INT PRIMARY KEY,
    username NVARCHAR(50),
    login_time DATETIME,
    success BIT
);