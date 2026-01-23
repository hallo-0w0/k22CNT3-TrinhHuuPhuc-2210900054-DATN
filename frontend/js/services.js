/**
 * Services Page Script
 */

let allServices = [];
let categories = [];

document.addEventListener('DOMContentLoaded', async function () {
    // Load data
    try {
        await Promise.all([
            loadCategories(),
            loadServices()
        ]);
    } catch (error) {
        console.error('Error loading data:', error);
    }

    // Setup search listener
    const searchInput = document.getElementById('serviceSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filterAndDisplayServices(e.target.value);
        });
    }
});

async function loadCategories() {
    try {
        categories = await API.getCategories();
    } catch (error) {
        console.warn('Could not load categories, grouping might be limited', error);
    }
}

async function loadServices() {
    try {
        allServices = await API.getServices();
        displayGroupedServices(allServices);
    } catch (error) {
        console.error('Error loading services:', error);
        document.getElementById('servicesList').innerHTML =
            '<div class="col-12 text-center text-danger">Không thể tải danh sách dịch vụ. Vui lòng thử lại sau.</div>';
    }
}

function filterAndDisplayServices(keyword) {
    const term = keyword.toLowerCase().trim();

    if (!term) {
        displayGroupedServices(allServices);
        return;
    }

    const filtered = allServices.filter(s =>
        s.service_name.toLowerCase().includes(term) ||
        (s.service_description && s.service_description.toLowerCase().includes(term))
    );

    displayGroupedServices(filtered, true); // true = force list view if searching? Or still grouped?
    // Let's keep grouped view even when searching, but filter items within groups
}

function displayGroupedServices(services) {
    const container = document.getElementById('servicesList');
    if (!container) return;

    if (services.length === 0) {
        container.innerHTML = '<div class="col-12 py-5"><p class="text-center text-muted fs-5">Không tìm thấy dịch vụ nào phù hợp.</p></div>';
        return;
    }

    // Group services by category
    const groups = {};

    // Initialize groups from categories list to ensure order (optional) and correct names
    categories.forEach(cat => {
        groups[cat.category_id] = {
            name: cat.category_name,
            items: []
        };
    });

    // Add 'Other/Uncategorized' group
    groups['other'] = { name: 'Dịch vụ khác', items: [] };

    // Distribute services
    services.forEach(s => {
        const catId = s.category_id;
        if (catId && groups[catId]) {
            groups[catId].items.push(s);
        } else {
            groups['other'].items.push(s);
        }
    });

    // Render groups
    let html = '';

    // Helper to render a grid of services
    const renderServiceGrid = (items) => {
        return items.map(service => `
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
                            ${service.service_description || 'Dịch vụ vệ sinh chuyên nghiệp.'}
                        </p>
                        <div class="d-flex align-items-center justify-content-between mt-3 pt-3 border-top">
                            <span class="text-muted small">
                                <i class="bi bi-tag-fill me-1"></i> ${service.unit ? `${service.unit}` : 'Trọn gói'}
                            </span>
                             <span class="text-muted small">
                                <i class="bi bi-clock me-1"></i> ${service.duration_hours ? `${service.duration_hours}h` : '--'}
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
    };

    // Iterate over groups and build HTML
    // Use categories array to determine order
    const processedCatIds = new Set();

    categories.forEach(cat => {
        const group = groups[cat.category_id];
        if (group && group.items.length > 0) {
            html += `
                <div class="col-12 mb-4 mt-2">
                    <div class="d-flex align-items-center mb-3">
                        <h3 class="fw-bold text-primary mb-0 me-3">${group.name}</h3>
                        <div class="flex-grow-1 border-bottom"></div>
                    </div>
                    <div class="row">
                        ${renderServiceGrid(group.items)}
                    </div>
                </div>
            `;
            processedCatIds.add(cat.category_id);
        }
    });

    // Handle any leftovers in groups that weren't in categories list (edge case) or 'other'
    for (const [key, group] of Object.entries(groups)) {
        if (!processedCatIds.has(Number(key)) && key !== 'other' && group.items.length > 0) {
            html += `
                <div class="col-12 mb-4 mt-2">
                    <div class="d-flex align-items-center mb-3">
                        <h3 class="fw-bold text-primary mb-0 me-3">${group.name}</h3>
                        <div class="flex-grow-1 border-bottom"></div>
                    </div>
                    <div class="row">
                        ${renderServiceGrid(group.items)}
                    </div>
                </div>
            `;
        }
    }

    // Handle 'Other' group
    if (groups['other'].items.length > 0) {
        html += `
            <div class="col-12 mb-4 mt-2">
                <div class="d-flex align-items-center mb-3">
                    <h3 class="fw-bold text-secondary mb-0 me-3">Dịch vụ khác</h3>
                    <div class="flex-grow-1 border-bottom"></div>
                </div>
                <div class="row">
                    ${renderServiceGrid(groups['other'].items)}
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

function handleServiceClick(event, serviceId) {
    event.preventDefault();
    if (typeof BookingManager !== 'undefined') {
        BookingManager.openModal(serviceId);
    } else {
        // Fallback or alert
        alert('Vui lòng đăng nhập để đặt dịch vụ!');
        // Or redirect to login
        // window.location.href = '#auth';
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}
