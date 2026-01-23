/**
 * Staff Orders Page Script
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication và role
    if (!isAuthenticated() || getUserRole() !== 'STAFF') {
        window.location.href = '../index.html#auth';
        return;
    }
    
    // Load user info
    API.getCurrentUser()
        .then(user => {
            const el = document.getElementById('staffWelcome');
            if (el) el.textContent = `Xin chào, ${user.full_name}`;
        })
        .catch(() => {});
    
    // Load orders
    loadOrders();
    
    // Filter
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', () => loadOrders());
    }
    
    // Progress modal handlers
    const btnSaveProgress = document.getElementById('btnSaveProgress');
    if (btnSaveProgress) {
        btnSaveProgress.addEventListener('click', saveProgress);
    }
});

async function loadOrders() {
    try {
        const orders = await API.getOrders();
        updateStats(orders);
        const filtered = applyFilters(orders);
        displayOrders(filtered);
    } catch (error) {
        console.error('Error loading orders:', error);
        document.getElementById('ordersList').innerHTML = 
            '<div class="alert alert-danger">Không thể tải danh sách đơn hàng</div>';
    }
}

function applyFilters(orders) {
    const statusFilter = document.getElementById('statusFilter')?.value || '';
    return statusFilter ? orders.filter(o => o?.status?.status_code === statusFilter) : orders;
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
                <div class="mb-2 fw-semibold">Chưa có đơn hàng được phân công</div>
                <div class="text-muted small">Admin sẽ phân công đơn hàng cho bạn khi có đơn mới.</div>
            </div>
        `;
        return;
    }
    
    const html = orders.map(order => `
        <div class="card mb-3 shadow-sm">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h5 class="card-title mb-2">${order.service ? order.service.service_name : 'N/A'}</h5>
                        <div class="mb-2">
                            <span class="badge bg-${getStatusBadgeColor(order.status.status_code)} me-2">
                                ${order.status.status_name}
                            </span>
                            <span class="text-muted small">Mã: ${order.order_code}</span>
                        </div>
                        <div class="text-muted small">
                            <div><strong>Khách hàng:</strong> ${order.customer ? order.customer.full_name : 'N/A'}</div>
                            <div><strong>Địa chỉ:</strong> ${order.service_address}</div>
                            <div><strong>Ngày hẹn:</strong> ${formatDate(order.scheduled_date)} ${order.scheduled_time ? order.scheduled_time : ''}</div>
                            ${order.notes ? `<div><strong>Ghi chú:</strong> ${order.notes}</div>` : ''}
                        </div>
                    </div>
                    <div class="col-md-4 text-end mt-3 mt-md-0">
                        <div class="mb-2">
                            <strong class="text-primary">${formatCurrency(order.total_amount)}</strong>
                        </div>
                        <div class="d-flex flex-column gap-2">
                            <button class="btn btn-sm btn-primary" onclick="viewOrder(${order.order_id})">
                                Xem chi tiết
                            </button>
                            ${order.status.status_code !== 'COMPLETED' && order.status.status_code !== 'CANCELLED' ? `
                                <button class="btn btn-sm btn-success" onclick="openProgressModal(${order.order_id})">
                                    Cập nhật tiến độ
                                </button>
                            ` : ''}
                        </div>
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

function viewOrder(orderId) {
    // Xem chi tiết đơn hàng (có thể mở modal hoặc trang riêng)
    API.getOrder(orderId)
        .then(order => {
            const detail = `
Mã đơn: ${order.order_code}
Khách hàng: ${order.customer ? order.customer.full_name : 'N/A'}
Dịch vụ: ${order.service ? order.service.service_name : 'N/A'}
Địa chỉ: ${order.service_address}
Ngày hẹn: ${formatDate(order.scheduled_date)} ${order.scheduled_time || ''}
Tổng tiền: ${formatCurrency(order.total_amount)}
Trạng thái: ${order.status.status_name}
${order.notes ? `Ghi chú: ${order.notes}` : ''}
            `.trim();
            alert(detail);
        })
        .catch(error => {
            alert('Lỗi: ' + error.message);
        });
}

function openProgressModal(orderId) {
    document.getElementById('progressOrderId').value = orderId;
    document.getElementById('progressNote').value = '';
    document.getElementById('progressImageUrls').value = '';
    document.getElementById('progressIssue').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('progressModal'));
    modal.show();
}

function saveProgress() {
    const orderId = parseInt(document.getElementById('progressOrderId').value);
    const note = document.getElementById('progressNote').value.trim();
    const imageUrlsText = document.getElementById('progressImageUrls').value.trim();
    const issue = document.getElementById('progressIssue').value.trim();
    
    if (!note) {
        alert('Vui lòng nhập ghi chú tiến độ!');
        return;
    }
    
    // Parse image URLs
    let urls = [];
    if (imageUrlsText) {
        urls = imageUrlsText.split(/[,\n]/)
            .map(url => url.trim())
            .filter(url => url.length > 0);
    }
    
    const btnSave = document.getElementById('btnSaveProgress');
    const originalText = btnSave.textContent;
    btnSave.disabled = true;
    btnSave.textContent = 'Đang lưu...';
    
    API.addProgress(orderId, {
        progress_note: note,
        image_urls: urls,
        issue_report: issue || null
    })
    .then(() => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('progressModal'));
        if (modal) modal.hide();
        alert('Cập nhật tiến độ thành công!');
        loadOrders();
    })
    .catch(error => {
        alert('Lỗi: ' + error.message);
    })
    .finally(() => {
        btnSave.disabled = false;
        btnSave.textContent = originalText;
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}
