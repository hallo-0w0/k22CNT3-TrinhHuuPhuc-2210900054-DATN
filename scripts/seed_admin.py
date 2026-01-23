"""
Script tạo Admin đầu tiên
Chạy: python scripts/seed_admin.py
"""
import sys
import os

# Thêm parent directory vào path để import backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import create_app, db
from backend.models.user import User, Role, MemberLevel
from werkzeug.security import generate_password_hash

def create_admin():
    """Tạo admin đầu tiên"""
    app = create_app()
    
    with app.app_context():
        # Test kết nối database
        try:
            db.session.execute(db.text('SELECT 1'))
            print("✅ Kết nối database thành công!")
        except Exception as e:
            print(f"❌ Lỗi kết nối database: {e}")
            print("\n💡 Kiểm tra:")
            print("  1. SQL Server đang chạy")
            print("  2. File .env có cấu hình đúng:")
            print("     SQL_SERVER_SERVER=MSI\\SQLEXPRESS (hoặc localhost\\SQLEXPRESS)")
            print("     SQL_SERVER_DATABASE=OfficeCleaningService")
            print("  3. Đã chạy SQL script để tạo database")
            return
        
        # Kiểm tra đã có admin chưa
        admin_role = Role.query.filter_by(role_name='ADMIN').first()
        if not admin_role:
            print("❌ Không tìm thấy role ADMIN. Vui lòng chạy SQL script trước!")
            return
        
        existing_admin = User.query.filter_by(
            role_id=admin_role.role_id,
            email='admin@pclear.vn'
        ).first()
        
        if existing_admin:
            print("⚠️  Admin đã tồn tại!")
            response = input("Bạn có muốn đặt lại mật khẩu? (y/n): ")
            if response.lower() != 'y':
                return
        
        # Tạo hoặc cập nhật admin
        password = input("Nhập mật khẩu cho admin (mặc định: admin123): ").strip()
        if not password:
            password = "admin123"
        
        password_hash = generate_password_hash(password)
        
        if existing_admin:
            # Cập nhật bằng raw SQL để tránh conflict với trigger
            db.session.execute(
                db.text("""
                    UPDATE Users 
                    SET password_hash = :password_hash,
                        is_active = 1,
                        is_locked = 0,
                        updated_at = GETDATE()
                    WHERE user_id = :user_id
                """),
                {
                    'password_hash': password_hash,
                    'user_id': existing_admin.user_id
                }
            )
            db.session.commit()
            print("✅ Đã cập nhật mật khẩu admin!")
        else:
            # Dùng raw SQL INSERT để tránh conflict với trigger (OUTPUT clause)
            # Lưu ý: Admin KHÔNG có member_level_id (chỉ CUSTOMER mới có)
            db.session.execute(
                db.text("""
                    INSERT INTO Users (username, email, password_hash, full_name, role_id, member_level_id, is_active, is_locked, created_at, updated_at)
                    VALUES (:username, :email, :password_hash, :full_name, :role_id, NULL, 1, 0, GETDATE(), GETDATE())
                """),
                {
                    'username': 'admin',
                    'email': 'admin@pclear.vn',
                    'password_hash': password_hash,
                    'full_name': 'System Admin',
                    'role_id': admin_role.role_id
                }
            )
            db.session.commit()
            print("✅ Đã tạo admin thành công!")
        
        print(f"\n📧 Email: admin@pclear.vn")
        print(f"🔑 Password: {password}")
        print("\n⚠️  Lưu ý: Đổi mật khẩu sau khi đăng nhập lần đầu!")

if __name__ == '__main__':
    create_admin()
