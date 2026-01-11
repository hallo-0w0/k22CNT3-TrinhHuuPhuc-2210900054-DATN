# HƯỚNG DẪN CẤU HÌNH SQL SERVER

## Cấu hình đã được thiết lập

File `config.py` đã được cấu hình với các giá trị mặc định:

- **Server:** `MSI\SQLEXPRESS`
- **Database:** `OfficeCleaningService`
- **Authentication:** Windows Authentication (mặc định)
- **ODBC Driver:** ODBC Driver 17 for SQL Server

## Cách cấu hình

### Cách 1: Sử dụng Environment Variables (Khuyến nghị)

Tạo file `.env` trong thư mục `backend/`:

```env
# SQL Server Configuration
SQL_SERVER_SERVER=MSI\SQLEXPRESS
SQL_SERVER_DATABASE=OfficeCleaningService
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
SQL_SERVER_AUTH=windows

# Nếu dùng SQL Server Authentication, thay đổi:
# SQL_SERVER_AUTH=sql
# SQL_SERVER_UID=sa
# SQL_SERVER_PWD=your-password
```

### Cách 2: Sửa trực tiếp trong config.py

Mở file `backend/config.py` và sửa các giá trị:

```python
# Dòng 20-31
SQL_SERVER_SERVER = 'MSI\\SQLEXPRESS'  # Server của bạn
SQL_SERVER_DATABASE = 'OfficeCleaningService'
SQL_SERVER_DRIVER = 'ODBC Driver 17 for SQL Server'
SQL_SERVER_AUTH = 'windows'  # hoặc 'sql'
SQL_SERVER_UID = 'sa'  # Chỉ cần khi SQL_SERVER_AUTH = 'sql'
SQL_SERVER_PWD = 'your-password'  # Chỉ cần khi SQL_SERVER_AUTH = 'sql'
```

## Phương thức Authentication

### Windows Authentication (Mặc định)

Sử dụng tài khoản Windows hiện tại để kết nối. Không cần username/password.

**Cấu hình:**
```python
SQL_SERVER_AUTH = 'windows'
```

**Ưu điểm:**
- Không cần lưu password
- Bảo mật cao
- Dễ quản lý

### SQL Server Authentication

Sử dụng username/password của SQL Server.

**Cấu hình:**
```python
SQL_SERVER_AUTH = 'sql'
SQL_SERVER_UID = 'sa'
SQL_SERVER_PWD = 'your-password'
```

**Lưu ý:**
- Đảm bảo SQL Server đã bật SQL Server Authentication
- Password sẽ được URL encode tự động

## Kiểm tra ODBC Driver

Để kiểm tra ODBC Driver đã cài đặt, chạy lệnh:

```bash
# Windows PowerShell
Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}
```

Hoặc kiểm tra trong **ODBC Data Source Administrator (64-bit)**:
- Mở `odbcad32.exe`
- Tab "Drivers"
- Tìm các driver có tên:
  - `ODBC Driver 17 for SQL Server`
  - `ODBC Driver 18 for SQL Server`
  - `SQL Server Native Client 11.0`

Nếu không có, tải và cài đặt từ Microsoft:
- [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- [ODBC Driver 18 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Kiểm tra kết nối

Sau khi cấu hình, test kết nối bằng cách chạy:

```bash
python test_import.py
```

Hoặc chạy backend:

```bash
python app.py
```

Nếu có lỗi kết nối, kiểm tra:

1. **SQL Server đang chạy:**
   - Mở SQL Server Configuration Manager
   - Kiểm tra SQL Server Services đang Running

2. **Firewall:**
   - Đảm bảo port 1433 (hoặc port của SQL Server) được mở

3. **SQL Server cho phép remote connections:**
   - Mở SQL Server Management Studio
   - Right-click server → Properties → Connections
   - Check "Allow remote connections to this server"

4. **Database đã được tạo:**
   - Chạy script `database/create_database.sql` trong SSMS

## Troubleshooting

### Lỗi: [Microsoft][ODBC Driver Manager] Data source name not found

**Nguyên nhân:** ODBC Driver chưa được cài đặt hoặc tên driver không đúng.

**Giải pháp:**
- Kiểm tra tên driver trong `config.py` khớp với driver đã cài
- Hoặc cài đặt ODBC Driver từ Microsoft

### Lỗi: Login failed for user

**Nguyên nhân:** Username/password sai hoặc user không có quyền.

**Giải pháp:**
- Kiểm tra lại username/password
- Đảm bảo SQL Server Authentication đã được bật
- Kiểm tra user có quyền truy cập database

### Lỗi: Cannot open database requested by the login

**Nguyên nhân:** Database chưa được tạo hoặc user không có quyền truy cập.

**Giải pháp:**
- Chạy script `database/create_database.sql` để tạo database
- Kiểm tra user có quyền truy cập database

### Lỗi: [Microsoft][ODBC Driver 17 for SQL Server]SSL Provider: No credentials are available

**Nguyên nhân:** Vấn đề với SSL/TLS khi kết nối.

**Giải pháp:**
- Thêm `Encrypt=no` vào connection string (chỉ cho development)
- Hoặc cấu hình SSL certificate cho SQL Server

---

**Sau khi cấu hình xong, bạn có thể chạy backend bằng lệnh: `python app.py`**
