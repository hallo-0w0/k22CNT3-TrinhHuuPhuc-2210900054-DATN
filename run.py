"""
File chạy Flask app từ root directory
Chạy: python run.py
"""
from backend import create_app
from backend.models import *  # Import tất cả models để SQLAlchemy nhận diện

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PCLEAR Backend Server")
    print("=" * 60)
    print("📡 Server đang chạy tại: http://localhost:5000")
    print("📚 API Documentation:")
    print("   - POST   /api/auth/login")
    print("   - GET    /api/auth/me")
    print("   - GET    /api/services")
    print("   - GET    /api/orders")
    print("   - GET    /api/content/<type>")
    print("=" * 60)
    print("\n⚠️  Nhấn Ctrl+C để dừng server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
