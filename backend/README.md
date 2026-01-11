# BACKEND API - WEBSITE THƯƠNG MẠI DỊCH VỤ VỆ SINH VĂN PHÒNG

## Mô tả

Backend Flask API cho hệ thống website thương mại dịch vụ vệ sinh văn phòng, hỗ trợ:
- RESTful API
- JWT Authentication
- Role-based Access Control (RBAC)
- Member Level cho khách hàng
- CRUD đầy đủ cho tất cả các chức năng

## Công nghệ sử dụng

- **Python 3.8+**
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - JWT authentication
- **pyodbc** - Kết nối SQL Server
- **bcrypt** - Hash password

## Cấu trúc project

```
backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── README.md              # File này
├── models/                # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── role.py
│   ├── order.py
│   └── ...
├── routes/                # API routes
│   ├── __init__.py
│   ├── auth.py            # Authentication
│   ├── users.py           # Users CRUD
│   ├── services.py        # Services CRUD
│   ├── orders.py          # Orders CRUD
│   └── ...
└── utils/                 # Utilities
    ├── __init__.py
    ├── decorators.py      # Role-based decorators
    └── helpers.py         # Helper functions
```

## Cài đặt

### 1. Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình

Tạo file `.env` trong thư mục `backend/`:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# SQL Server
SQL_SERVER_SERVER=MSI\SQLEXPRESS
SQL_SERVER_DATABASE=OfficeCleaningService
SQL_SERVER_UID=sa
SQL_SERVER_PWD=your-password
SQL_SERVER_TRUSTED_CONNECTION=no
```

Hoặc chỉnh sửa trực tiếp trong `config.py`

### 4. Chạy ứng dụng

```bash
python app.py
```

API sẽ chạy tại: `http://localhost:5000`

## API Endpoints

### Authentication (`/api/auth`)

- `POST /api/auth/register` - Đăng ký
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Lấy thông tin user hiện tại
- `POST /api/auth/logout` - Đăng xuất

### Users (`/api/users`)

- `GET /api/users` - Lấy danh sách users (ADMIN)
- `GET /api/users/<id>` - Lấy chi tiết user
- `POST /api/users` - Tạo user (ADMIN)
- `PUT /api/users/<id>` - Cập nhật user
- `DELETE /api/users/<id>` - Xóa user (ADMIN)

### Services (`/api/services`)

- `GET /api/services` - Lấy danh sách services (public)
- `GET /api/services/<id>` - Lấy chi tiết service (public)
- `POST /api/services` - Tạo service (ADMIN)
- `PUT /api/services/<id>` - Cập nhật service (ADMIN)
- `DELETE /api/services/<id>` - Xóa service (ADMIN)

### Orders (`/api/orders`)

- `GET /api/orders` - Lấy danh sách orders
- `GET /api/orders/<id>` - Lấy chi tiết order
- `POST /api/orders` - Tạo order (CUSTOMER)
- `PUT /api/orders/<id>` - Cập nhật order
- `DELETE /api/orders/<id>` - Hủy order

### Reviews (`/api/reviews`)

- `GET /api/reviews` - Lấy danh sách reviews (public)
- `GET /api/reviews/<id>` - Lấy chi tiết review
- `POST /api/reviews` - Tạo review (CUSTOMER)
- `PUT /api/reviews/<id>` - Cập nhật review
- `DELETE /api/reviews/<id>` - Xóa review (ADMIN)

### Invoices (`/api/invoices`)

- `GET /api/invoices` - Lấy danh sách invoices
- `GET /api/invoices/<id>` - Lấy chi tiết invoice
- `POST /api/invoices` - Tạo invoice (ADMIN)
- `PUT /api/invoices/<id>` - Cập nhật invoice (ADMIN)

### Consultations (`/api/consultations`)

- `GET /api/consultations` - Lấy danh sách consultations (ADMIN)
- `GET /api/consultations/<id>` - Lấy chi tiết consultation (ADMIN)
- `POST /api/consultations` - Tạo consultation (public)
- `PUT /api/consultations/<id>` - Cập nhật consultation (ADMIN)
- `DELETE /api/consultations/<id>` - Xóa consultation (ADMIN)

### Member Levels (`/api/member-levels`)

- `GET /api/member-levels` - Lấy danh sách member levels (public)
- `GET /api/member-levels/<id>` - Lấy chi tiết member level (public)
- `POST /api/member-levels` - Tạo member level (ADMIN)
- `PUT /api/member-levels/<id>` - Cập nhật member level (ADMIN)
- `DELETE /api/member-levels/<id>` - Xóa member level (ADMIN)

### Dashboard (`/api/dashboard`)

- `GET /api/dashboard/stats` - Lấy thống kê tổng quan (ADMIN)

## Authentication

### Đăng nhập

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "customer001",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": 1,
    "username": "customer001",
    ...
  }
}
```

### Sử dụng token

Thêm header vào request:
```
Authorization: Bearer <access_token>
```

## Phân quyền

### Roles

- **GUEST** - Không lưu trong DB, không cần token
- **CUSTOMER** - Khách hàng
- **STAFF** - Nhân viên
- **ADMIN** - Quản trị viên

### Member Levels (chỉ cho CUSTOMER)

- **SILVER** - Giảm 0%
- **GOLD** - Giảm 5%
- **DIAMOND** - Giảm 10%

**Lưu ý:** Member Level KHÔNG dùng để phân quyền API, chỉ dùng cho business logic (giảm giá, ưu tiên).

## Testing với Postman

1. Import collection từ file `postman_collection.json` (nếu có)
2. Hoặc tạo request thủ công:
   - Đăng nhập để lấy token
   - Copy token vào header `Authorization: Bearer <token>`
   - Test các endpoints

## Lưu ý

1. **Password hash:** Dữ liệu mẫu trong database có password hash giả, cần reset password khi test
2. **ODBC Driver:** Đảm bảo đã cài ODBC Driver 17 for SQL Server
3. **Database:** Chạy script `database/create_database.sql` trước khi chạy API
4. **CORS:** Cấu hình CORS_ORIGINS trong config nếu frontend chạy trên domain khác

## Troubleshooting

### Lỗi kết nối SQL Server

- Kiểm tra SQL Server đang chạy
- Kiểm tra connection string trong config
- Kiểm tra ODBC Driver đã cài đặt

### Lỗi import

- Đảm bảo đã activate virtual environment
- Chạy `pip install -r requirements.txt`

### Lỗi JWT

- Kiểm tra SECRET_KEY và JWT_SECRET_KEY trong config
- Đảm bảo token được gửi đúng format trong header

---

**Tài liệu sẽ được cập nhật khi có thay đổi.**
