# KHẮC PHỤC LỖI KẾT NỐI SQL SERVER

## Lỗi hiện tại

```
Could not open a connection to SQL Server
Server is not found or not accessible
```

## Các bước khắc phục

### Bước 1: Kiểm tra SQL Server đang chạy

1. Mở **SQL Server Configuration Manager**
2. Chọn **SQL Server Services**
3. Kiểm tra các service sau đang **Running**:
   - **SQL Server (SQLEXPRESS)** hoặc **SQL Server (MSSQLSERVER)**
   - **SQL Server Browser** (khuyến nghị bật)

Nếu chưa chạy, **Right-click → Start**

### Bước 2: Xác định Server name chính xác

1. Mở **SQL Server Management Studio (SSMS)**
2. Khi kết nối, xem **Server name** hiển thị
3. Các format thường gặp:
   - `MSI\SQLEXPRESS`
   - `localhost\SQLEXPRESS`
   - `.\SQLEXPRESS`
   - `(local)\SQLEXPRESS`
   - `COMPUTERNAME\SQLEXPRESS`

### Bước 3: Test kết nối bằng script

Chạy script test:

```bash
cd backend
python test_connection.py
```

Script sẽ hỏi thông tin và test kết nối. Nếu thành công, sẽ hiển thị cấu hình đúng.

### Bước 4: Cập nhật config.py

Sau khi test thành công, cập nhật `backend/config.py`:

```python
SQL_SERVER_SERVER = 'MSI\\SQLEXPRESS'  # Server name từ bước 2
SQL_SERVER_DATABASE = 'OfficeCleaningService'
SQL_SERVER_AUTH = 'windows'  # hoặc 'sql'
```

### Bước 5: Kiểm tra SQL Server Browser

Nếu dùng named instance (có `\SQLEXPRESS`), cần bật **SQL Server Browser**:

1. Mở **Services** (Windows + R → `services.msc`)
2. Tìm **SQL Server Browser**
3. **Right-click → Start**
4. **Right-click → Properties → Startup type: Automatic**

### Bước 6: Kiểm tra Firewall

1. Mở **Windows Defender Firewall**
2. **Advanced Settings**
3. **Inbound Rules**
4. Cho phép:
   - **SQL Server** (port 1433)
   - **SQL Server Browser** (port 1434)

### Bước 7: Thử các Server name khác

Nếu vẫn không được, thử các format sau trong `config.py`:

```python
# Thử 1: localhost
SQL_SERVER_SERVER = 'localhost\\SQLEXPRESS'

# Thử 2: Dấu chấm
SQL_SERVER_SERVER = '.\\SQLEXPRESS'

# Thử 3: (local)
SQL_SERVER_SERVER = '(local)\\SQLEXPRESS'

# Thử 4: Tên máy tính
SQL_SERVER_SERVER = 'COMPUTERNAME\\SQLEXPRESS'  # Thay COMPUTERNAME
```

### Bước 8: Dùng SQL Server Authentication

Nếu Windows Authentication không được, thử SQL Authentication:

1. Trong SSMS, **Right-click server → Properties → Security**
2. Chọn **SQL Server and Windows Authentication mode**
3. **OK** và **Restart SQL Server**

4. Tạo login:
   ```sql
   CREATE LOGIN testuser WITH PASSWORD = 'password123';
   ALTER SERVER ROLE sysadmin ADD MEMBER testuser;
   ```

5. Cập nhật `config.py`:
   ```python
   SQL_SERVER_AUTH = 'sql'
   SQL_SERVER_UID = 'testuser'
   SQL_SERVER_PWD = 'password123'
   ```

## Test nhanh với pyodbc

Chạy Python và test:

```python
import pyodbc

# Thử Windows Auth
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\\SQLEXPRESS;'
    'DATABASE=OfficeCleaningService;'
    'Trusted_Connection=yes;'
)
print("Kết nối thành công!")
```

## Sau khi sửa xong

1. Chạy lại: `python reset_admin_password.py`
2. Nếu thành công, chạy: `python app.py`

---

**Nếu vẫn không được, vui lòng cung cấp:**
- Server name bạn dùng trong SSMS
- SQL Server version
- Lỗi chi tiết từ test_connection.py
