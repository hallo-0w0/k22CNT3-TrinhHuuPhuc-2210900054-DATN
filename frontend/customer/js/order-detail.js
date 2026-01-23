/**
 * Customer Order Detail Page Script
 */

let currentOrder = null;
let orderId = null;

document.addEventListener('DOMContentLoaded', function () {
    // Check authentication
    if (!isAuthenticated() || getUserRole() !== 'CUSTOMER') {
        window.location.href = '../index.html#auth';
        return;
    }

    // Get order ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    orderId = urlParams.get('id');

    if (!orderId) {
        alert('Không tìm thấy mã đơn hàng');
        window.location.href = 'orders.html';
        return;
    }

    loadOrderDetail();

    // Handle reason change
    const reasonSelect = document.getElementById('cancelReason');
    const otherGroup = document.getElementById('otherReasonGroup');
    if (reasonSelect) {
        reasonSelect.addEventListener('change', function () {
            if (this.value === 'Khác') {
                otherGroup.classList.remove('d-none');
            } else {
                otherGroup.classList.add('d-none');
            }
        });
    }
});

async function loadOrderDetail() {
    try {
        currentOrder = await API.getOrder(orderId);
        displayOrderDetail();
        loadProgress(); // Helper from admin/js but simplified if API allows
    } catch (error) {
        console.error('Error loading order detail:', error);

        // Try to parse error data if available
        let detailMsg = error.message;
        if (error.data && error.data.error) {
            detailMsg = error.data.error;
        }

        document.getElementById('orderInfo').innerHTML =
            `<div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>Không thể tải chi tiết đơn hàng<br>
                <small class="text-muted">Lỗi: ${detailMsg}</small>
                <div class="mt-2"><button class="btn btn-outline-danger btn-sm" onclick="window.location.reload()">Thử lại</button></div>
            </div>`;
    }
}

function displayOrderDetail() {
    if (!currentOrder) return;

    // Order Code
    document.getElementById('orderCode').textContent = `Mã đơn: ${currentOrder.order_code}`;

    // Order Info
    const orderHTML = `
        <div class="row">
            <div class="col-md-6 mb-3">
                <small class="text-muted d-block">Mã đơn hàng</small>
                <strong>#${currentOrder.order_code}</strong>
            </div>
            <div class="col-md-6 mb-3">
                <small class="text-muted d-block">Ngày đặt</small>
                <span>${formatDate(currentOrder.order_date)}</span>
            </div>
             <div class="col-md-6 mb-3">
                <small class="text-muted d-block">Ngày hẹn</small>
                <span>${formatDate(currentOrder.scheduled_date)}</span>
            </div>
            <div class="col-md-6 mb-3">
                <small class="text-muted d-block">Giờ hẹn</small>
                <span>${currentOrder.scheduled_time || '—'}</span>
            </div>
            <div class="col-12 mb-3">
                <small class="text-muted d-block">Địa chỉ thực hiện</small>
                <span>${currentOrder.service_address}</span>
            </div>
             ${currentOrder.notes ? `
                <div class="col-12">
                    <small class="text-muted d-block">Ghi chú của bạn</small>
                    <div class="p-2 bg-light rounded text-small">${currentOrder.notes}</div>
                </div>
            ` : ''}
        </div>
    `;
    document.getElementById('orderInfo').innerHTML = orderHTML;

    // Service Info
    const service = currentOrder.service;
    const serviceHTML = `
        <div class="d-flex align-items-start gap-3">
             <img src="../images/services/${service?.service_id || 1}.jpg" class="rounded object-fit-cover" width="80" height="80"
                  onerror="this.src='../images/services/1.jpg'">
             <div>
                <h6 class="mb-1 fw-bold">${service?.service_name || 'Dịch vụ'}</h6>
                <p class="text-muted small mb-1 line-clamp-2">${service?.service_description || ''}</p>
                <div class="small">
                    <span>${formatCurrency(currentOrder.unit_price)}</span> x ${currentOrder.quantity} ${service?.unit || ''}
                </div>
             </div>
        </div>
    `;
    document.getElementById('serviceInfo').innerHTML = serviceHTML;

    // Status Card
    const status = currentOrder.status;
    const statusHTML = `
        <div class="text-center mb-3">
            <span class="badge bg-${getStatusBadgeColor(status.status_code)} bg-opacity-10 text-${getStatusBadgeColor(status.status_code)} fs-6 px-3 py-2 rounded-pill border border-${getStatusBadgeColor(status.status_code)}">
                ${status.status_name}
            </span>
        </div>
        ${status.description ? `<p class="text-muted small text-center">${status.description}</p>` : ''}
        
        ${['PENDING', 'CONFIRMED'].includes(status.status_code) ? `
            <div class="d-grid mt-3">
                <button class="btn btn-outline-danger btn-sm" data-bs-toggle="modal" data-bs-target="#cancelOrderModal" onclick="checkStatusForWarning('${status.status_code}')">
                    ${status.status_code === 'CONFIRMED' ? 'Yêu cầu hủy / thay đổi' : 'Hủy đơn hàng'}
                </button>
                <small class="text-center text-muted mt-2" style="font-size: 0.75rem">
                    ${status.status_code === 'CONFIRMED'
                ? 'Đơn đã xác nhận. Hủy đơn có thể ảnh hưởng đến uy tín.'
                : 'Bạn có thể hủy đơn trước khi nhân viên bắt đầu.'}
                </small>
            </div>
        ` : ''}
    `;
    document.getElementById('statusCard').innerHTML = statusHTML;

    // Payment Summary
    const paymentHTML = `
         <div class="mb-2 d-flex justify-content-between">
            <span class="text-muted">Tạm tính</span>
            <span>${formatCurrency(currentOrder.unit_price * currentOrder.quantity)}</span>
        </div>
         ${currentOrder.discount_percentage > 0 ? `
             <div class="mb-2 d-flex justify-content-between text-success">
                <span>Giảm giá thành viên <small class="text-muted">(lúc đặt)</small></span>
                <span>-${formatCurrency(currentOrder.discount_amount)}</span>
            </div>
        ` : ''}
        <hr class="my-2">
        <div class="d-flex justify-content-between align-items-center">
            <span class="fw-bold">Tổng cộng</span>
            <span class="fw-bold text-primary fs-5">${formatCurrency(currentOrder.total_amount)}</span>
        </div>
    `;
    document.getElementById('paymentSummary').innerHTML = paymentHTML;

    // Staff Info (if needed)
    // TODO: Implement Staff View if API supports it
}

// Progress Timeline (Reuse logic but visually simplified)
async function loadProgress() {
    try {
        const progress = await API.getProgress(orderId); // Make sure API.getProgress works for Customer
        const container = document.getElementById('progressTimeline');

        if (!progress || progress.length === 0) {
            container.innerHTML = '<p class="text-muted text-center small my-3">Chưa có cập nhật tiến độ.</p>';
            return;
        }

        const timelineHTML = `
            <div class="timeline ps-3 border-start">
                ${progress.map(p => `
                    <div class="position-relative mb-4 ps-3">
                         <div class="position-absolute top-0 start-0 translate-middle rounded-circle bg-primary" 
                              style="width: 10px; height: 10px; left: 0 !important; top: 6px !important"></div>
                        <div class="small text-muted mb-1">${formatDateTime(p.created_at)}</div>
                        <div class="fw-semibold text-dark">${p.progress_note || 'Cập nhật trạng thái'}</div>
                        ${p.issue_report ? `
                             <div class="alert alert-warning py-2 px-3 mt-2 small icon-link">
                                <i class="bi bi-exclamation-triangle"></i> ${p.issue_report}
                             </div>
                        ` : ''}
                         ${p.image_urls && p.image_urls.length > 0 ? `
                            <div class="d-flex gap-2 mt-2 overflow-auto pb-2">
                                ${p.image_urls.map(url => `
                                    <a href="${url}" target="_blank">
                                        <img src="${url}" class="rounded border shadow-sm" style="width: 60px; height: 60px; object-fit: cover;">
                                    </a>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
        container.innerHTML = timelineHTML;

    } catch (e) {
        console.warn('Cannot load progress', e);
        document.getElementById('progressTimeline').innerHTML = '<p class="text-muted text-center small my-3">Chưa có cập nhật tiến độ.</p>';
    }
}


async function confirmCancelOrder() {
    const reasonSelect = document.getElementById('cancelReason');
    const commentInput = document.getElementById('cancelComment');
    const reasonValue = reasonSelect.value;

    if (!reasonValue) {
        alert('Vui lòng chọn lý do hủy đơn');
        reasonSelect.focus();
        return;
    }

    let finalReason = reasonValue;
    if (reasonValue === 'Khác') {
        const comment = commentInput.value.trim();
        if (!comment) {
            alert('Vui lòng nhập lý do cụ thể');
            commentInput.focus();
            return;
        }
        finalReason = `Khác: ${comment}`;
    }

    // Disable button
    const btn = document.getElementById('confirmCancelBtn');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Đang xử lý...';

    try {
        const response = await API.cancelOrder(orderId, finalReason);

        // Hide modal
        const modalEl = document.getElementById('cancelOrderModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();

        if (response.is_request_only) {
            // Show contact info for CONFIRMED orders
            const contactModal = new bootstrap.Modal(document.getElementById('contactSupportModal'));
            contactModal.show();
        } else {
            alert('Đã hủy đơn hàng thành công');
            loadOrderDetail();
        }
    } catch (e) {
        alert('Lỗi: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

function checkStatusForWarning(statusCode) {
    const warningEl = document.querySelector('#cancelOrderModal .alert-warning div');
    if (statusCode === 'CONFIRMED') {
        warningEl.innerHTML = '<strong>Lưu ý:</strong> Đơn hàng đã được xác nhận. Việc hủy đơn lúc này có thể ảnh hưởng đến điểm uy tín của bạn.';
    } else {
        warningEl.textContent = 'Bạn có chắc chắn muốn hủy đơn dịch vụ này không? Hành động này không thể hoàn tác.';
    }
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
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}
function formatDateTime(dateString) {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleString('vi-VN');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}
