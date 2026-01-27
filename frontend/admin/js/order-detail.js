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
                ${currentOrder.quantity}
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
                    <span class="text-muted small">${service.service_description}</span>
                </div>
            ` : ''}
            
            <div class="col-12">
                <div class="table-responsive">
                    <table class="table table-bordered table-sm mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Đơn giá</th>
                                <th>Số lượng</th>
                                <th>Đơn vị</th>
                                <th class="text-end">Thành tiền</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>${formatCurrency(currentOrder.unit_price)}</td>
                                <td>${currentOrder.quantity}</td>
                                <td>${service?.unit || 'lần'}</td>
                                <td class="text-end fw-bold">${formatCurrency(currentOrder.unit_price * currentOrder.quantity)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
    document.getElementById('serviceInfo').innerHTML = serviceInfo;

    // Status Card
    const orderStatus = currentOrder.status;
    const statusCard = `
        <div class="text-center mb-3">
            <span class="badge bg-${getStatusBadgeColor(orderStatus.status_code)} fs-6 p-3">
                ${orderStatus.status_name}
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
    const paymentStatus = (currentOrder.status.status_code === 'COMPLETED')
        ? '<span class="badge bg-success">Đã thanh toán</span>'
        : '<span class="badge bg-light text-dark border">Chưa thanh toán</span>';

    const paymentSummary = `
        <div class="mb-3">
            <div class="d-flex justify-content-between mb-2">
                <div>
                    <span class="text-muted">Tạm tính</span>
                    <div class="small text-muted" style="font-size: 0.8em">
                        ${currentOrder.quantity} x ${formatCurrency(currentOrder.unit_price)}
                    </div>
                </div>
                <span>${formatCurrency(currentOrder.unit_price * currentOrder.quantity)}</span>
            </div>
            ${currentOrder.discount_percentage > 0 ? `
                <div class="d-flex justify-content-between mb-2 text-success">
                    <div>
                         <span>Giảm giá thành viên</span>
                         <span class="badge bg-success bg-opacity-10 text-success ms-1">-${currentOrder.discount_percentage}%</span>
                    </div>
                    <span>-${formatCurrency(currentOrder.discount_amount)}</span>
                </div>
            ` : ''}
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="text-muted">Phương thức</span>
                <span class="small text-end">Thanh toán sau khi<br>hoàn thành</span>
            </div>
            <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="text-muted">Trạng thái</span>
                <div>${paymentStatus}</div>
            </div>
            <hr>
            <div class="d-flex justify-content-between">
                <span class="fs-5"><strong>Tổng cộng</strong></span>
                <span class="fs-5"><strong class="text-primary">${formatCurrency(currentOrder.total_amount)}</strong></span>
            </div>
        </div>
    `;
    document.getElementById('paymentSummary').innerHTML = paymentSummary;

    // Staff Assignment
    const assignments = currentOrder.assignments || [];
    // Active assignments only
    const activeAssignments = assignments.filter(a => a.is_active);

    let staffHtml = '';
    const status = currentOrder.status.status_code;

    if (status === 'PENDING') {
        staffHtml = `<p class="text-muted text-center my-3"><em>Đơn hàng cần được xác nhận trước khi phân công.</em></p>`;
    } else if (status === 'CONFIRMED') {
        // Giai đoạn 2: 1 Nhân viên chính
        const mainStaff = activeAssignments[0]; // Should only be one
        if (mainStaff && mainStaff.staff) {
            staffHtml = `
                <div class="border rounded p-2 mb-2 bg-light">
                    <div class="d-flex align-items-center">
                        <div class="flex-grow-1">
                            <span class="badge bg-primary mb-1">Nhân viên chính</span>
                            <h6 class="mb-0 fw-bold">${mainStaff.staff.full_name}</h6>
                            <small class="text-muted">${mainStaff.staff.email}</small>
                        </div>
                    </div>
                </div>
                <button class="btn btn-sm btn-outline-primary w-100" onclick="assignStaff()">
                    Thay đổi nhân viên chính
                </button>
            `;
        } else {
            staffHtml = `
                <p class="text-muted small text-center my-3">Chưa có nhân viên chính</p>
                <button class="btn btn-sm btn-primary w-100" onclick="assignStaff()">
                    Phân công nhân viên chính
                </button>
            `;
        }
    } else if (status === 'IN_PROGRESS') {
        // Giai đoạn 3: Danh sách nhân viên đang tham gia
        staffHtml = '<h6 class="text-muted small mb-2">Đội ngũ thực hiện:</h6>';

        if (activeAssignments.length > 0) {
            staffHtml += '<div class="list-group list-group-flush mb-3">';
            activeAssignments.forEach(a => {
                staffHtml += `
                    <div class="list-group-item px-0 py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-0 fw-bold small">${a.staff.full_name}</h6>
                                <small class="text-muted" style="font-size: 0.75rem">${a.notes || 'Thành viên'}</small>
                            </div>
                            <span class="badge bg-success rounded-pill" style="font-size: 0.6rem">Active</span>
                        </div>
                    </div>
                `;
            });
            staffHtml += '</div>';
        } else {
            staffHtml += '<p class="text-muted small text-center">Chưa có nhân viên nào.</p>';
        }

        staffHtml += `
            <button class="btn btn-sm btn-outline-primary w-100" onclick="assignStaff()">
                + Thêm nhân viên hỗ trợ
            </button>
        `;
    } else {
        // COMPLETED / CANCELLED: Read only
        if (activeAssignments.length > 0) {
            staffHtml += '<ul class="list-group list-group-flush">';
            activeAssignments.forEach(a => {
                staffHtml += `
                    <li class="list-group-item px-0">
                        <strong>${a.staff.full_name}</strong>
                        <br><small class="text-muted">${a.notes || ''}</small>
                    </li>
                `;
            });
            staffHtml += '</ul>';
        } else {
            staffHtml = '<p class="text-muted small">Không có dữ liệu phân công.</p>';
        }
    }

    document.getElementById('staffAssignment').innerHTML = staffHtml;

    // Handle Cancellation Alerts
    const mainCol = document.querySelector('.col-lg-8');
    const existingAlert = mainCol.querySelector('.alert-cancellation-info');
    if (existingAlert) existingAlert.remove();

    const history = currentOrder.status_history || [];
    const cancelRequest = history.find(h => h.change_reason && h.change_reason.startsWith('YÊU CẦU HỦY:'));
    const isCancelled = currentOrder.status.status_code === 'CANCELLED';
    const cancelReason = isCancelled
        ? (history.sort((a, b) => b.history_id - a.history_id).find(h => h.new_status_id === currentOrder.status_id)?.change_reason)
        : null;

    let warningHtml = '';
    if (cancelRequest && currentOrder.status.status_code === 'CONFIRMED') {
        warningHtml = `
            <div class="alert alert-warning border-warning d-flex align-items-start gap-3 mb-4 alert-cancellation-info shadow-sm">
                <span class="fs-4">⚠️</span>
                <div class="w-100">
                    <h5 class="alert-heading fw-bold mb-2">Khách hàng yêu cầu hủy đơn!</h5>
                    <div class="bg-white bg-opacity-50 p-3 rounded mb-3">
                         <strong class="text-dark">Lý do:</strong> <span class="text-dark">${cancelRequest.change_reason.replace('YÊU CẦU HỦY: ', '')}</span>
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-danger" onclick="quickUpdateStatus('CANCELLED', 'Chấp nhận yêu cầu hủy: ${cancelRequest.change_reason.replace('YÊU CẦU HỦY: ', '')}')">
                            ✓ Chấp nhận hủy
                        </button>
                        <a href="tel:${currentOrder.customer.phone_number}" class="btn btn-outline-dark">
                            📞 Liên hệ khách
                        </a>
                    </div>
                </div>
            </div>
         `;
    } else if (isCancelled) {
        warningHtml = `
            <div class="alert alert-danger d-flex align-items-center gap-3 mb-4 alert-cancellation-info">
                <span class="fs-4">✕</span>
                <div>
                    <h6 class="fw-bold mb-1">Đơn hàng đã bị hủy</h6>
                    <span class="small">Lý do: ${cancelReason || 'Không có lý do cụ thể'}</span>
                </div>
            </div>
         `;
    }

    if (warningHtml) {
        const div = document.createElement('div');
        div.innerHTML = warningHtml;
        mainCol.prepend(div.firstElementChild);
    }

    // Order Actions
    const actions = getOrderActionButtons();
    document.getElementById('orderActions').innerHTML = actions;
}

function getOrderActionButtons() {
    const status = currentOrder.status.status_code;
    let buttons = '';

    if (status === 'PENDING') {
        buttons += `<button class="btn btn-success me-2" onclick="quickUpdateStatus('CONFIRMED')">✓ Xác nhận đơn</button>`;
        buttons += `<button class="btn btn-outline-danger" onclick="quickUpdateStatus('CANCELLED')">✕ Hủy đơn</button>`;
    } else if (status === 'CONFIRMED') {
        buttons += `<button class="btn btn-primary me-2" onclick="quickUpdateStatus('IN_PROGRESS')">▶ Bắt đầu thực hiện</button>`;
        buttons += `<button class="btn btn-outline-danger" onclick="quickUpdateStatus('CANCELLED')">✕ Hủy đơn</button>`;
    } else if (status === 'IN_PROGRESS') {
        buttons += `<button class="btn btn-success me-2" onclick="quickUpdateStatus('COMPLETED')">✓ Hoàn thành</button>`;
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

    const statusMap = {
        'PENDING': 'Chờ xử lý',
        'CONFIRMED': 'Đã xác nhận',
        'IN_PROGRESS': 'Đang thực hiện',
        'COMPLETED': 'Hoàn thành',
        'CANCELLED': 'Đã hủy'
    };

    const confirmMsg = `Bạn có chắc chắn muốn cập nhật trạng thái đơn hàng sang "${statusMap[newStatus] || newStatus}"?\n\nHành động này sẽ được lưu vào lịch sử.`;

    if (!confirm(confirmMsg)) {
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

async function quickUpdateStatus(statusCode, reason = '') {
    const statusMap = {
        'CONFIRMED': 'Đã xác nhận',
        'IN_PROGRESS': 'Đang thực hiện',
        'COMPLETED': 'Hoàn thành',
        'CANCELLED': 'Đã hủy'
    };

    let confirmMsg = `Bạn có chắc chắn muốn cập nhật trạng thái đơn hàng sang "${statusMap[statusCode] || statusCode}"?`;

    if (statusCode === 'CANCELLED') {
        confirmMsg = `GẤP: Bạn đang thực hiện HỦY đơn hàng này.\n\nBạn có chắc chắn muốn tiếp tục không?`;
    }

    if (!confirm(confirmMsg)) {
        return;
    }

    // Double check for cancellation if it wasn't a request
    if (statusCode === 'CANCELLED' && !reason && !confirm("Xác nhận lần 2: Hành động này KHÔNG THỂ hoàn tác. Bạn vẫn muốn hủy?")) {
        return;
    }

    try {
        await API.updateOrderStatus(orderId, statusCode, reason);
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

async function assignStaff() {
    try {
        // Fetch staff list first
        // Use API helper instead of raw fetch to avoid BASE_URL issues
        const staffList = await API.adminGetStaff();

        const select = document.getElementById('staffSelect');
        select.innerHTML = '<option value="">-- Chọn nhân viên --</option>';
        staffList.forEach(s => {
            select.innerHTML += `<option value="${s.user_id}">${s.full_name} (${s.email})</option>`;
        });

        // Set default note based on context using current status
        const status = currentOrder.status.status_code;
        const noteInput = document.getElementById('assignNotes');
        if (status === 'CONFIRMED') {
            document.getElementById('assignModalTitle').textContent = 'Phân công nhân viên chính';
            noteInput.value = 'Nhân viên chính';
        } else if (status === 'IN_PROGRESS') {
            document.getElementById('assignModalTitle').textContent = 'Thêm nhân viên hỗ trợ';
            noteInput.value = 'Nhân viên hỗ trợ';
        } else {
            noteInput.value = '';
        }

        const modal = new bootstrap.Modal(document.getElementById('assignStaffModal'));
        modal.show();

    } catch (error) {
        // Handle potential errors from API helper
        const msg = error.message || 'Không thể tải danh sách nhân viên';
        showAlert('Lỗi: ' + msg, 'danger');
    }
}

async function submitAssignment() {
    const staffId = document.getElementById('staffSelect').value;
    const notes = document.getElementById('assignNotes').value;

    if (!staffId) {
        alert('Vui lòng chọn nhân viên');
        return;
    }

    try {
        // Use API helper
        await API.adminAssignOrder(orderId, { staff_id: staffId, notes: notes });

        showAlert('Phân công thành công!', 'success');
        bootstrap.Modal.getInstance(document.getElementById('assignStaffModal')).hide();
        loadOrderDetail();
    } catch (e) {
        showAlert('Lỗi: ' + e.message, 'danger');
    }
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
