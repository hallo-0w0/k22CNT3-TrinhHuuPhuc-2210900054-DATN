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

    switch (role) {
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
    const guestNav = document.getElementById('guestNav');
    const memberNavItems = document.querySelectorAll('.member-nav');
    const logoutLink = document.getElementById('logoutLink');

    // Luôn bind nút logout nếu có
    if (logoutLink && !logoutLink.__pclearLogoutBound) {
        logoutLink.__pclearLogoutBound = true;
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    if (isAuthenticated()) {
        if (guestNav) guestNav.classList.add('d-none');
        memberNavItems.forEach(item => item.classList.remove('d-none'));

        // Load user info để check token valid và cập nhật UI Header
        API.getCurrentUser()
            .then(user => {
                updateHeaderUser(user);
                updateMemberModal(user);
            })
            .catch((error) => {
                console.warn('Check token failed:', error);
                if (error.status === 401) {
                    logout();
                }
            });

    } else {
        if (guestNav) guestNav.classList.remove('d-none');
        memberNavItems.forEach(item => item.classList.add('d-none'));
    }
}

function updateHeaderUser(user) {
    const userNameEl = document.getElementById('headerUserName');
    const badgeEl = document.getElementById('headerMemberBadge');

    if (userNameEl) userNameEl.textContent = `Xin chào, ${user.full_name.split(' ').pop()}`;

    if (badgeEl && user.member_level) {
        badgeEl.textContent = user.member_level.level_name;
        badgeEl.className = `badge ms-1 bg-${getMemberLevelColor(user.member_level.level_code)}`;
    }
}

function updateMemberModal(user) {
    if (!user.member_level) return;

    const badgeEl = document.getElementById('modalMemberBadge');
    if (badgeEl) {
        badgeEl.textContent = user.member_level.level_name;
        badgeEl.className = `badge rounded-pill fs-5 mb-2 px-4 py-2 bg-${getMemberLevelColor(user.member_level.level_code)}`;
    }

    if (document.getElementById('modalMemberName'))
        document.getElementById('modalMemberName').textContent = user.full_name;

    if (document.getElementById('modalMemberEmail'))
        document.getElementById('modalMemberEmail').textContent = user.email;

    if (document.getElementById('modalDiscountPercent'))
        document.getElementById('modalDiscountPercent').textContent = `${user.member_level.discount_percentage}%`;
}

function getMemberLevelColor(levelCode) {
    switch (levelCode) {
        case 'GOLD': return 'warning text-dark';
        case 'DIAMOND': return 'info text-white';
        default: return 'secondary';
    }
}
// Auto init khi page load (mọi trang)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateNavigation);
} else {
    updateNavigation();
}
