# 🚀 Hướng Dẫn Nhanh - PCLEAR Project

## Bước 1: Setup Database

1. Mở SQL Server Management Studio (SSMS)
2. Chạy script: `Database/k22CNT3-TrinhHuuPhuc-2210900054-DATN.sql`
3. Kiểm tra database `OfficeCleaningService` đã được tạo

## Bước 2: Setup Backend

1. Tạo virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# hoặc
source venv/bin/activate  # Linux/Mac
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Tạo file `.env` từ `env.example` và cập nhật thông tin:
```env
# Với SQL Server Express, dùng format: SERVER\INSTANCE
# Ví dụ: MSI\SQLEXPRESS, localhost\SQLEXPRESS, .\SQLEXPRESS
SQL_SERVER_SERVER=MSI\SQLEXPRESS
SQL_SERVER_DATABASE=OfficeCleaningService
JWT_SECRET_KEY=your-secret-key-here
```

**Lưu ý về SQL Server Express:**
- Nếu SQL Server Express đang chạy trên máy local với instance name `SQLEXPRESS`:
  - Dùng: `localhost\SQLEXPRESS` hoặc `.\SQLEXPRESS` hoặc `MSI\SQLEXPRESS`
- Nếu SQL Server Default Instance (không có instance name):
  - Dùng: `localhost` hoặc `.`

4. Tạo Admin đầu tiên:
```bash
python scripts/seed_admin.py
```

5. Chạy Backend:
```bash
python run.py
```

Hoặc nếu muốn chạy từ thư mục backend:
```bash
cd backend
python -m app
```

Backend sẽ chạy tại: `http://localhost:5000`

## Bước 3: Setup Frontend

1. Mở `frontend/index.html` bằng Live Server (VS Code extension) hoặc bất kỳ web server nào
2. Hoặc dùng Python simple server:
```bash
cd frontend
python -m http.server 8000
```

Frontend sẽ chạy tại: `http://localhost:8000`

## Bước 4: Test

1. Mở trình duyệt: `http://localhost:8000`
2. Đăng nhập với:
   - Email: `admin@pclear.vn`
   - Password: (mật khẩu bạn đã nhập khi chạy seed_admin.py)

3. Sau khi đăng nhập, bạn sẽ được redirect theo role:
   - **ADMIN** → `/admin/dashboard.html`
   - **CUSTOMER** → `/customer/orders.html`
   - **STAFF** → `/staff/orders.html`

## 📝 Lưu Ý

- Đảm bảo SQL Server đang chạy
- Đảm bảo đã cài ODBC Driver 17 for SQL Server
- Backend và Frontend phải chạy đồng thời
- CORS đã được cấu hình để cho phép frontend gọi API

## 🔧 Troubleshooting

### Lỗi kết nối Database
- Kiểm tra SQL Server đang chạy
- Kiểm tra thông tin trong `.env`:
  - Với SQL Server Express: `SQL_SERVER_SERVER=MSI\SQLEXPRESS` (hoặc `localhost\SQLEXPRESS`)
  - Với SQL Server Default: `SQL_SERVER_SERVER=localhost`
- Kiểm tra ODBC Driver đã cài đặt
- Test kết nối bằng SSMS trước khi chạy backend
- Đảm bảo Windows Authentication hoạt động (nếu dùng Trusted_Connection=yes)

### Lỗi CORS
- Kiểm tra `CORS_ORIGINS` trong `.env`
- Đảm bảo frontend và backend đang chạy trên đúng port

### Lỗi JWT
- Kiểm tra `JWT_SECRET_KEY` trong `.env`
- Xóa token cũ trong localStorage và đăng nhập lại

## 📚 Tài Liệu

- Chi tiết đầy đủ: `readme_pclear.md`
- API Documentation: Xem code trong `backend/routes/`
