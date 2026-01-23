# Frontend - PCLEAR

## Cách Chạy Frontend

### Option 1: Live Server (Khuyến nghị)

1. Mở VS Code
2. Cài extension **Live Server**
3. Click chuột phải vào `index.html` → **Open with Live Server**
4. Trình duyệt sẽ mở tự động tại: `http://127.0.0.1:5500/index.html`

### Option 2: Python HTTP Server

```bash
cd frontend
python -m http.server 8000
```

Truy cập: `http://localhost:8000`

## Cấu Trúc Thư Mục

```
frontend/
├── index.html          # Trang chủ
├── login.html          # Trang đăng nhập
├── admin/
│   └── dashboard.html  # Admin dashboard
├── customer/
│   └── orders.html     # Customer orders
├── staff/
│   └── orders.html     # Staff orders
├── css/
│   └── style.css       # Styles
└── js/
    ├── api.js          # API helper
    ├── auth.js         # Auth helper
    ├── login.js        # Login page script
    └── index.js        # Home page script
```

## Các Trang Chính

- **Trang chủ**: `index.html`
- **Đăng nhập**: `login.html`
- **Admin Dashboard**: `admin/dashboard.html`
- **Customer Orders**: `customer/orders.html`
- **Staff Orders**: `staff/orders.html`

## Lưu Ý

- Đảm bảo Backend đang chạy tại `http://localhost:5000`
- CORS đã được cấu hình để cho phép frontend gọi API
- JWT token được lưu trong `localStorage`
