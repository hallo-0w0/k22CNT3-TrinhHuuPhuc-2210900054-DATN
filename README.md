# 🧹 PCLEAR – Office Cleaning Service Platform

Website thương mại cung cấp dịch vụ vệ sinh văn phòng.

## 📋 Yêu Cầu Hệ Thống

- Python 3.8+
- SQL Server 2019/2022 hoặc SQL Server Express
- ODBC Driver 17 for SQL Server

## 🚀 Cài Đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd k22CNT3-TrinhHuuPhuc-2210900054-DATN-3
```

### 2. Tạo virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình Database

#### a. Chạy SQL Script
- Mở SQL Server Management Studio (SSMS)
- Kết nối đến SQL Server (ví dụ: `MSI\SQLEXPRESS` với Windows Authentication)
- Chạy script: `Database/k22CNT3-TrinhHuuPhuc-2210900054-DATN.sql`
- Kiểm tra database `OfficeCleaningService` đã được tạo

#### b. Tạo file `.env`
Copy `env.example` thành `.env` và cập nhật:

```env
# Với SQL Server Express (có instance name)
SQL_SERVER_SERVER=MSI\SQLEXPRESS
# hoặc
SQL_SERVER_SERVER=localhost\SQLEXPRESS
# hoặc
SQL_SERVER_SERVER=.\SQLEXPRESS

# Với SQL Server Default Instance (không có instance name)
# SQL_SERVER_SERVER=localhost

SQL_SERVER_DATABASE=OfficeCleaningService
SQL_SERVER_TRUSTED_CONNECTION=yes
JWT_SECRET_KEY=your-secret-key-change-in-production-12345
```

**Lưu ý:** 
- Nếu SQL Server Express với instance `SQLEXPRESS`, dùng format: `SERVER\SQLEXPRESS`
- Kiểm tra server name trong SSMS khi kết nối (ví dụ: `MSI\SQLEXPRESS`)

### 5. Tạo Admin đầu tiên
```bash
python scripts/seed_admin.py
```

Script sẽ:
- Kiểm tra kết nối database
- Tạo admin với email: `admin@pclear.vn`
- Bạn sẽ được yêu cầu nhập mật khẩu

### 6. Chạy Backend
```bash
python run.py
```

Hoặc:
```bash
python -m backend.app
```

Backend sẽ chạy tại: `http://localhost:5000`

## 📁 Cấu Trúc Project

```
.
├── backend/              # Backend Flask API
│   ├── models/          # Database models
│   ├── routes/          # API routes
│   ├── config.py        # Configuration
│   └── app.py           # Application entry point
├── frontend/            # Frontend HTML/JS/CSS
├── Database/            # SQL scripts
├── scripts/             # Utility scripts
└── requirements.txt     # Python dependencies
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Lấy thông tin user hiện tại
- `POST /api/auth/logout` - Đăng xuất

### Services
- `GET /api/services` - Lấy danh sách dịch vụ
- `GET /api/services/<id>` - Lấy chi tiết dịch vụ
- `GET /api/services/categories` - Lấy danh mục dịch vụ

### Orders
- `GET /api/orders` - Lấy danh sách đơn hàng
- `POST /api/orders` - Tạo đơn hàng mới
- `GET /api/orders/<id>` - Lấy chi tiết đơn hàng
- `PUT /api/orders/<id>/status` - Cập nhật trạng thái đơn
- `POST /api/orders/<id>/progress` - Thêm tiến độ đơn hàng
- `GET /api/orders/<id>/progress` - Lấy tiến độ đơn hàng

### Content
- `GET /api/content/<type>` - Lấy nội dung theo type

## 🔐 Default Admin Account

Sau khi chạy `seed_admin.py`:
- Email: `admin@pclear.vn`
- Password: (mật khẩu bạn đã nhập khi chạy script)

## 🔧 Troubleshooting

### Lỗi kết nối Database
1. Kiểm tra SQL Server đang chạy (Services hoặc SQL Server Configuration Manager)
2. Kiểm tra server name trong SSMS khi kết nối thành công
3. Cập nhật `SQL_SERVER_SERVER` trong `.env` đúng với server name
4. Với SQL Server Express: dùng format `SERVER\SQLEXPRESS`
5. Kiểm tra ODBC Driver 17 đã cài đặt

### Lỗi "Cannot open database"
- Đảm bảo đã chạy SQL script để tạo database
- Kiểm tra `SQL_SERVER_DATABASE=OfficeCleaningService` trong `.env`

### Lỗi CORS
- Kiểm tra `CORS_ORIGINS` trong `.env`
- Đảm bảo frontend và backend đang chạy trên đúng port


