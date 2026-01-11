"""
Script test kết nối SQL Server
"""
import pyodbc
import sys

print("=" * 60)
print("KIỂM TRA KẾT NỐI SQL SERVER")
print("=" * 60)
print()

# Thông tin kết nối
server = input("Nhập Server name (ví dụ: MSI\\SQLEXPRESS hoặc localhost\\SQLEXPRESS): ").strip()
if not server:
    server = 'MSI\\SQLEXPRESS'

database = input("Nhập Database name (mặc định: OfficeCleaningService): ").strip()
if not database:
    database = 'OfficeCleaningService'

auth_method = input("Chọn phương thức authentication (1=Windows, 2=SQL): ").strip()
use_windows_auth = auth_method != '2'

if not use_windows_auth:
    uid = input("Username (mặc định: sa): ").strip() or 'sa'
    pwd = input("Password: ").strip()
else:
    uid = ''
    pwd = ''

print()
print("Đang thử kết nối...")
print(f"Server: {server}")
print(f"Database: {database}")
print(f"Authentication: {'Windows' if use_windows_auth else 'SQL Server'}")
print()

try:
    if use_windows_auth:
        # Windows Authentication
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
        )
    else:
        # SQL Server Authentication
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={uid};"
            f"PWD={pwd};"
            f"Trusted_Connection=no;"
        )
    
    print("Connection string:")
    print(connection_string.replace(pwd, '***' if pwd else ''))
    print()
    
    conn = pyodbc.connect(connection_string, timeout=5)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    
    print("=" * 60)
    print("✓ KẾT NỐI THÀNH CÔNG!")
    print("=" * 60)
    print(f"SQL Server Version: {version[:50]}...")
    print()
    
    # Check database exists
    cursor.execute("SELECT name FROM sys.databases WHERE name = ?", database)
    db_exists = cursor.fetchone()
    
    if db_exists:
        print(f"✓ Database '{database}' đã tồn tại")
        
        # Check tables
        cursor.execute(f"USE {database}; SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        table_count = cursor.fetchone()[0]
        print(f"✓ Số bảng: {table_count}")
    else:
        print(f"⚠ Database '{database}' chưa tồn tại")
        print("  Vui lòng chạy script create_database.sql trước")
    
    conn.close()
    
    print()
    print("=" * 60)
    print("CẤU HÌNH CHO config.py:")
    print("=" * 60)
    print(f"SQL_SERVER_SERVER = '{server}'")
    print(f"SQL_SERVER_DATABASE = '{database}'")
    print(f"SQL_SERVER_AUTH = {'windows' if use_windows_auth else 'sql'}")
    if not use_windows_auth:
        print(f"SQL_SERVER_UID = '{uid}'")
        print(f"SQL_SERVER_PWD = '{pwd}'")
    print("=" * 60)
    
except pyodbc.Error as e:
    print("=" * 60)
    print("❌ LỖI KẾT NỐI!")
    print("=" * 60)
    print(f"Error: {e}")
    print()
    print("CÁCH KHẮC PHỤC:")
    print("1. Kiểm tra SQL Server đang chạy:")
    print("   - Mở SQL Server Configuration Manager")
    print("   - Kiểm tra SQL Server Services đang Running")
    print()
    print("2. Kiểm tra Server name:")
    print("   - Mở SQL Server Management Studio")
    print("   - Xem Server name khi kết nối")
    print("   - Thử: localhost\\SQLEXPRESS hoặc .\\SQLEXPRESS")
    print()
    print("3. Kiểm tra SQL Server Browser:")
    print("   - Mở Services (services.msc)")
    print("   - Tìm 'SQL Server Browser'")
    print("   - Start service nếu chưa chạy")
    print()
    print("4. Kiểm tra Firewall:")
    print("   - Cho phép port 1433 (SQL Server)")
    print("   - Cho phép port 1434 (SQL Server Browser)")
    print()
    print("5. Thử kết nối bằng SQL Server Management Studio trước")
    sys.exit(1)

except Exception as e:
    print("=" * 60)
    print("❌ LỖI!")
    print("=" * 60)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
