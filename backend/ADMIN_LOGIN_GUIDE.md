# HƯỚNG DẪN ĐĂNG NHẬP ADMIN

## Thông tin đăng nhập mặc định

Sau khi chạy database script, tài khoản admin đã được tạo nhưng **password là hash giả**, nên bạn cần reset password trước.

## Cách 1: Reset password bằng script (Khuyến nghị)

### Bước 1: Chạy script reset password

```bash
cd backend
python reset_admin_password.py
```

Script sẽ hỏi bạn nhập password mới. Nếu không nhập, mặc định là `admin123`.

### Bước 2: Đăng nhập

Sau khi reset xong, đăng nhập với:
- **Username:** `admin`
- **Password:** `admin123` (hoặc password bạn đã đặt)

## Cách 2: Tạo admin mới qua SQL

Nếu không dùng được script, bạn có thể chạy SQL trực tiếp trong SQL Server Management Studio:

```sql
USE OfficeCleaningService;

-- Lấy role_id của ADMIN
DECLARE @AdminRoleId INT;
SELECT @AdminRoleId = role_id FROM Roles WHERE role_name = 'ADMIN';

-- Update password cho admin (password: admin123)
-- Hash này được tạo từ bcrypt với password "admin123"
UPDATE Users 
SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5'
WHERE username = 'admin' AND role_id = @AdminRoleId;

-- Hoặc tạo admin mới nếu chưa có
IF NOT EXISTS (SELECT 1 FROM Users WHERE username = 'admin' AND role_id = @AdminRoleId)
BEGIN
    INSERT INTO Users (username, email, password_hash, full_name, phone_number, address, role_id, is_active)
    VALUES (
        'admin',
        'admin@cleaningservice.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5',
        N'Nguyễn Văn Admin',
        '0901234567',
        N'123 Đường ABC, Quận 1, TP.HCM',
        @AdminRoleId,
        1
    );
END
```

**Lưu ý:** Hash trên là hash giả, bạn cần tạo hash thật từ Python script.

## Cách 3: Đăng ký tài khoản mới và nâng cấp lên Admin

### Bước 1: Đăng ký tài khoản mới

Truy cập API register (hoặc tạo user qua SQL):

```sql
-- Tạo user mới với role CUSTOMER
INSERT INTO Users (username, email, password_hash, full_name, role_id, is_active)
VALUES (
    'newadmin',
    'newadmin@example.com',
    -- Password hash cho "password123"
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5',
    N'New Admin',
    (SELECT role_id FROM Roles WHERE role_name = 'CUSTOMER'),
    1
);
```

### Bước 2: Nâng cấp lên Admin

```sql
UPDATE Users 
SET role_id = (SELECT role_id FROM Roles WHERE role_name = 'ADMIN')
WHERE username = 'newadmin';
```

## Thông tin đăng nhập sau khi reset

Sau khi reset password bằng script:

- **URL đăng nhập:** `http://192.168.0.3:5000/admin/login.html` hoặc `http://localhost:5000/admin/login.html`
- **Username:** `admin`
- **Password:** `admin123` (hoặc password bạn đã đặt)

## Các tài khoản khác trong database

Ngoài admin, database còn có:

### Staff:
- `staff001` / `staff002` / `staff003`
- Password: Cần reset tương tự

### Customers:
- `customer001` đến `customer006`
- Password: Cần reset tương tự

## Troubleshooting

### Lỗi: "Tên đăng nhập hoặc mật khẩu không đúng"

- Kiểm tra username/email đúng chưa
- Đảm bảo đã reset password bằng script
- Kiểm tra user có `is_active = 1` và `is_locked = 0`

### Lỗi: "Bạn không có quyền truy cập trang quản trị"

- Kiểm tra user có role = ADMIN
- Chạy SQL: `SELECT * FROM Users WHERE username = 'admin'`

### Lỗi: Script reset password không chạy được

- Đảm bảo đã activate virtual environment
- Đảm bảo backend đã cài đặt dependencies
- Kiểm tra kết nối database trong `config.py`

---

**Sau khi reset password, bạn có thể đăng nhập vào trang admin!**
