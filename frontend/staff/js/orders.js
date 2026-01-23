/**
 * Staff Orders Page Script
 */

document.addEventListener('DOMContentLoaded', function () {
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
        .catch(() => { });

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
        const orders = await API.staffGetOrders();
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
                            ${order.status.status_code === 'CONFIRMED' ? `
                                <button class="btn btn-sm btn-info" onclick="startOrder(${order.order_id})">
                                    Nhận việc
                                </button>
                            ` : ''}
                            ${order.status.status_code === 'IN_PROGRESS' ? `
                                <button class="btn btn-sm btn-success" onclick="openProgressModal(${order.order_id})">
                                    Cập nhật tiến độ
                                </button>
                                <button class="btn btn-sm btn-warning" onclick="completeOrder(${order.order_id})">
                                    Hoàn thành
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
    // Hiển thị modal
    const modal = new bootstrap.Modal(document.getElementById('orderDetailModal'));
    modal.show();

    // Load chi tiết đơn hàng
    Promise.all([
        API.staffGetOrder(orderId),
        API.staffGetProgress(orderId)
    ])
        .then(([order, progressList]) => {
            const content = document.getElementById('orderDetailContent');

            const html = `
            <div class="mb-4">
                <h6 class="fw-semibold mb-3">Thông tin đơn hàng</h6>
                <div class="row g-2">
                    <div class="col-6">
                        <div class="text-muted small">Mã đơn</div>
                        <div class="fw-semibold">${order.order_code}</div>
                    </div>
                    <div class="col-6">
                        <div class="text-muted small">Trạng thái</div>
                        <div>
                            <span class="badge bg-${getStatusBadgeColor(order.status.status_code)}">
                                ${order.status.status_name}
                            </span>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="text-muted small">Khách hàng</div>
                        <div>${order.customer ? order.customer.full_name : 'N/A'}</div>
                    </div>
                    <div class="col-6">
                        <div class="text-muted small">Số điện thoại</div>
                        <div>${order.customer?.phone_number || 'N/A'}</div>
                    </div>
                    <div class="col-12">
                        <div class="text-muted small">Dịch vụ</div>
                        <div>${order.service ? order.service.service_name : 'N/A'}</div>
                    </div>
                    <div class="col-12">
                        <div class="text-muted small">Địa chỉ</div>
                        <div>${order.service_address}</div>
                    </div>
                    <div class="col-6">
                        <div class="text-muted small">Ngày hẹn</div>
                        <div>${formatDate(order.scheduled_date)} ${order.scheduled_time || ''}</div>
                    </div>
                    <div class="col-6">
                        <div class="text-muted small">Tổng tiền</div>
                        <div class="text-primary fw-semibold">${formatCurrency(order.total_amount)}</div>
                    </div>
                    ${order.notes ? `
                        <div class="col-12">
                            <div class="text-muted small">Ghi chú</div>
                            <div>${order.notes}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
            
            <hr>
            
            <div>
                <h6 class="fw-semibold mb-3">Lịch sử tiến độ (${progressList.length})</h6>
                ${progressList.length > 0 ? `
                    <div class="timeline">
                        ${progressList.map(p => `
                            <div class="card mb-2">
                                <div class="card-body p-3">
                                    <div class="d-flex justify-content-between align-items-start mb-2">
                                        <div class="fw-semibold">${p.staff?.full_name || 'Nhân viên'}</div>
                                        <div class="text-muted small">${formatDateTime(p.created_at)}</div>
                                    </div>
                                    <div class="mb-2">${p.progress_note}</div>
                                    ${p.image_urls && p.image_urls.length > 0 ? `
                                        <div class="mb-2">
                                            <div class="text-muted small mb-1">Hình ảnh:</div>
                                            <div class="d-flex flex-wrap gap-2">
                                                ${p.image_urls.map(url => `
                                                    <a href="${url}" target="_blank" class="text-decoration-none">
                                                        <img src="${url}" alt="Progress" class="rounded" style="width: 80px; height: 80px; object-fit: cover;">
                                                    </a>
                                                `).join('')}
                                            </div>
                                        </div>
                                    ` : ''}
                                    ${p.issue_report ? `
                                        <div class="alert alert-warning mb-0 py-2 px-3">
                                            <strong>Vấn đề:</strong> ${p.issue_report}
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div class="text-center text-muted py-3">
                        <small>Chưa có cập nhật tiến độ nào</small>
                    </div>
                `}
            </div>
        `;

            content.innerHTML = html;
        })
        .catch(error => {
            const content = document.getElementById('orderDetailContent');
            content.innerHTML = `
            <div class="alert alert-danger">
                Lỗi: ${error.message}
            </div>
        `;
        });
}

function startOrder(orderId) {
    if (!confirm('Bạn có chắc muốn nhận việc này không?')) {
        return;
    }

    API.staffStartOrder(orderId)
        .then(response => {
            alert(response.message || 'Đã nhận việc thành công!');
            loadOrders();
        })
        .catch(error => {
            alert('Lỗi: ' + error.message);
        });
}

function completeOrder(orderId) {
    if (!confirm('Bạn có chắc muốn hoàn thành công việc này không?')) {
        return;
    }

    API.staffCompleteOrder(orderId)
        .then(response => {
            alert(response.message || 'Đã hoàn thành công việc!');
            loadOrders();
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

    API.staffAddProgress(orderId, {
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

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}
