/**
 * Admin Dashboard Script - Complete Implementation
 */

let currentTab = 'dashboard';
let categories = [];
let staff = [];

document.addEventListener('DOMContentLoaded', function () {
    // Check authentication và role
    const token = localStorage.getItem('access_token');
    const role = getUserRole();

    console.log('Admin Dashboard - Auth check:', {
        hasToken: !!token,
        role: role,
        tokenLength: token ? token.length : 0
    });

    if (!isAuthenticated()) {
        console.warn('Not authenticated, redirecting to login');
        // alert('Lỗi: Chưa đăng nhập hoặc không tìm thấy token!');
        window.location.href = '../login.html';
        return;
    }

    if (role !== 'ADMIN') {
        console.warn('Not ADMIN role, current role:', role, '- redirecting to login');
        alert('Tài khoản không có quyền truy cập trang quản trị.');
        window.location.href = '../login.html';
        return;
    }

    // Nếu token không hợp lệ, xóa và redirect
    let tokenInvalid = false;

    // Welcome text - không block nếu lỗi, chỉ log
    API.getCurrentUser()
        .then((u) => {
            console.log('Current user loaded:', u);
            const el = document.getElementById('adminWelcome');
            if (el) el.textContent = `Xin chào, ${u.full_name}`;
        })
        .catch((error) => {
            console.error('Error getting current user:', error);
            // Nếu token không hợp lệ, xóa và redirect về login
            if (error.status === 401 || error.status === 422) {
                console.warn('Token invalid, clearing and redirecting to login');
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_role');
                // alert('Phiên đăng nhập hết hạn hoặc token không hợp lệ (Lỗi ' + error.status + '). Vui lòng đăng nhập lại.');
                window.location.href = '../login.html';
                return;
            }
        });

    // Handle hash navigation when returning from order detail
    const hash = window.location.hash;
    if (hash) {
        const tabName = hash.substring(1);
        if (['dashboard', 'orders', 'services', 'categories', 'users', 'staff', 'content'].includes(tabName)) {
            switchTab(tabName);
        } else {
            loadDashboardStats();
            loadCategories();
            loadStaff();
        }
    } else {
        // Load initial data
        loadDashboardStats();
        loadCategories();
        loadStaff();
    }

    // Event listeners
    const orderSearch = document.getElementById('orderSearch');
    if (orderSearch) {
        orderSearch.addEventListener('input', () => loadOrders());
    }

    const orderStatusFilter = document.getElementById('orderStatusFilter');
    if (orderStatusFilter) {
        orderStatusFilter.addEventListener('change', () => loadOrders());
    }
});

// ==================== TAB MANAGEMENT ====================
function switchTab(tabName) {
    currentTab = tabName;

    // Update active state
    document.querySelectorAll('.list-group-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('href') === `#${tabName}`) {
            item.classList.add('active');
        }
    });

    // Update tab pane visibility
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('show', 'active');
    });
    const targetPane = document.getElementById(tabName);
    if (targetPane) {
        targetPane.classList.add('show', 'active');
    }

    // Load data for the tab
    switch (tabName) {
        case 'dashboard':
            loadDashboardStats();
            break;
        case 'orders':
            loadOrders();
            break;
        case 'services':
            loadServices();
            break;
        case 'categories':
            loadCategories();
            break;
        case 'users':
            loadUsers();
            break;
        case 'staff':
            loadStaff();
            break;
        case 'content':
            loadContent();
            break;
    }
}

// ==================== DASHBOARD ====================
async function loadDashboardStats() {
    try {
        const stats = await API.getDashboardStats();
        console.log('Dashboard stats:', stats);

        if (document.getElementById('statTotalUsers')) {
            document.getElementById('statTotalUsers').textContent = stats.total_users || 0;
        }
        if (document.getElementById('statTotalOrders')) {
            document.getElementById('statTotalOrders').textContent = stats.total_orders || 0;
        }
        if (document.getElementById('statTotalRevenue')) {
            document.getElementById('statTotalRevenue').textContent = formatCurrency(stats.total_revenue || 0);
        }
        if (document.getElementById('statPendingOrders')) {
            document.getElementById('statPendingOrders').textContent = stats.pending_orders || 0;
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        const errorMsg = error.message || 'Không thể tải thống kê';
        showAlert(errorMsg, 'danger');
        // Set default values
        if (document.getElementById('statTotalUsers')) document.getElementById('statTotalUsers').textContent = '—';
        if (document.getElementById('statTotalOrders')) document.getElementById('statTotalOrders').textContent = '—';
        if (document.getElementById('statTotalRevenue')) document.getElementById('statTotalRevenue').textContent = '—';
        if (document.getElementById('statPendingOrders')) document.getElementById('statPendingOrders').textContent = '—';
    }
}

// ==================== ORDERS ====================
async function loadOrders() {
    try {
        const orders = await API.getOrders();
        console.log('Orders loaded:', orders);

        if (!Array.isArray(orders)) {
            throw new Error('Dữ liệu đơn hàng không hợp lệ');
        }

        const filtered = applyOrderFilters(orders);
        displayOrders(filtered);
    } catch (error) {
        console.error('Error loading orders:', error);
        const container = document.getElementById('ordersTable');
        if (container) {
            container.innerHTML =
                `<div class="alert alert-danger">Không thể tải danh sách đơn hàng: ${error.message || 'Lỗi không xác định'}</div>`;
        }
    }
}

function applyOrderFilters(orders) {
    if (!Array.isArray(orders)) {
        return [];
    }

    const statusFilter = document.getElementById('orderStatusFilter')?.value || '';
    const keyword = (document.getElementById('orderSearch')?.value || '').toLowerCase().trim();

    return orders.filter(o => {
        if (!o) return false;

        const statusCode = o?.status?.status_code || '';
        const matchStatus = statusFilter ? statusCode === statusFilter : true;

        const orderCode = (o?.order_code || '').toLowerCase();
        const customerName = (o?.customer?.full_name || '').toLowerCase();
        const serviceName = (o?.service?.service_name || '').toLowerCase();

        const matchKeyword = keyword
            ? (orderCode.includes(keyword) ||
                customerName.includes(keyword) ||
                serviceName.includes(keyword))
            : true;
        return matchStatus && matchKeyword;
    });
}

function displayOrders(orders) {
    const container = document.getElementById('ordersTable');
    if (!container) {
        console.error('ordersTable container not found');
        return;
    }

    if (!Array.isArray(orders) || orders.length === 0) {
        container.innerHTML = '<p class="text-muted">Chưa có đơn hàng nào.</p>';
        return;
    }

    const table = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Mã đơn</th>
                        <th>Khách hàng</th>
                        <th>Dịch vụ</th>
                        <th>Ngày đặt</th>
                        <th>Tổng tiền</th>
                        <th>Trạng thái</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    ${orders.map(order => {
        const status = order.status || {};
        const statusCode = status.status_code || 'UNKNOWN';
        const statusName = status.status_name || 'N/A';
        return `
                        <tr>
                            <td><code>${escapeHtml(order.order_code || 'N/A')}</code></td>
                            <td>${escapeHtml(order.customer ? order.customer.full_name : 'N/A')}</td>
                            <td>${escapeHtml(order.service ? order.service.service_name : 'N/A')}</td>
                            <td>${formatDate(order.order_date)}</td>
                            <td>${formatCurrency(order.total_amount || 0)}</td>
                            <td>
                                <span class="badge bg-${getStatusBadgeColor(statusCode)}">
                                    ${escapeHtml(statusName)}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-primary" onclick="viewOrder(${order.order_id})">
                                        👁️ Xem
                                    </button>
                                    ${getOrderActionButtons(order)}
                                </div>
                            </td>
                        </tr>
                    `;
    }).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = table;
}

function getOrderActionButtons(order) {
    const status = order.status.status_code;
    let buttons = '';

    if (status === 'PENDING') {
        buttons += `<button class="btn btn-success" onclick="updateOrderStatus(${order.order_id}, 'CONFIRMED')">✓ Xác nhận</button>`;
        buttons += `<button class="btn btn-info" onclick="showAssignStaffModal(${order.order_id})">👨‍💼 Phân công</button>`;
    } else if (status === 'CONFIRMED') {
        buttons += `<button class="btn btn-primary" onclick="updateOrderStatus(${order.order_id}, 'IN_PROGRESS')">▶ Bắt đầu</button>`;
    } else if (status === 'IN_PROGRESS') {
        buttons += `<button class="btn btn-success" onclick="updateOrderStatus(${order.order_id}, 'COMPLETED')">✓ Hoàn thành</button>`;
    }

    if (status !== 'COMPLETED' && status !== 'CANCELLED') {
        buttons += `<button class="btn btn-danger" onclick="updateOrderStatus(${order.order_id}, 'CANCELLED')">✕ Hủy</button>`;
    }

    return buttons;
}

async function updateOrderStatus(orderId, statusCode) {
    if (!confirm('Bạn có chắc muốn cập nhật trạng thái?')) {
        return;
    }

    try {
        await API.updateOrderStatus(orderId, statusCode);
        showAlert('Cập nhật trạng thái thành công!', 'success');
        loadOrders();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

function viewOrder(orderId) {
    window.location.href = `order-detail.html?id=${orderId}`;
}

// ==================== SERVICES ====================
async function loadServices() {
    try {
        const services = await API.adminGetServices();
        console.log('Services loaded:', services);

        if (!Array.isArray(services)) {
            throw new Error('Dữ liệu dịch vụ không hợp lệ');
        }

        displayServices(services);
    } catch (error) {
        console.error('Error loading services:', error);
        const container = document.getElementById('servicesTable');
        if (container) {
            container.innerHTML =
                `<div class="alert alert-danger">Không thể tải danh sách dịch vụ: ${error.message || 'Lỗi không xác định'}</div>`;
        }
    }
}

function displayServices(services) {
    const container = document.getElementById('servicesTable');
    if (!container) {
        console.error('servicesTable container not found');
        return;
    }

    if (!Array.isArray(services) || services.length === 0) {
        container.innerHTML = '<p class="text-muted">Chưa có dịch vụ nào.</p>';
        return;
    }

    const table = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Tên dịch vụ</th>
                        <th>Danh mục</th>
                        <th>Giá</th>
                        <th>Thời lượng</th>
                        <th>Trạng thái</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    ${services.map(service => {
        const categoryName = service.category ? service.category.category_name : 'N/A';
        const isActive = service.is_active !== false;
        return `
                        <tr>
                            <td><strong>${escapeHtml(service.service_name || 'N/A')}</strong></td>
                            <td>${escapeHtml(categoryName)}</td>
                            <td>${formatCurrency(service.base_price || 0)}</td>
                            <td>${service.duration_hours ? service.duration_hours + 'h' : 'N/A'}</td>
                            <td>
                                <span class="badge bg-${isActive ? 'success' : 'secondary'}">
                                    ${isActive ? 'Hoạt động' : 'Tạm khóa'}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-primary" onclick="editService(${service.service_id})">
                                        ✏️ Sửa
                                    </button>
                                    <button class="btn btn-danger" onclick="deleteService(${service.service_id})">
                                        🗑️ Xóa
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
    }).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = table;
}

function showServiceModal(serviceId = null) {
    const modal = new bootstrap.Modal(document.getElementById('serviceModal'));
    const title = document.getElementById('serviceModalTitle');
    const form = document.getElementById('serviceForm');

    form.reset();
    document.getElementById('serviceId').value = serviceId || '';

    if (serviceId) {
        title.textContent = 'Sửa dịch vụ';
        loadServiceData(serviceId);
    } else {
        title.textContent = 'Thêm dịch vụ';
        loadCategoriesForSelect('serviceCategory');
    }

    modal.show();
}

async function loadServiceData(serviceId) {
    try {
        const service = await API.adminGetService(serviceId);

        document.getElementById('serviceId').value = service.service_id;
        document.getElementById('serviceName').value = service.service_name;
        document.getElementById('serviceDescription').value = service.service_description || '';
        document.getElementById('servicePrice').value = service.base_price;
        document.getElementById('serviceDuration').value = service.duration_hours || '';
        document.getElementById('serviceUnit').value = service.unit || '';
        document.getElementById('serviceDisplayOrder').value = service.display_order || 0;
        document.getElementById('serviceIsActive').checked = service.is_active;

        await loadCategoriesForSelect('serviceCategory');
        document.getElementById('serviceCategory').value = service.category_id;
    } catch (error) {
        showAlert('Không thể tải dữ liệu dịch vụ', 'danger');
    }
}

async function loadCategoriesForSelect(selectId) {
    try {
        if (categories.length === 0) {
            categories = await API.adminGetCategories();
        }

        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Chọn danh mục...</option>' +
            categories.map(cat =>
                `<option value="${cat.category_id}">${cat.category_name}</option>`
            ).join('');
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function saveService() {
    const form = document.getElementById('serviceForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const serviceId = document.getElementById('serviceId').value;
    const data = {
        service_name: document.getElementById('serviceName').value,
        service_description: document.getElementById('serviceDescription').value,
        category_id: parseInt(document.getElementById('serviceCategory').value),
        base_price: parseFloat(document.getElementById('servicePrice').value),
        duration_hours: document.getElementById('serviceDuration').value ? parseFloat(document.getElementById('serviceDuration').value) : null,
        unit: document.getElementById('serviceUnit').value,
        display_order: parseInt(document.getElementById('serviceDisplayOrder').value) || 0,
        is_active: document.getElementById('serviceIsActive').checked
    };

    try {
        if (serviceId) {
            await API.adminUpdateService(serviceId, data);
            showAlert('Cập nhật dịch vụ thành công!', 'success');
        } else {
            await API.adminCreateService(data);
            showAlert('Thêm dịch vụ thành công!', 'success');
        }

        bootstrap.Modal.getInstance(document.getElementById('serviceModal')).hide();
        loadServices();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

function editService(serviceId) {
    showServiceModal(serviceId);
}

async function deleteService(serviceId) {
    if (!confirm('Bạn có chắc muốn xóa dịch vụ này?')) {
        return;
    }

    try {
        await API.adminDeleteService(serviceId);
        showAlert('Xóa dịch vụ thành công!', 'success');
        loadServices();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

// ==================== CATEGORIES ====================
async function loadCategories() {
    try {
        categories = await API.adminGetCategories();
        console.log('Categories loaded:', categories);

        if (!Array.isArray(categories)) {
            throw new Error('Dữ liệu danh mục không hợp lệ');
        }

        displayCategories(categories);
    } catch (error) {
        console.error('Error loading categories:', error);
        const container = document.getElementById('categoriesTable');
        if (container) {
            container.innerHTML =
                `<div class="alert alert-danger">Không thể tải danh sách danh mục: ${error.message || 'Lỗi không xác định'}</div>`;
        }
    }
}

function displayCategories(categories) {
    const container = document.getElementById('categoriesTable');
    if (!container) {
        console.error('categoriesTable container not found');
        return;
    }

    if (!Array.isArray(categories) || categories.length === 0) {
        container.innerHTML = '<p class="text-muted">Chưa có danh mục nào.</p>';
        return;
    }

    const table = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Tên danh mục</th>
                        <th>Mô tả</th>
                        <th>Thứ tự</th>
                        <th>Trạng thái</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    ${categories.map(cat => {
        const isActive = cat.is_active !== false;
        return `
                        <tr>
                            <td><strong>${escapeHtml(cat.category_name || 'N/A')}</strong></td>
                            <td>${escapeHtml(cat.category_description || '—')}</td>
                            <td>${cat.display_order || 0}</td>
                            <td>
                                <span class="badge bg-${isActive ? 'success' : 'secondary'}">
                                    ${isActive ? 'Hoạt động' : 'Tạm khóa'}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-primary" onclick="editCategory(${cat.category_id})">
                                        ✏️ Sửa
                                    </button>
                                    <button class="btn btn-danger" onclick="deleteCategory(${cat.category_id})">
                                        🗑️ Xóa
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
    }).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = table;
}

function showCategoryModal(categoryId = null) {
    const modal = new bootstrap.Modal(document.getElementById('categoryModal'));
    const title = document.getElementById('categoryModalTitle');
    const form = document.getElementById('categoryForm');

    form.reset();
    document.getElementById('categoryId').value = categoryId || '';

    if (categoryId) {
        title.textContent = 'Sửa danh mục';
        loadCategoryData(categoryId);
    } else {
        title.textContent = 'Thêm danh mục';
    }

    modal.show();
}

async function loadCategoryData(categoryId) {
    try {
        const categories = await API.adminGetCategories();
        const category = categories.find(c => c.category_id === categoryId);

        if (category) {
            document.getElementById('categoryId').value = category.category_id;
            document.getElementById('categoryName').value = category.category_name;
            document.getElementById('categoryDescription').value = category.category_description || '';
            document.getElementById('categoryDisplayOrder').value = category.display_order || 0;
            document.getElementById('categoryIsActive').checked = category.is_active;
        }
    } catch (error) {
        showAlert('Không thể tải dữ liệu danh mục', 'danger');
    }
}

async function saveCategory() {
    const form = document.getElementById('categoryForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const categoryId = document.getElementById('categoryId').value;
    const data = {
        category_name: document.getElementById('categoryName').value,
        category_description: document.getElementById('categoryDescription').value,
        display_order: parseInt(document.getElementById('categoryDisplayOrder').value) || 0,
        is_active: document.getElementById('categoryIsActive').checked
    };

    try {
        if (categoryId) {
            await API.adminUpdateCategory(categoryId, data);
            showAlert('Cập nhật danh mục thành công!', 'success');
        } else {
            await API.adminCreateCategory(data);
            showAlert('Thêm danh mục thành công!', 'success');
        }

        bootstrap.Modal.getInstance(document.getElementById('categoryModal')).hide();
        loadCategories();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

function editCategory(categoryId) {
    showCategoryModal(categoryId);
}

async function deleteCategory(categoryId) {
    if (!confirm('Bạn có chắc muốn xóa danh mục này? Lưu ý: Không thể xóa nếu có dịch vụ đang sử dụng.')) {
        return;
    }

    try {
        await API.adminDeleteCategory(categoryId);
        showAlert('Xóa danh mục thành công!', 'success');
        loadCategories();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

// ==================== USERS ====================
async function loadUsers() {
    try {
        const roleFilter = document.getElementById('userRoleFilter')?.value || '';
        const users = await API.adminGetUsers(roleFilter || null);
        console.log('Users loaded:', users);

        if (!Array.isArray(users)) {
            throw new Error('Dữ liệu người dùng không hợp lệ');
        }

        displayUsers(users);
    } catch (error) {
        console.error('Error loading users:', error);
        const container = document.getElementById('usersTable');
        if (container) {
            container.innerHTML =
                `<div class="alert alert-danger">Không thể tải danh sách người dùng: ${error.message || 'Lỗi không xác định'}</div>`;
        }
    }
}

function displayUsers(users) {
    const container = document.getElementById('usersTable');
    if (!container) {
        console.error('usersTable container not found');
        return;
    }

    if (!Array.isArray(users) || users.length === 0) {
        container.innerHTML = '<p class="text-muted">Chưa có người dùng nào.</p>';
        return;
    }

    const table = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Họ tên</th>
                        <th>Email</th>
                        <th>Username</th>
                        <th>Vai trò</th>
                        <th>Member Level</th>
                        <th>Trạng thái</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => {
        const isActive = user.is_active !== false;
        const isLocked = user.is_locked === true;
        const memberLevel = user.member_level ? user.member_level.level_name : '—';
        return `
                        <tr>
                            <td><strong>${escapeHtml(user.full_name || 'N/A')}</strong></td>
                            <td>${escapeHtml(user.email || 'N/A')}</td>
                            <td>${escapeHtml(user.username || 'N/A')}</td>
                            <td><span class="badge bg-info">${escapeHtml(user.role_name || 'N/A')}</span></td>
                            <td>${escapeHtml(memberLevel)}</td>
                            <td>
                                <span class="badge bg-${isActive && !isLocked ? 'success' : 'danger'}">
                                    ${isActive && !isLocked ? 'Hoạt động' : 'Khóa'}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-primary" onclick="viewUser(${user.user_id})">
                                        👁️ Xem
                                    </button>
                                    <button class="btn btn-${isLocked ? 'success' : 'warning'}" 
                                            onclick="toggleUserLock(${user.user_id}, ${!isLocked})">
                                        ${isLocked ? '🔓 Mở khóa' : '🔒 Khóa'}
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
    }).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = table;
}

function viewUser(userId) {
    // TODO: Implement user detail view
    alert('Xem chi tiết user ID: ' + userId);
}

async function toggleUserLock(userId, lock) {
    const action = lock ? 'khóa' : 'mở khóa';
    if (!confirm(`Bạn có chắc muốn ${action} tài khoản này?`)) {
        return;
    }

    try {
        await API.adminUpdateUserStatus(userId, { is_locked: lock });
        showAlert(`${action.charAt(0).toUpperCase() + action.slice(1)} tài khoản thành công!`, 'success');
        loadUsers();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

// ==================== STAFF ====================
async function loadStaff() {
    try {
        staff = await API.adminGetStaff();
        console.log('Staff loaded:', staff);

        if (!Array.isArray(staff)) {
            throw new Error('Dữ liệu nhân viên không hợp lệ');
        }

        displayStaff(staff);
    } catch (error) {
        console.error('Error loading staff:', error);
        const container = document.getElementById('staffTable');
        if (container) {
            container.innerHTML =
                `<div class="alert alert-danger">Không thể tải danh sách nhân viên: ${error.message || 'Lỗi không xác định'}</div>`;
        }
    }
}

function displayStaff(staff) {
    const container = document.getElementById('staffTable');
    if (!container) {
        console.error('staffTable container not found');
        return;
    }

    if (!Array.isArray(staff) || staff.length === 0) {
        container.innerHTML = '<p class="text-muted">Chưa có nhân viên nào.</p>';
        return;
    }

    const table = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Họ tên</th>
                        <th>Email</th>
                        <th>Username</th>
                        <th>Số điện thoại</th>
                        <th>Trạng thái</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    ${staff.map(s => {
        const isActive = s.is_active !== false;
        const isLocked = s.is_locked === true;
        return `
                        <tr>
                            <td><strong>${escapeHtml(s.full_name || 'N/A')}</strong></td>
                            <td>${escapeHtml(s.email || 'N/A')}</td>
                            <td>${escapeHtml(s.username || 'N/A')}</td>
                            <td>${escapeHtml(s.phone_number || '—')}</td>
                            <td>
                                <span class="badge bg-${isActive && !isLocked ? 'success' : 'danger'}">
                                    ${isActive && !isLocked ? 'Hoạt động' : 'Khóa'}
                                </span>
                            </td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="viewUser(${s.user_id})">
                                    👁️ Xem
                                </button>
                            </td>
                        </tr>
                    `;
    }).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = table;
}

// ==================== CONTENT ====================
async function loadContent() {
    try {
        const contentType = document.getElementById('contentTypeFilter')?.value || '';
        const contents = await API.adminGetContent(contentType || null);
        console.log('Content loaded:', contents);

        if (!Array.isArray(contents)) {
            throw new Error('Dữ liệu nội dung không hợp lệ');
        }

        displayContent(contents);
    } catch (error) {
        console.error('Error loading content:', error);
        const container = document.getElementById('contentTable');
        if (container) {
            container.innerHTML =
                `<div class="alert alert-danger">Không thể tải danh sách nội dung: ${error.message || 'Lỗi không xác định'}</div>`;
        }
    }
}

function displayContent(contents) {
    const container = document.getElementById('contentTable');
    if (!container) {
        console.error('contentTable container not found');
        return;
    }

    if (!Array.isArray(contents) || contents.length === 0) {
        container.innerHTML = '<p class="text-muted">Chưa có nội dung nào.</p>';
        return;
    }

    const table = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Loại</th>
                        <th>Tiêu đề</th>
                        <th>Thứ tự</th>
                        <th>Trạng thái</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    ${contents.map(content => {
        const isActive = content.is_active !== false;
        return `
                        <tr>
                            <td><span class="badge bg-secondary">${escapeHtml(content.content_type || 'N/A')}</span></td>
                            <td><strong>${escapeHtml(content.title || 'N/A')}</strong></td>
                            <td>${content.display_order || 0}</td>
                            <td>
                                <span class="badge bg-${isActive ? 'success' : 'secondary'}">
                                    ${isActive ? 'Hoạt động' : 'Tạm khóa'}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-primary" onclick="editContent(${content.content_id})">
                                        ✏️ Sửa
                                    </button>
                                    <button class="btn btn-danger" onclick="deleteContent(${content.content_id})">
                                        🗑️ Xóa
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
    }).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = table;
}

function showContentModal(contentId = null) {
    const modal = new bootstrap.Modal(document.getElementById('contentModal'));
    const title = document.getElementById('contentModalTitle');
    const form = document.getElementById('contentForm');

    form.reset();
    document.getElementById('contentId').value = contentId || '';

    if (contentId) {
        title.textContent = 'Sửa nội dung';
        loadContentData(contentId);
    } else {
        title.textContent = 'Thêm nội dung';
    }

    modal.show();
}

async function loadContentData(contentId) {
    try {
        const contents = await API.adminGetContent();
        const content = contents.find(c => c.content_id === contentId);

        if (content) {
            document.getElementById('contentId').value = content.content_id;
            document.getElementById('contentType').value = content.content_type;
            document.getElementById('contentTitle').value = content.title;
            document.getElementById('contentText').value = content.content_text || '';
            document.getElementById('contentImageUrl').value = content.image_url || '';
            document.getElementById('contentDisplayOrder').value = content.display_order || 0;
            document.getElementById('contentIsActive').checked = content.is_active;
        }
    } catch (error) {
        showAlert('Không thể tải dữ liệu nội dung', 'danger');
    }
}

async function saveContent() {
    const form = document.getElementById('contentForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const contentId = document.getElementById('contentId').value;
    const data = {
        content_type: document.getElementById('contentType').value,
        title: document.getElementById('contentTitle').value,
        content_text: document.getElementById('contentText').value,
        image_url: document.getElementById('contentImageUrl').value,
        display_order: parseInt(document.getElementById('contentDisplayOrder').value) || 0,
        is_active: document.getElementById('contentIsActive').checked
    };

    try {
        if (contentId) {
            await API.adminUpdateContent(contentId, data);
            showAlert('Cập nhật nội dung thành công!', 'success');
        } else {
            await API.adminCreateContent(data);
            showAlert('Thêm nội dung thành công!', 'success');
        }

        bootstrap.Modal.getInstance(document.getElementById('contentModal')).hide();
        loadContent();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

function editContent(contentId) {
    showContentModal(contentId);
}

async function deleteContent(contentId) {
    if (!confirm('Bạn có chắc muốn xóa nội dung này?')) {
        return;
    }

    try {
        await API.adminDeleteContent(contentId);
        showAlert('Xóa nội dung thành công!', 'success');
        loadContent();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

// ==================== ASSIGN STAFF ====================
async function showAssignStaffModal(orderId) {
    const modal = new bootstrap.Modal(document.getElementById('assignStaffModal'));
    document.getElementById('assignOrderId').value = orderId;

    // Load staff list
    if (staff.length === 0) {
        staff = await API.adminGetStaff();
    }

    const select = document.getElementById('assignStaffId');
    select.innerHTML = '<option value="">Chọn nhân viên...</option>' +
        staff.filter(s => s.is_active && !s.is_locked).map(s =>
            `<option value="${s.user_id}">${s.full_name} (${s.email})</option>`
        ).join('');

    modal.show();
}

async function saveAssignStaff() {
    const form = document.getElementById('assignStaffForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const orderId = document.getElementById('assignOrderId').value;
    const data = {
        staff_id: parseInt(document.getElementById('assignStaffId').value),
        notes: document.getElementById('assignNotes').value
    };

    try {
        await API.adminAssignOrder(orderId, data);
        showAlert('Phân công nhân viên thành công!', 'success');
        bootstrap.Modal.getInstance(document.getElementById('assignStaffModal')).hide();
        loadOrders();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

// ==================== UTILITY FUNCTIONS ====================
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getStatusBadgeColor(statusCode) {
    const colors = {
        'PENDING': 'warning',
        'CONFIRMED': 'info',
        'IN_PROGRESS': 'primary',
        'COMPLETED': 'success',
        'CANCELLED': 'danger'
    };
    return colors[statusCode] || 'secondary';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'N/A';
        return date.toLocaleDateString('vi-VN');
    } catch (e) {
        return 'N/A';
    }
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) {
        return '0 ₫';
    }
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // Auto remove after 3 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}
