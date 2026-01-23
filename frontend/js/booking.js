/**
 * Booking Handling Script
 * Handles the Booking Modal specific logic
 */

const BookingManager = {
    selectedService: null,

    init: function () {
        this.injectModal();
        // Event listeners handling is inside injectModal or after it
    },

    injectModal: function () {
        if (document.getElementById('bookingModal')) return;

        const modalHTML = `
        <div class="modal fade pclear-modal" id="bookingModal" tabindex="-1" aria-hidden="true" data-bs-backdrop="static">
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title fw-bold">
                            <i class="bi bi-calendar-check me-2"></i>Đặt dịch vụ
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body p-4">
                        <div id="bookingAlertContainer"></div>
                        <form id="bookingForm">
                            <input type="hidden" id="bookingServiceId">
                            
                            <!-- Step 1: Service Info (Read Only) -->
                            <div class="mb-4 p-3 bg-light rounded-3 border">
                                <h6 class="fw-bold text-primary mb-3">1. Dịch vụ đã chọn</h6>
                                <div class="row align-items-center">
                                    <div class="col-md-2 mb-2 mb-md-0">
                                         <img id="bookingServiceImg" src="" class="img-fluid rounded border" alt="Service">
                                    </div>
                                    <div class="col-md-7 mb-2 mb-md-0">
                                        <h5 class="fw-bold mb-1" id="bookingServiceName">Service Name</h5>
                                        <div class="text-muted small line-clamp-2" id="bookingServiceDesc">Description</div>
                                    </div>
                                    <div class="col-md-3 text-md-end">
                                        <div class="text-primary fw-bold fs-5" id="bookingServicePrice">0 đ</div>
                                        <small class="text-muted" id="bookingServiceUnit">/ lần</small>
                                    </div>
                                </div>
                            </div>

                            <!-- Step 2: Booking Info -->
                            <h6 class="fw-bold text-primary mb-3">2. Thông tin thực hiện</h6>
                            <div class="row g-3 mb-4">
                                <div class="col-md-12">
                                    <label class="form-label fw-semibold">Địa chỉ vệ sinh <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="bookingAddress" required placeholder="Số nhà, đường, phường, quận...">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Ngày thực hiện <span class="text-danger">*</span></label>
                                    <input type="date" class="form-control" id="bookingDate" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Giờ mong muốn <span class="text-danger">*</span></label>
                                    <select class="form-select" id="bookingTime" required>
                                        <option value="">Chọn khung giờ</option>
                                        <option value="08:00">08:00 - Sáng</option>
                                        <option value="09:00">09:00 - Sáng</option>
                                        <option value="10:00">10:00 - Sáng</option>
                                        <option value="11:00">11:00 - Sáng</option>
                                        <option value="13:00">13:00 - Chiều</option>
                                        <option value="14:00">14:00 - Chiều</option>
                                        <option value="15:00">15:00 - Chiều</option>
                                        <option value="16:00">16:00 - Chiều</option>
                                        <option value="17:00">17:00 - Chiều</option>
                                    </select>
                                </div>
                                <div class="col-md-12">
                                     <label class="form-label fw-semibold">Ghi chú thêm</label>
                                     <textarea class="form-control" id="bookingNote" rows="2" placeholder="VD: Nhà có trẻ nhỏ, cần mang dụng cụ lau kính..."></textarea>
                                </div>
                            </div>

                            <!-- Step 3: Payment Preview -->
                            <div class="bg-primary-subtle p-3 rounded-3 border border-primary-subtle">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="text-primary-emphasis fw-semibold">Tổng thanh toán dự kiến:</span>
                                    <span class="fs-4 fw-bold text-primary" id="bookingTotal">0 đ</span>
                                </div>
                                <div class="text-muted small mt-1 text-end">* Chưa bao gồm phụ phí phát sinh (nếu có)</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer bg-light">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Đóng</button>
                        <button type="button" class="btn btn-primary px-4 fw-bold" onclick="BookingManager.submitBooking()">
                            <i class="bi bi-check-circle-fill me-2"></i>Xác nhận đặt dịch vụ
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Success Modal -->
        <div class="modal fade" id="bookingSuccessModal" tabindex="-1" aria-hidden="true" data-bs-backdrop="static">
             <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content text-center p-4">
                    <div class="modal-body">
                        <div class="mb-3">
                             <div class="d-inline-flex align-items-center justify-content-center bg-success text-white rounded-circle" style="width: 80px; height: 80px;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">
                                  <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/>
                                </svg>
                             </div>
                        </div>
                        <h4 class="fw-bold text-success mb-2">Đặt dịch vụ thành công!</h4>
                        <p class="text-muted">Đơn hàng của bạn đã được tạo. Nhân viên PCLEAR sẽ sớm liên hệ để xác nhận.</p>
                        <div class="mt-4 d-grid gap-2">
                            <a href="customer/orders.html" class="btn btn-primary">Xem đơn hàng của tôi</a>
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Đóng cửa sổ</button>
                        </div>
                    </div>
                </div>
             </div>
        </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Pre-fill date with tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        document.getElementById('bookingDate').valueAsDate = tomorrow;
        document.getElementById('bookingDate').min = new Date().toISOString().split("T")[0];
    },

    openModal: async function (serviceId) {
        if (!isAuthenticated()) {
            const authModal = new bootstrap.Modal(document.getElementById('authModal'));
            authModal.show();
            return;
        }

        try {
            // Load service details
            const service = await API.getService(serviceId); // Ensure API.getService exists
            this.selectedService = service;

            // Populate Modal
            document.getElementById('bookingServiceId').value = service.service_id;
            document.getElementById('bookingServiceName').textContent = service.service_name;
            document.getElementById('bookingServiceDesc').textContent = service.service_description;
            document.getElementById('bookingServicePrice').textContent = this.formatCurrency(service.base_price);
            document.getElementById('bookingServiceUnit').textContent = service.unit ? `/ ${service.unit}` : '';
            document.getElementById('bookingTotal').textContent = this.formatCurrency(service.base_price);
            document.getElementById('bookingServiceImg').src = `images/services/${service.service_id}.jpg`;
            document.getElementById('bookingServiceImg').onerror = function () { this.src = 'images/services/1.jpg'; };

            // Pre-fill user address if available (Assuming we might store it or fetch it)
            // const user = await API.getCurrentUser();
            // if(user && user.address) document.getElementById('bookingAddress').value = user.address;

            const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
            modal.show();

        } catch (error) {
            console.error(error);
            alert('Không thể tải thông tin dịch vụ');
        }
    },

    submitBooking: async function () {
        const serviceId = document.getElementById('bookingServiceId').value;
        const address = document.getElementById('bookingAddress').value;
        const date = document.getElementById('bookingDate').value;
        const time = document.getElementById('bookingTime').value;
        const note = document.getElementById('bookingNote').value;

        // Validation
        if (!address || !date || !time) {
            this.showAlert('Vui lòng điền đầy đủ các trường bắt buộc (*)', 'danger');
            return;
        }

        const btn = document.querySelector('#bookingModal .btn-primary');
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang xử lý...';

        try {
            const orderData = {
                service_id: serviceId,
                quantity: 1, // Default quantity
                service_address: address,
                scheduled_date: date,
                scheduled_time: time,
                notes: note
            };

            await API.createOrder(orderData); // Assuming API.createOrder exists

            // Hide booking modal
            const bookingModalEl = document.getElementById('bookingModal');
            bootstrap.Modal.getInstance(bookingModalEl).hide();

            // Show success modal
            const successModal = new bootstrap.Modal(document.getElementById('bookingSuccessModal'));
            successModal.show();

            // Reset form
            document.getElementById('bookingForm').reset();

        } catch (error) {
            this.showAlert(error.message || 'Có lỗi xảy ra khi đặt dịch vụ', 'danger');
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    },

    showAlert: function (message, type) {
        const container = document.getElementById('bookingAlertContainer');
        container.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    },

    formatCurrency: function (amount) {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    BookingManager.init();
});
