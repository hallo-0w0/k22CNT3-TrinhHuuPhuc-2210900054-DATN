/**
 * Customer Orders Page Script
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication và role
    if (!isAuthenticated() || getUserRole() !== 'CUSTOMER') {
        window.location.href = '../login.html';
        return;
    }
    
    // Load orders
    loadOrders();

    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', () => loadOrders());
    }
});

async function loadOrders() {
    try {
        const orders = await API.getOrders();
        updateStats(orders);

        const statusCode = document.getElementById('statusFilter')?.value || '';
        const filtered = statusCode ? orders.filter(o => o?.status?.status_code === statusCode) : orders;

        displayOrders(filtered);
    } catch (error) {
        console.error('Error loading orders:', error);
        document.getElementById('ordersList').innerHTML = 
            '<div class="alert alert-danger">Không thể tải danh sách đơn hàng</div>';
    }
}

function updateStats(orders) {
    const total = orders.length;
    const inProgress = orders.filter(o => o?.status?.status_code === 'IN_PROGRESS').length;
    const completed = orders.filter(o => o?.status?.status_code === 'COMPLETED').length;

    const elTotal = document.getElementById('statTotal');
    const elInProgress = document.getElementById('statInProgress');
    const elCompleted = document.getElementById('statCompleted');

    if (elTotal) elTotal.textContent = total;
    if (elInProgress) elInProgress.textContent = inProgress;
    if (elCompleted) elCompleted.textContent = completed;
}

function displayOrders(orders) {
    const container = document.getElementById('ordersList');
    
    if (orders.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <div class="mb-2 fw-semibold">Chưa có đơn hàng nào</div>
                <div class="text-muted small">Bạn có thể quay lại trang dịch vụ để tạo đơn mới.</div>
                <a class="btn btn-primary btn-sm mt-3" href="../index.html">Về trang chủ</a>
            </div>
        `;
        return;
    }
    
    const html = orders.map(order => `
        <div class="card mb-3">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h5 class="card-title">${order.service ? order.service.service_name : 'N/A'}</h5>
                        <p class="card-text">
                            <strong>Mã đơn:</strong> ${order.order_code}<br>
                            <strong>Ngày đặt:</strong> ${formatDate(order.order_date)}<br>
                            <strong>Địa chỉ:</strong> ${order.service_address}
                        </p>
                    </div>
                    <div class="col-md-4 text-end">
                        <p class="card-text">
                            <span class="badge bg-${getStatusBadgeColor(order.status.status_code)}">
                                ${order.status.status_name}
                            </span>
                        </p>
                        <p class="card-text">
                            <strong class="text-primary">${formatCurrency(order.total_amount)}</strong>
                        </p>
                        <button class="btn btn-sm btn-primary" onclick="viewOrder(${order.order_id})">
                            Xem chi tiết
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
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
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

function viewOrder(orderId) {
    window.location.href = `order-detail.html?id=${orderId}`;
}
