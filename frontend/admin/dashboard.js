// Dashboard functionality

// Check authentication
if (!requireAuth()) {
    // Redirect handled in requireAuth
}

// Load user info
const user = API.getUser();
if (user) {
    document.getElementById('userName').textContent = user.full_name || user.username;
}

// Toggle sidebar on mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('show');
}

// Logout function
async function logout() {
    try {
        await API.post(API_CONFIG.ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        API.removeToken();
        window.location.href = '/admin/login.html';
    }
}

// Load dashboard stats
async function loadDashboardStats() {
    try {
        const stats = await API.get(API_CONFIG.ENDPOINTS.DASHBOARD);
        
        // Update stat cards
        const totalUsers = Object.values(stats.users_by_role || {}).reduce((a, b) => a + b, 0);
        document.getElementById('totalUsers').textContent = totalUsers.toLocaleString('vi-VN');
        
        const totalOrders = Object.values(stats.orders_by_status || {}).reduce((a, b) => a + b, 0);
        document.getElementById('totalOrders').textContent = totalOrders.toLocaleString('vi-VN');
        
        const revenue = stats.total_revenue || 0;
        document.getElementById('totalRevenue').textContent = new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(revenue);
        
        const avgRating = stats.average_rating || 0;
        document.getElementById('avgRating').textContent = avgRating.toFixed(1);
        
        // Create charts
        createOrdersChart(stats.orders_by_status || {});
        createUsersChart(stats.users_by_role || {});
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        showError('Không thể tải thống kê. Vui lòng thử lại.');
    }
}

// Create orders chart
function createOrdersChart(data) {
    const ctx = document.getElementById('ordersChart').getContext('2d');
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    const colors = [
        'rgba(59, 130, 246, 0.8)',  // Blue
        'rgba(16, 185, 129, 0.8)',  // Green
        'rgba(245, 158, 11, 0.8)',   // Yellow
        'rgba(239, 68, 68, 0.8)',    // Red
        'rgba(139, 92, 246, 0.8)'    // Purple
    ];
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Create users chart
function createUsersChart(data) {
    const ctx = document.getElementById('usersChart').getContext('2d');
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    const colors = [
        'rgba(59, 130, 246, 0.8)',  // Blue - CUSTOMER
        'rgba(16, 185, 129, 0.8)',  // Green - STAFF
        'rgba(245, 158, 11, 0.8)',   // Yellow - ADMIN
    ];
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Số lượng',
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.slice(0, labels.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Show error message
function showError(message) {
    // You can implement a toast notification here
    alert(message);
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
    
    // Set active menu item
    const currentPage = window.location.pathname;
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
});
