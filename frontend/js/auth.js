/**
 * Authentication Helper Functions
 */

/**
 * Kiểm tra user đã đăng nhập chưa
 */
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

/**
 * Lấy role của user hiện tại
 */
function getUserRole() {
    return localStorage.getItem('user_role');
}

/**
 * Redirect theo role sau khi đăng nhập
 */
function redirectByRole(role) {
    localStorage.setItem('user_role', role);
    
    // Tính toán đường dẫn từ vị trí hiện tại
    const currentPath = window.location.pathname;
    let basePath = '';
    
    // Nếu đang ở trong thư mục con (admin, customer, staff), về root
    if (currentPath.includes('/admin/') || currentPath.includes('/customer/') || currentPath.includes('/staff/')) {
        basePath = '../';
    }
    // Nếu đang ở login.html hoặc index.html trong frontend root, không cần basePath
    
    console.log('Redirecting by role:', { role, currentPath, basePath });
    
    switch(role) {
        case 'ADMIN':
            const adminPath = basePath + 'admin/dashboard.html';
            console.log('Redirecting to:', adminPath);
            window.location.href = adminPath;
            break;
        case 'STAFF':
            const staffPath = basePath + 'staff/orders.html';
            console.log('Redirecting to:', staffPath);
            window.location.href = staffPath;
            break;
        case 'CUSTOMER':
            const customerPath = basePath + 'customer/orders.html';
            console.log('Redirecting to:', customerPath);
            window.location.href = customerPath;
            break;
        default:
            const defaultPath = basePath + 'index.html';
            console.log('Redirecting to default:', defaultPath);
            window.location.href = defaultPath;
    }
}

/**
 * Đăng xuất
 */
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    
    // Tính toán đường dẫn về login.html từ vị trí hiện tại
    // Nếu đang ở admin/, customer/, staff/ thì cần về root
    const currentPath = window.location.pathname;
    let loginPath = 'index.html#auth';
    
    // Nếu đang ở trong thư mục con (admin, customer, staff)
    if (currentPath.includes('/admin/') || currentPath.includes('/customer/') || currentPath.includes('/staff/')) {
        loginPath = '../index.html#auth';
    }
    
    window.location.href = loginPath;
}

/**
 * Kiểm tra và cập nhật UI navigation
 */
function updateNavigation() {
    const loginLink = document.getElementById('loginLink');
    const userMenu = document.getElementById('userMenu');
    const userName = document.getElementById('userName');
    const logoutLink = document.getElementById('logoutLink');
    
    // Luôn bind nút logout nếu có (admin/customer/staff đều có thể có logoutLink)
    if (logoutLink && !logoutLink.__pclearLogoutBound) {
        logoutLink.__pclearLogoutBound = true;
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    // Chỉ update UI nav kiểu home (loginLink/userMenu) nếu có các element này
    if (!loginLink && !userMenu) return;
    
    if (isAuthenticated()) {
        if (loginLink) loginLink.classList.add('d-none');
        if (userMenu) userMenu.classList.remove('d-none');
        
        // Load user info (không logout nếu fail, chỉ log error)
        API.getCurrentUser()
            .then(user => {
                if (userName) userName.textContent = user.full_name;
            })
            .catch((error) => {
                // Chỉ log error, không logout tự động
                // Vì có thể là lỗi network tạm thời hoặc backend chưa chạy
                console.warn('Không thể load user info:', error);
                // Chỉ logout nếu là lỗi 401 (Unauthorized) - token không hợp lệ
                if (error.status === 401) {
                    console.log('Token không hợp lệ, đăng xuất...');
                    logout();
                } else {
                    console.log('Lỗi network hoặc backend chưa chạy. Kiểm tra backend tại http://localhost:5000');
                }
            });
        
    } else {
        if (loginLink) loginLink.classList.remove('d-none');
        if (userMenu) userMenu.classList.add('d-none');
    }
}

// Auto init khi page load (mọi trang)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateNavigation);
} else {
    updateNavigation();
}
