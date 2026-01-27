/**
 * Home Page Script
 */

document.addEventListener('DOMContentLoaded', async function () {
    // Load services
    try {
        const services = await API.getServices();
        displayServices(services);
    } catch (error) {
        console.error('Error loading services:', error);
    }
});

function displayServices(services) {
    const servicesList = document.getElementById('servicesList');

    if (!servicesList) return;

    if (services.length === 0) {
        servicesList.innerHTML = '<div class="col-12"><p class="text-center text-muted">Chưa có dịch vụ nào.</p></div>';
        return;
    }

    // Chỉ hiển thị 3 dịch vụ nổi bật
    const featuredServices = services.slice(0, 3);

    servicesList.innerHTML = featuredServices.map(service => `
        <div class="col-md-4 mb-4">
            <div class="card h-100 border-0 shadow-sm hover-shadow transition-all">
                <div class="position-relative overflow-hidden" style="height: 200px;">
                    <img src="images/services/${service.service_id}.jpg"  
                         class="card-img-top w-100 h-100 object-fit-cover transition-transform" 
                         alt="${service.service_name}"
                         onerror="this.onerror=null; this.src='images/services/1.jpg'">
                    <div class="position-absolute top-0 end-0 m-3">
                         <span class="badge bg-white text-primary shadow-sm px-3 py-2 rounded-pill fw-bold">
                            ${formatCurrency(service.base_price)}
                         </span>
                    </div>
                </div>
                <div class="card-body d-flex flex-column p-4">
                    <h5 class="card-title fw-bold mb-3">${service.service_name}</h5>
                    <p class="card-text text-muted small flex-grow-1 line-clamp-3">
                        ${service.service_description || 'Dịch vụ vệ sinh chuyên nghiệp, đảm bảo sạch sẽ và an toàn cho không gian của bạn.'}
                    </p>
                    <div class="d-flex align-items-center justify-content-between mt-3 pt-3 border-top">
                        <span class="text-muted small">
                            <i class="bi bi-tag-fill me-1"></i> ${service.unit ? `Tính theo ${service.unit}` : 'Trọn gói'}
                        </span>
                    </div>
                </div>
                <div class="card-footer bg-white border-0 p-4 pt-0">
                    <a href="#" class="btn btn-outline-primary w-100 rounded-pill fw-semibold" onclick="handleServiceClick(event, ${service.service_id})">
                        Đặt dịch vụ
                    </a>
                </div>
            </div>
        </div>
    `).join('');
}

function handleServiceClick(event, serviceId) {
    event.preventDefault();
    if (typeof BookingManager !== 'undefined') {
        BookingManager.openModal(serviceId);
    } else {
        console.error('BookingManager is not defined');
        alert('Chức năng đặt dịch vụ đang được cập nhật. Vui lòng thử lại sau.');
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}
