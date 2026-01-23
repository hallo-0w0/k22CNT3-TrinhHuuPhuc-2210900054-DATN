/**
 * Order Detail Page Script
 */

let currentOrder = null;
let orderId = null;

document.addEventListener('DOMContentLoaded', function () {
    // Check authentication và role
    if (!isAuthenticated() || getUserRole() !== 'ADMIN') {
        window.location.href = '../login.html';
        return;
    }

    // Get order ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    orderId = urlParams.get('id');

    if (!orderId) {
        alert('Không tìm thấy mã đơn hàng');
        window.location.href = 'dashboard.html#orders';
        return;
    }

    loadOrderDetail();
});

async function loadOrderDetail() {
    try {
        currentOrder = await API.getOrder(orderId);
        displayOrderDetail();
        loadProgress();
    } catch (error) {
        console.error('Error loading order detail:', error);
        alert('Không thể tải chi tiết đơn hàng');
        window.location.href = 'dashboard.html#orders';
    }
}

function displayOrderDetail() {
    if (!currentOrder) return;

    // Order Code
    document.getElementById('orderCode').textContent = `Mã đơn: ${currentOrder.order_code}`;

    // Order Info
    const orderInfo = `
        <div class="row">
            <div class="col-md-6 mb-3">
                <strong>Mã đơn:</strong><br>
                <code>${currentOrder.order_code}</code>
            </div>
            <div class="col-md-6 mb-3">
                <strong>Ngày đặt:</strong><br>
                ${formatDate(currentOrder.order_date)}
            </div>
            <div class="col-md-6 mb-3">
                <strong>Ngày hẹn:</strong><br>
                ${formatDate(currentOrder.scheduled_date)}
            </div>
            <div class="col-md-6 mb-3">
                <strong>Giờ hẹn:</strong><br>
                ${currentOrder.scheduled_time || '—'}
            </div>
            <div class="col-12 mb-3">
                <strong>Địa chỉ dịch vụ:</strong><br>
                ${currentOrder.service_address}
            </div>
            <div class="col-md-6 mb-3">
                <strong>Số lượng:</strong><br>
                ${currentOrder.quantity} ${currentOrder.service?.unit || ''}
            </div>
            ${currentOrder.notes ? `
                <div class="col-12 mb-3">
                    <strong>Ghi chú:</strong><br>
                    <div class="p-2 bg-light rounded">${currentOrder.notes}</div>
                </div>
            ` : ''}
        </div>
    `;
    document.getElementById('orderInfo').innerHTML = orderInfo;

    // Customer Info
    const customer = currentOrder.customer;
    const customerInfo = `
        <div class="row">
            <div class="col-md-6 mb-3">
                <strong>Họ tên:</strong><br>
                ${customer?.full_name || 'N/A'}
            </div>
            <div class="col-md-6 mb-3">
                <strong>Email:</strong><br>
                ${customer?.email || 'N/A'}
            </div>
            <div class="col-md-6 mb-3">
                <strong>Số điện thoại:</strong><br>
                ${customer?.phone_number || '—'}
            </div>
            <div class="col-md-6 mb-3">
                <strong>Member Level:</strong><br>
                ${customer?.member_level ?
            `<span class="badge bg-info">${customer.member_level.level_name}</span>` :
            '—'}
            </div>
            ${customer?.address ? `
                <div class="col-12 mb-3">
                    <strong>Địa chỉ:</strong><br>
                    ${customer.address}
                </div>
            ` : ''}
        </div>
    `;
    document.getElementById('customerInfo').innerHTML = customerInfo;

    // Service Info
    const service = currentOrder.service;
    const serviceInfo = `
        <div class="row">
            <div class="col-12 mb-3">
                <strong>Tên dịch vụ:</strong><br>
                ${service?.service_name || 'N/A'}
            </div>
            ${service?.service_description ? `
                <div class="col-12 mb-3">
                    <strong>Mô tả:</strong><br>
                    ${service.service_description}
                </div>
            ` : ''}
            <div class="col-md-6 mb-3">
                <strong>Giá cơ bản:</strong><br>
                ${formatCurrency(currentOrder.unit_price)}
            </div>
            <div class="col-md-6 mb-3">
                <strong>Thời lượng:</strong><br>
                ${service?.duration_hours ? service.duration_hours + ' giờ' : '—'}
            </div>
        </div>
    `;
    document.getElementById('serviceInfo').innerHTML = serviceInfo;

    // Status Card
    const status = currentOrder.status;
    const statusCard = `
        <div class="text-center mb-3">
            <span class="badge bg-${getStatusBadgeColor(status.status_code)} fs-6 p-3">
                ${status.status_name}
            </span>
        </div>
        <div class="d-grid gap-2">
            <button class="btn btn-primary" onclick="showStatusModal()">
                ✏️ Cập nhật trạng thái
            </button>
        </div>
    `;
    document.getElementById('statusCard').innerHTML = statusCard;

    // Payment Summary
    const paymentSummary = `
        <div class="mb-3">
            <div class="d-flex justify-content-between mb-2">
                <span>Giá gốc:</span>
                <strong>${formatCurrency(currentOrder.unit_price * currentOrder.quantity)}</strong>
            </div>
            ${currentOrder.discount_percentage > 0 ? `
                <div class="d-flex justify-content-between mb-2">
                    <span>Giảm giá (${currentOrder.discount_percentage}%):</span>
                    <strong class="text-success">-${formatCurrency(currentOrder.discount_amount)}</strong>
                </div>
            ` : ''}
            <hr>
            <div class="d-flex justify-content-between">
                <span class="fs-5"><strong>Tổng tiền:</strong></span>
                <span class="fs-5"><strong class="text-primary">${formatCurrency(currentOrder.total_amount)}</strong></span>
            </div>
        </div>
    `;
    document.getElementById('paymentSummary').innerHTML = paymentSummary;

    // Staff Assignment
    // TODO: Load staff assignment from order
    const staffAssignment = `
        <div id="staffInfo">
            <p class="text-muted">Chưa phân công nhân viên</p>
            <button class="btn btn-sm btn-primary" onclick="assignStaff()">
                Phân công nhân viên
            </button>
        </div>
    `;
    document.getElementById('staffAssignment').innerHTML = staffAssignment;

    // Order Actions
    const actions = getOrderActionButtons();
    document.getElementById('orderActions').innerHTML = actions;
}

function getOrderActionButtons() {
    const status = currentOrder.status.status_code;
    let buttons = '';

    if (status === 'PENDING') {
        buttons += `<button class="btn btn-success me-2" onclick="quickUpdateStatus('CONFIRMED')">✓ Xác nhận</button>`;
    } else if (status === 'CONFIRMED') {
        buttons += `<button class="btn btn-primary me-2" onclick="quickUpdateStatus('IN_PROGRESS')">▶ Bắt đầu</button>`;
    } else if (status === 'IN_PROGRESS') {
        buttons += `<button class="btn btn-success me-2" onclick="quickUpdateStatus('COMPLETED')">✓ Hoàn thành</button>`;
    }

    if (status !== 'COMPLETED' && status !== 'CANCELLED') {
        buttons += `<button class="btn btn-danger" onclick="quickUpdateStatus('CANCELLED')">✕ Hủy</button>`;
    }

    return buttons;
}

function showStatusModal() {
    const modal = new bootstrap.Modal(document.getElementById('statusModal'));
    document.getElementById('newStatus').value = currentOrder.status.status_code;
    document.getElementById('statusReason').value = '';
    modal.show();
}

async function updateStatus() {
    const newStatus = document.getElementById('newStatus').value;
    const reason = document.getElementById('statusReason').value;

    if (!confirm(`Bạn có chắc muốn cập nhật trạng thái sang "${newStatus}"?`)) {
        return;
    }

    try {
        await API.updateOrderStatus(orderId, newStatus, reason);
        showAlert('Cập nhật trạng thái thành công!', 'success');
        bootstrap.Modal.getInstance(document.getElementById('statusModal')).hide();
        loadOrderDetail();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

async function quickUpdateStatus(statusCode) {
    if (!confirm(`Bạn có chắc muốn cập nhật trạng thái sang "${statusCode}"?`)) {
        return;
    }

    try {
        await API.updateOrderStatus(orderId, statusCode);
        showAlert('Cập nhật trạng thái thành công!', 'success');
        loadOrderDetail();
    } catch (error) {
        showAlert('Lỗi: ' + error.message, 'danger');
    }
}

async function loadProgress() {
    try {
        const progress = await API.getProgress(orderId);
        displayProgress(progress);
    } catch (error) {
        console.error('Error loading progress:', error);
        document.getElementById('progressTimeline').innerHTML =
            '<p class="text-muted">Chưa có tiến độ nào.</p>';
    }
}

function displayProgress(progressList) {
    const container = document.getElementById('progressTimeline');

    if (progressList.length === 0) {
        container.innerHTML = '<p class="text-muted">Chưa có tiến độ nào.</p>';
        return;
    }

    const timeline = `
        <div class="timeline">
            ${progressList.map(p => `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <strong>${p.staff?.full_name || 'N/A'}</strong>
                                <span class="text-muted small ms-2">${formatDateTime(p.created_at)}</span>
                            </div>
                        </div>
                        ${p.progress_note ? `
                            <div class="mb-2">
                                <strong>Ghi chú:</strong><br>
                                ${p.progress_note}
                            </div>
                        ` : ''}
                        ${p.issue_report ? `
                            <div class="mb-2">
                                <strong>Báo cáo vấn đề:</strong><br>
                                <div class="alert alert-warning mb-0">${p.issue_report}</div>
                            </div>
                        ` : ''}
                        ${p.image_urls && p.image_urls.length > 0 ? `
                            <div class="mt-2">
                                <strong>Hình ảnh:</strong><br>
                                <div class="d-flex flex-wrap gap-2 mt-2">
                                    ${p.image_urls.map(url => `
                                        <a href="${url}" target="_blank">
                                            <img src="${url}" alt="Progress image" class="img-thumbnail" style="max-width: 150px; max-height: 150px;">
                                        </a>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    container.innerHTML = timeline;
}

function assignStaff() {
    window.location.href = `dashboard.html#orders`;
    // TODO: Implement assign staff modal
}

// Utility functions
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
    return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}
