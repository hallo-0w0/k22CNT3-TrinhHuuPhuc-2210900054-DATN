"""
Script test kết nối SQL Server
Chạy: python scripts/test_db_connection.py
"""
import sys
import os

# Thêm parent directory vào path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pyodbc
from backend.config import Config

def test_connection():
    """Test kết nối SQL Server với nhiều cách khác nhau"""
    
    print("=" * 60)
    print("🔍 TEST KẾT NỐI SQL SERVER")
    print("=" * 60)
    
    # Lấy config
    config = Config()
    server = config.SQL_SERVER_SERVER
    database = config.SQL_SERVER_DATABASE
    driver = config.SQL_SERVER_DRIVER
    
    print(f"\n📋 Thông tin cấu hình:")
    print(f"   Server: {server}")
    print(f"   Database: {database}")
    print(f"   Driver: {driver}")
    print(f"   Trusted Connection: {config.SQL_SERVER_TRUSTED_CONNECTION}")
    
    # Test 1: Kết nối trực tiếp với pyodbc
    print(f"\n{'='*60}")
    print("TEST 1: Kết nối trực tiếp với pyodbc")
    print(f"{'='*60}")
    
    connection_strings = [
        # Format 1: Với instance name
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;",
        # Format 2: Với localhost
        f"DRIVER={{{driver}}};SERVER=localhost\\SQLEXPRESS;DATABASE={database};Trusted_Connection=yes;",
        # Format 3: Với . (local)
        f"DRIVER={{{driver}}};SERVER=.\\SQLEXPRESS;DATABASE={database};Trusted_Connection=yes;",
        # Format 4: Chỉ localhost (nếu default instance)
        f"DRIVER={{{driver}}};SERVER=localhost;DATABASE={database};Trusted_Connection=yes;",
    ]
    
    success = False
    for i, conn_str in enumerate(connection_strings, 1):
        try:
            print(f"\n🔄 Thử connection string {i}...")
            print(f"   {conn_str[:80]}...")
            
            conn = pyodbc.connect(conn_str, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            
            print(f"   ✅ KẾT NỐI THÀNH CÔNG!")
            print(f"   📦 SQL Server Version: {version[:50]}...")
            
            # Test database
            cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{database}'")
            db_exists = cursor.fetchone()
            
            if db_exists:
                print(f"   ✅ Database '{database}' tồn tại!")
            else:
                print(f"   ⚠️  Database '{database}' KHÔNG tồn tại!")
                print(f"   💡 Hãy chạy SQL script để tạo database")
            
            cursor.close()
            conn.close()
            success = True
            
            print(f"\n✅ Sử dụng connection string này trong file .env:")
            if i == 1:
                print(f"   SQL_SERVER_SERVER={server}")
            elif i == 2:
                print(f"   SQL_SERVER_SERVER=localhost\\SQLEXPRESS")
            elif i == 3:
                print(f"   SQL_SERVER_SERVER=.\\SQLEXPRESS")
            elif i == 4:
                print(f"   SQL_SERVER_SERVER=localhost")
            
            break
            
        except pyodbc.Error as e:
            print(f"   ❌ Thất bại: {str(e)[:100]}")
            continue
        except Exception as e:
            print(f"   ❌ Lỗi: {str(e)[:100]}")
            continue
    
    if not success:
        print(f"\n{'='*60}")
        print("❌ KHÔNG THỂ KẾT NỐI!")
        print(f"{'='*60}")
        print("\n💡 Các bước kiểm tra:")
        print("1. Kiểm tra SQL Server đang chạy:")
        print("   - Mở Services (services.msc)")
        print("   - Tìm 'SQL Server (SQLEXPRESS)' hoặc 'SQL Server (MSSQLSERVER)'")
        print("   - Đảm bảo Status = Running")
        print("\n2. Kiểm tra SQL Server Browser đang chạy:")
        print("   - Tìm 'SQL Server Browser' trong Services")
        print("   - Đảm bảo Status = Running")
        print("\n3. Kiểm tra server name trong SSMS:")
        print("   - Mở SSMS và kết nối thành công")
        print("   - Xem server name ở Object Explorer (ví dụ: MSI\\SQLEXPRESS)")
        print("   - Dùng chính xác server name đó trong file .env")
        print("\n4. Thử các format khác trong file .env:")
        print("   - localhost\\SQLEXPRESS")
        print("   - .\\SQLEXPRESS")
        print("   - localhost (nếu default instance)")
        print("\n5. Kiểm tra ODBC Driver:")
        print("   - Mở ODBC Data Source Administrator (odbcad32.exe)")
        print("   - Tab 'Drivers'")
        print("   - Tìm 'ODBC Driver 17 for SQL Server'")
    
    return success

if __name__ == '__main__':
    test_connection()
