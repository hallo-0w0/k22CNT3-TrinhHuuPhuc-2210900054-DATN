"""
Script để reset password cho admin
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.user import User
from models.role import Role

def reset_admin_password():
    """Reset password cho admin user"""
    app = create_app()
    
    with app.app_context():
        # Find admin role
        admin_role = Role.query.filter_by(role_name='ADMIN').first()
        if not admin_role:
            print("❌ Không tìm thấy role ADMIN!")
            return
        
        # Find admin user
        admin = User.query.filter_by(username='admin', role_id=admin_role.role_id).first()
        if not admin:
            print("❌ Không tìm thấy user admin!")
            print("Tạo user admin mới...")
            admin = User(
                username='admin',
                email='admin@cleaningservice.com',
                full_name='Nguyễn Văn Admin',
                phone_number='0901234567',
                address='123 Đường ABC, Quận 1, TP.HCM',
                role_id=admin_role.role_id,
                is_active=True
            )
            db.session.add(admin)
        
        # Set new password
        new_password = input("Nhập mật khẩu mới cho admin (mặc định: admin123): ").strip()
        if not new_password:
            new_password = 'admin123'
        
        admin.set_password(new_password)
        db.session.commit()
        
        print("=" * 50)
        print("✓ Đã reset password thành công!")
        print("=" * 50)
        print(f"Username: admin")
        print(f"Email: admin@cleaningservice.com")
        print(f"Password: {new_password}")
        print("=" * 50)
        print("\nBạn có thể đăng nhập với thông tin trên.")

if __name__ == '__main__':
    try:
        reset_admin_password()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
