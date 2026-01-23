/**
 * Customer Orders Page Script
 */

document.addEventListener('DOMContentLoaded', function () {
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

    const html = orders.map(order => {
        const statusMap = {
            'PENDING': 1,
            'CONFIRMED': 2,
            'IN_PROGRESS': 3,
            'COMPLETED': 4
        };
        const currentStep = statusMap[order.status.status_code] || 0;
        const isCancelled = order.status.status_code === 'CANCELLED';

        // Timeline HTML
        let timelineHtml = '';
        if (!isCancelled) {
            timelineHtml = `
            <div class="position-relative m-3">
                <div class="progress" style="height: 2px;">
                    <div class="progress-bar bg-success" role="progressbar" style="width: ${(currentStep - 1) * 33}%" ></div>
                </div>
                <div class="position-absolute top-0 start-0 translate-middle btn btn-sm btn-${currentStep >= 1 ? 'success' : 'secondary'} rounded-pill" style="width: 2rem; height:2rem; padding: 0.25rem 0;">1</div>
                <div class="position-absolute top-0 start-50 translate-middle btn btn-sm btn-${currentStep >= 2 ? 'success' : 'secondary'} rounded-pill" style="width: 2rem; height:2rem; padding: 0.25rem 0; left: 33% !important">2</div>
                <div class="position-absolute top-0 start-50 translate-middle btn btn-sm btn-${currentStep >= 3 ? 'success' : 'secondary'} rounded-pill" style="width: 2rem; height:2rem; padding: 0.25rem 0; left: 66% !important">3</div>
                <div class="position-absolute top-0 start-100 translate-middle btn btn-sm btn-${currentStep >= 4 ? 'success' : 'secondary'} rounded-pill" style="width: 2rem; height:2rem; padding: 0.25rem 0;">4</div>
                
                <div class="position-relative mt-4 text-center" style="height: 20px; font-size: 0.75rem">
                    <span class="position-absolute top-0 start-0 translate-middle-x ${currentStep >= 1 ? 'text-success fw-bold' : 'text-muted'}" style="width: max-content">Chờ xác nhận</span>
                    <span class="position-absolute top-0 translate-middle-x ${currentStep >= 2 ? 'text-success fw-bold' : 'text-muted'}" style="left: 33%; width: max-content">Đã xác nhận</span>
                    <span class="position-absolute top-0 translate-middle-x ${currentStep >= 3 ? 'text-success fw-bold' : 'text-muted'}" style="left: 66%; width: max-content">Đang làm</span>
                    <span class="position-absolute top-0 start-100 translate-middle-x ${currentStep >= 4 ? 'text-success fw-bold' : 'text-muted'}" style="width: max-content">Hoàn thành</span>
                </div>
            </div>
            `;
        } else {
            timelineHtml = `
             <div class="alert alert-danger mb-0 d-flex align-items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">
                  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/>
                </svg>
                Đơn hàng đã bị hủy
             </div>
             `;
        }

        return `
        <div class="card mb-4 border-0 shadow-sm rounded-3 overflow-hidden">
            <div class="card-header bg-white py-3 border-bottom d-flex align-items-center justify-content-between">
                <div>
                    <span class="text-muted small">Mã đơn:</span>
                    <span class="fw-bold">#${order.order_code}</span>
                </div>
                <span class="badge bg-${getStatusBadgeColor(order.status.status_code)} bg-opacity-10 text-${getStatusBadgeColor(order.status.status_code)} px-3 py-2 rounded-pill">
                    ${order.status.status_name}
                </span>
            </div>
            <div class="card-body">
                <div class="row align-items-center mb-4">
                    <div class="col-md-7">
                        <h5 class="fw-bold text-primary mb-1">${order.service ? order.service.service_name : 'Dịch vụ'}</h5>
                        <div class="text-muted small mb-2"><i class="bi bi-geo-alt-fill"></i> Địa chỉ thực hiện: ${order.service_address}</div>
                        <div class="text-muted small"><i class="bi bi-calendar-event"></i> Ngày đặt: ${formatDate(order.order_date)}</div>
                    </div>
                    <div class="col-md-5 text-md-end mt-3 mt-md-0">
                        <div class="small text-muted">Tổng tiền</div>
                        <div class="fs-4 fw-bold text-success">${formatCurrency(order.total_amount)}</div>
                    </div>
                </div>

                <!-- Timeline -->
                <div class="mb-4 px-2">
                    ${timelineHtml}
                </div>

                <div class="d-flex justify-content-end gap-2 border-top pt-3">
                     <!-- Context buttons can go here -->
                    <button class="btn btn-outline-primary btn-sm rounded-pill px-4" onclick="viewOrder(${order.order_id})">
                        Xem chi tiết & Theo dõi
                    </button>
                </div>
            </div>
        </div>
    `}).join('');

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
