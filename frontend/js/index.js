/**
 * Home Page Script
 */

document.addEventListener('DOMContentLoaded', async function() {
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
    
    servicesList.innerHTML = services.map(service => `
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <img src="/images/services/${service.service_id}.jpg" 
                     class="card-img-top" 
                     alt="${service.service_name}"
                     onerror="this.src='https://via.placeholder.com/300x200?text=${encodeURIComponent(service.service_name)}'">
                <div class="card-body">
                    <h5 class="card-title">${service.service_name}</h5>
                    <p class="card-text">${service.service_description || ''}</p>
                    <p class="card-text">
                        <strong class="text-primary">${formatCurrency(service.base_price)}</strong>
                        ${service.unit ? `/ ${service.unit}` : ''}
                    </p>
                </div>
                <div class="card-footer">
                    <a href="services.html?id=${service.service_id}" class="btn btn-primary w-100">Xem chi tiết</a>
                </div>
            </div>
        </div>
    `).join('');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}
