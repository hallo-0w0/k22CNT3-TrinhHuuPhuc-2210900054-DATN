
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'OfficeCleaningService')
BEGIN
    CREATE DATABASE OfficeCleaningService;
END
GO

USE OfficeCleaningService;
GO

-- =============================================
-- 1. BẢNG ROLE (Vai trò người dùng)
-- =============================================
IF OBJECT_ID('Roles', 'U') IS NOT NULL
    DROP TABLE Roles;
GO

CREATE TABLE Roles (
    role_id INT PRIMARY KEY IDENTITY(1,1),
    role_name NVARCHAR(50) NOT NULL UNIQUE,
    role_description NVARCHAR(255),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);
GO

-- =============================================
-- 2. BẢNG MEMBER LEVEL (Cấp độ thành viên - chỉ cho CUSTOMER)
-- =============================================
IF OBJECT_ID('MemberLevels', 'U') IS NOT NULL
    DROP TABLE MemberLevels;
GO

CREATE TABLE MemberLevels (
    member_level_id INT PRIMARY KEY IDENTITY(1,1),
    level_code NVARCHAR(20) NOT NULL UNIQUE, -- SILVER, GOLD, DIAMOND
    level_name NVARCHAR(50) NOT NULL, -- Bạc, Vàng, Kim cương
    discount_percentage DECIMAL(5,2) NOT NULL DEFAULT 0, -- % giảm giá
    min_total_amount DECIMAL(18,2), -- Tổng giá trị tối thiểu
    min_service_count INT, -- Số lần sử dụng tối thiểu
    min_continuous_months INT, -- Số tháng liên tục tối thiểu
    description NVARCHAR(500),
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);
GO

-- =============================================
-- 3. BẢNG USERS (Người dùng)
-- =============================================
IF OBJECT_ID('Users', 'U') IS NOT NULL
    DROP TABLE Users;
GO

CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(100) NOT NULL UNIQUE,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    full_name NVARCHAR(255) NOT NULL,
    phone_number NVARCHAR(20),
    address NVARCHAR(500),
    role_id INT NOT NULL,
    member_level_id INT NULL, -- Chỉ áp dụng cho CUSTOMER
    is_active BIT DEFAULT 1,
    is_locked BIT DEFAULT 0,
    last_login DATETIME,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (role_id) REFERENCES Roles(role_id),
    FOREIGN KEY (member_level_id) REFERENCES MemberLevels(member_level_id)
);
GO

-- Index cho tìm kiếm
CREATE INDEX IX_Users_Role ON Users(role_id);
CREATE INDEX IX_Users_Email ON Users(email);
CREATE INDEX IX_Users_MemberLevel ON Users(member_level_id);
GO

-- Trigger: Đảm bảo Member Level chỉ áp dụng cho CUSTOMER
IF OBJECT_ID('TRG_Users_MemberLevel_Check', 'TR') IS NOT NULL
    DROP TRIGGER TRG_Users_MemberLevel_Check;
GO

CREATE TRIGGER TRG_Users_MemberLevel_Check
ON Users
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @CustomerRoleId INT;
    SELECT @CustomerRoleId = role_id FROM Roles WHERE role_name = 'CUSTOMER';
    
    IF EXISTS (
        SELECT 1 
        FROM inserted i
        WHERE i.member_level_id IS NOT NULL 
          AND i.role_id != @CustomerRoleId
    )
    BEGIN
        RAISERROR('Member Level chỉ có thể áp dụng cho CUSTOMER!', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END
    
    IF EXISTS (
        SELECT 1 
        FROM inserted i
        WHERE i.member_level_id IS NOT NULL 
          AND i.role_id = @CustomerRoleId
          AND NOT EXISTS (SELECT 1 FROM MemberLevels ml WHERE ml.member_level_id = i.member_level_id)
    )
    BEGIN
        RAISERROR('Member Level không hợp lệ!', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END
END;
GO

-- =============================================
-- 4. BẢNG SERVICE CATEGORIES (Danh mục dịch vụ)
-- =============================================
IF OBJECT_ID('ServiceCategories', 'U') IS NOT NULL
    DROP TABLE ServiceCategories;
GO

CREATE TABLE ServiceCategories (
    category_id INT PRIMARY KEY IDENTITY(1,1),
    category_name NVARCHAR(255) NOT NULL,
    category_description NVARCHAR(500),
    display_order INT DEFAULT 0,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);
GO

-- =============================================
-- 5. BẢNG SERVICES (Dịch vụ)
-- =============================================
IF OBJECT_ID('Services', 'U') IS NOT NULL
    DROP TABLE Services;
GO

CREATE TABLE Services (
    service_id INT PRIMARY KEY IDENTITY(1,1),
    service_name NVARCHAR(255) NOT NULL,
    service_description NVARCHAR(1000),
    category_id INT NOT NULL,
    base_price DECIMAL(18,2) NOT NULL,
    duration_hours DECIMAL(5,2), -- Thời gian thực hiện (giờ)
    unit NVARCHAR(50), -- Đơn vị: m2, phòng, lần, v.v.
    is_active BIT DEFAULT 1,
    display_order INT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (category_id) REFERENCES ServiceCategories(category_id)
);
GO

CREATE INDEX IX_Services_Category ON Services(category_id);
GO

-- =============================================
-- 6. BẢNG ORDER STATUS (Trạng thái đơn hàng)
-- =============================================
IF OBJECT_ID('OrderStatus', 'U') IS NOT NULL
    DROP TABLE OrderStatus;
GO

CREATE TABLE OrderStatus (
    status_id INT PRIMARY KEY IDENTITY(1,1),
    status_code NVARCHAR(50) NOT NULL UNIQUE, -- PENDING, CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED
    status_name NVARCHAR(100) NOT NULL,
    status_description NVARCHAR(255),
    display_order INT DEFAULT 0
);
GO

-- =============================================
-- 7. BẢNG ORDERS (Đơn dịch vụ)
-- =============================================
IF OBJECT_ID('Orders', 'U') IS NOT NULL
    DROP TABLE Orders;
GO

CREATE TABLE Orders (
    order_id INT PRIMARY KEY IDENTITY(1,1),
    order_code NVARCHAR(50) NOT NULL UNIQUE, -- Mã đơn hàng tự động
    customer_id INT NOT NULL,
    service_id INT NOT NULL,
    order_date DATETIME NOT NULL DEFAULT GETDATE(),
    scheduled_date DATETIME NOT NULL, -- Ngày giờ đặt lịch
    scheduled_time TIME, -- Giờ cụ thể
    service_address NVARCHAR(500) NOT NULL,
    quantity DECIMAL(10,2) DEFAULT 1, -- Số lượng
    unit_price DECIMAL(18,2) NOT NULL, -- Giá đơn vị
    discount_percentage DECIMAL(5,2) DEFAULT 0, -- % giảm giá theo member level
    discount_amount DECIMAL(18,2) DEFAULT 0, -- Số tiền giảm
    total_amount DECIMAL(18,2) NOT NULL, -- Tổng tiền sau giảm giá
    notes NVARCHAR(1000), -- Ghi chú từ khách hàng
    status_id INT NOT NULL DEFAULT 1, -- Mặc định: PENDING
    priority INT DEFAULT 0, -- Độ ưu tiên (dựa trên member level)
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (customer_id) REFERENCES Users(user_id),
    FOREIGN KEY (service_id) REFERENCES Services(service_id),
    FOREIGN KEY (status_id) REFERENCES OrderStatus(status_id)
);
GO

CREATE INDEX IX_Orders_Customer ON Orders(customer_id);
CREATE INDEX IX_Orders_Service ON Orders(service_id);
CREATE INDEX IX_Orders_Status ON Orders(status_id);
CREATE INDEX IX_Orders_ScheduledDate ON Orders(scheduled_date);
CREATE INDEX IX_Orders_Priority ON Orders(priority DESC);
GO

-- =============================================
-- 8. BẢNG ORDER ASSIGNMENTS (Phân công nhân viên)
-- =============================================
IF OBJECT_ID('OrderAssignments', 'U') IS NOT NULL
    DROP TABLE OrderAssignments;
GO

CREATE TABLE OrderAssignments (
    assignment_id INT PRIMARY KEY IDENTITY(1,1),
    order_id INT NOT NULL,
    staff_id INT NOT NULL,
    assigned_by INT NOT NULL, -- Admin phân công
    assigned_at DATETIME DEFAULT GETDATE(),
    notes NVARCHAR(500),
    is_active BIT DEFAULT 1,
    
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES Users(user_id),
    FOREIGN KEY (assigned_by) REFERENCES Users(user_id),
    
    CONSTRAINT UQ_Order_Staff_Active UNIQUE (order_id, staff_id, is_active)
);
GO

CREATE INDEX IX_OrderAssignments_Order ON OrderAssignments(order_id);
CREATE INDEX IX_OrderAssignments_Staff ON OrderAssignments(staff_id);
GO

-- =============================================
-- 9. BẢNG ORDER STATUS HISTORY (Lịch sử thay đổi trạng thái)
-- =============================================
IF OBJECT_ID('OrderStatusHistory', 'U') IS NOT NULL
    DROP TABLE OrderStatusHistory;
GO

CREATE TABLE OrderStatusHistory (
    history_id INT PRIMARY KEY IDENTITY(1,1),
    order_id INT NOT NULL,
    old_status_id INT,
    new_status_id INT NOT NULL,
    changed_by INT NOT NULL, -- User thay đổi
    change_reason NVARCHAR(500),
    created_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (old_status_id) REFERENCES OrderStatus(status_id),
    FOREIGN KEY (new_status_id) REFERENCES OrderStatus(status_id),
    FOREIGN KEY (changed_by) REFERENCES Users(user_id)
);
GO

CREATE INDEX IX_OrderStatusHistory_Order ON OrderStatusHistory(order_id);
GO

-- =============================================
-- 10. BẢNG ORDER PROGRESS (Tiến độ công việc - từ nhân viên)
-- =============================================
IF OBJECT_ID('OrderProgress', 'U') IS NOT NULL
    DROP TABLE OrderProgress;
GO

CREATE TABLE OrderProgress (
    progress_id INT PRIMARY KEY IDENTITY(1,1),
    order_id INT NOT NULL,
    staff_id INT NOT NULL,
    progress_note NVARCHAR(1000),
    image_urls NVARCHAR(MAX), -- JSON array các URL hình ảnh
    issue_report NVARCHAR(1000), -- Báo cáo vấn đề
    created_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES Users(user_id)
);
GO

CREATE INDEX IX_OrderProgress_Order ON OrderProgress(order_id);
CREATE INDEX IX_OrderProgress_Staff ON OrderProgress(staff_id);
GO

-- =============================================
-- 11. BẢNG INVOICES (Hóa đơn)
-- =============================================
IF OBJECT_ID('Invoices', 'U') IS NOT NULL
    DROP TABLE Invoices;
GO

CREATE TABLE Invoices (
    invoice_id INT PRIMARY KEY IDENTITY(1,1),
    invoice_code NVARCHAR(50) NOT NULL UNIQUE,
    order_id INT NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    invoice_date DATETIME DEFAULT GETDATE(),
    subtotal DECIMAL(18,2) NOT NULL,
    discount_amount DECIMAL(18,2) DEFAULT 0,
    tax_amount DECIMAL(18,2) DEFAULT 0,
    total_amount DECIMAL(18,2) NOT NULL,
    payment_status NVARCHAR(50) DEFAULT 'PENDING', -- PENDING, PAID, CANCELLED
    payment_date DATETIME,
    payment_method NVARCHAR(50),
    notes NVARCHAR(500),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES Users(user_id)
);
GO

CREATE INDEX IX_Invoices_Order ON Invoices(order_id);
CREATE INDEX IX_Invoices_Customer ON Invoices(customer_id);
CREATE INDEX IX_Invoices_InvoiceDate ON Invoices(invoice_date);
GO

-- =============================================
-- 12. BẢNG REVIEWS (Đánh giá dịch vụ)
-- =============================================
IF OBJECT_ID('Reviews', 'U') IS NOT NULL
    DROP TABLE Reviews;
GO

CREATE TABLE Reviews (
    review_id INT PRIMARY KEY IDENTITY(1,1),
    order_id INT NOT NULL,
    customer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5), -- 1-5 sao
    review_text NVARCHAR(1000),
    is_public BIT DEFAULT 1, -- Có hiển thị công khai không
    is_verified BIT DEFAULT 0, -- Đã xác thực (chỉ đánh giá sau khi hoàn thành)
    admin_response NVARCHAR(500), -- Phản hồi từ admin
    admin_response_by INT,
    admin_response_at DATETIME,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES Users(user_id),
    FOREIGN KEY (admin_response_by) REFERENCES Users(user_id),
    
    CONSTRAINT UQ_Order_Review UNIQUE (order_id) -- Mỗi đơn chỉ được đánh giá 1 lần
);
GO

CREATE INDEX IX_Reviews_Order ON Reviews(order_id);
CREATE INDEX IX_Reviews_Customer ON Reviews(customer_id);
CREATE INDEX IX_Reviews_Rating ON Reviews(rating);
CREATE INDEX IX_Reviews_IsPublic ON Reviews(is_public);
GO

-- =============================================
-- 13. BẢNG CONSULTATIONS (Yêu cầu tư vấn)
-- =============================================
IF OBJECT_ID('Consultations', 'U') IS NOT NULL
    DROP TABLE Consultations;
GO

CREATE TABLE Consultations (
    consultation_id INT PRIMARY KEY IDENTITY(1,1),
    full_name NVARCHAR(255) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    phone_number NVARCHAR(20),
    company_name NVARCHAR(255),
    address NVARCHAR(500),
    service_interest NVARCHAR(500), -- Dịch vụ quan tâm
    message NVARCHAR(1000) NOT NULL,
    status NVARCHAR(50) DEFAULT 'PENDING', -- PENDING, PROCESSING, COMPLETED
    handled_by INT, -- Admin xử lý
    response_message NVARCHAR(1000),
    handled_at DATETIME,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (handled_by) REFERENCES Users(user_id)
);
GO

CREATE INDEX IX_Consultations_Status ON Consultations(status);
CREATE INDEX IX_Consultations_CreatedAt ON Consultations(created_at);
GO

-- =============================================
-- 14. BẢNG ACTIVITY LOGS (Nhật ký hoạt động)
-- =============================================
IF OBJECT_ID('ActivityLogs', 'U') IS NOT NULL
    DROP TABLE ActivityLogs;
GO

CREATE TABLE ActivityLogs (
    log_id BIGINT PRIMARY KEY IDENTITY(1,1),
    user_id INT,
    action_type NVARCHAR(100) NOT NULL, -- CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    entity_type NVARCHAR(100), -- Order, User, Service, v.v.
    entity_id INT,
    description NVARCHAR(1000),
    ip_address NVARCHAR(50),
    user_agent NVARCHAR(500),
    created_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
GO

CREATE INDEX IX_ActivityLogs_User ON ActivityLogs(user_id);
CREATE INDEX IX_ActivityLogs_Entity ON ActivityLogs(entity_type, entity_id);
CREATE INDEX IX_ActivityLogs_CreatedAt ON ActivityLogs(created_at);
GO

-- =============================================
-- 15. BẢNG SYSTEM CONFIG (Cấu hình hệ thống)
-- =============================================
IF OBJECT_ID('SystemConfig', 'U') IS NOT NULL
    DROP TABLE SystemConfig;
GO

CREATE TABLE SystemConfig (
    config_id INT PRIMARY KEY IDENTITY(1,1),
    config_key NVARCHAR(100) NOT NULL UNIQUE,
    config_value NVARCHAR(MAX),
    config_type NVARCHAR(50), -- STRING, NUMBER, BOOLEAN, JSON
    description NVARCHAR(500),
    updated_by INT,
    updated_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (updated_by) REFERENCES Users(user_id)
);
GO

-- =============================================
-- 16. BẢNG CONTENT (Quản lý nội dung website)
-- =============================================
IF OBJECT_ID('Content', 'U') IS NOT NULL
    DROP TABLE Content;
GO

CREATE TABLE Content (
    content_id INT PRIMARY KEY IDENTITY(1,1),
    content_type NVARCHAR(50) NOT NULL, -- HOME, ABOUT, FAQ, NEWS, BANNER
    title NVARCHAR(255) NOT NULL,
    content_text NVARCHAR(MAX),
    image_url NVARCHAR(500),
    display_order INT DEFAULT 0,
    is_active BIT DEFAULT 1,
    created_by INT,
    created_at DATETIME DEFAULT GETDATE(),
    updated_by INT,
    updated_at DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (created_by) REFERENCES Users(user_id),
    FOREIGN KEY (updated_by) REFERENCES Users(user_id)
);
GO

CREATE INDEX IX_Content_Type ON Content(content_type);
GO

-- =============================================
-- INSERT DỮ LIỆU MẪU
-- =============================================

-- 1. INSERT ROLES
INSERT INTO Roles (role_name, role_description) VALUES
('CUSTOMER', N'Khách hàng - người sử dụng dịch vụ'),
('STAFF', N'Nhân viên - thực hiện dịch vụ'),
('ADMIN', N'Quản trị viên - quản lý hệ thống');
GO

-- 2. INSERT MEMBER LEVELS
INSERT INTO MemberLevels (level_code, level_name, discount_percentage, min_total_amount, min_service_count, min_continuous_months, description) VALUES
('SILVER', N'Thành viên Bạc', 0.00, 0, 1, 0, N'Khách hàng mới đăng ký, giảm giá 0%'),
('GOLD', N'Thành viên Vàng', 5.00, 5000000, 6, 3, N'Khách hàng trung thành, giảm giá 5%'),
('DIAMOND', N'Thành viên Kim cương', 10.00, 15000000, 15, 6, N'Khách hàng VIP, giảm giá 10%');
GO

-- 6. INSERT ORDER STATUS
INSERT INTO OrderStatus (status_code, status_name, status_description, display_order) VALUES
('PENDING', N'Chờ xử lý', N'Đơn hàng mới được tạo, chờ xác nhận', 1),
('CONFIRMED', N'Đã xác nhận', N'Đơn hàng đã được xác nhận và phân công nhân viên', 2),
('IN_PROGRESS', N'Đang thực hiện', N'Nhân viên đang thực hiện dịch vụ', 3),
('COMPLETED', N'Hoàn thành', N'Dịch vụ đã hoàn thành', 4),
('CANCELLED', N'Đã hủy', N'Đơn hàng đã bị hủy', 5);
GO

PRINT N'Database đã được tạo thành công với tất cả các bảng và dữ liệu mẫu!';
GO

