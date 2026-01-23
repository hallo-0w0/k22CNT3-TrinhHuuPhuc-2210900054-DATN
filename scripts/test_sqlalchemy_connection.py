"""
Script test kết nối SQL Server qua SQLAlchemy
Chạy: python scripts/test_sqlalchemy_connection.py
"""
import sys
import os

# Thêm parent directory vào path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import create_app, db

def test_sqlalchemy_connection():
    """Test kết nối qua SQLAlchemy"""
    
    print("=" * 60)
    print("🔍 TEST KẾT NỐI SQL SERVER QUA SQLALCHEMY")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        print(f"\n📋 Connection String:")
        print(f"   {app.config['SQLALCHEMY_DATABASE_URI'][:100]}...")
        
        try:
            # Test kết nối
            db.session.execute(db.text('SELECT 1'))
            print("\n✅ KẾT NỐI THÀNH CÔNG qua SQLAlchemy!")
            
            # Test query database
            result = db.session.execute(db.text("SELECT name FROM sys.databases WHERE name = 'OfficeCleaningService'"))
            db_exists = result.fetchone()
            
            if db_exists:
                print("✅ Database 'OfficeCleaningService' tồn tại!")
                
                # Test query table
                try:
                    result = db.session.execute(db.text("SELECT COUNT(*) FROM Roles"))
                    count = result.fetchone()[0]
                    print(f"✅ Có thể query database! (Roles table có {count} records)")
                except Exception as e:
                    print(f"⚠️  Database tồn tại nhưng chưa có tables: {e}")
                    print("💡 Hãy chạy SQL script để tạo tables")
            else:
                print("❌ Database 'OfficeCleaningService' KHÔNG tồn tại!")
                print("💡 Hãy chạy SQL script để tạo database")
            
            return True
            
        except Exception as e:
            print(f"\n❌ LỖI KẾT NỐI: {e}")
            print("\n💡 Kiểm tra:")
            print("  1. File .env có cấu hình đúng")
            print("  2. SQL Server đang chạy")
            print("  3. Database đã được tạo")
            return False

if __name__ == '__main__':
    test_sqlalchemy_connection()
