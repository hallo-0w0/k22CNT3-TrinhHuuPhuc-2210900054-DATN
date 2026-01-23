/**
 * API Configuration và Helper Functions
 */
const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Lấy token từ localStorage
 */
function getToken() {
    return localStorage.getItem('access_token');
}

/**
 * Lấy headers với token
 */
function getHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    } else {
        console.warn('No token found in localStorage');
    }
    
    return headers;
}

/**
 * API Request Helper
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config = {
        ...options,
        headers: {
            ...getHeaders(),
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, config);
        
        // Kiểm tra nếu response không phải JSON
        const contentType = response.headers.get('content-type');
        let data;
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        
        if (!response.ok) {
            // Lưu status code vào error để xử lý sau
            const errorMessage = data.error || data.message || `HTTP ${response.status}: ${response.statusText}`;
            const error = new Error(errorMessage);
            error.status = response.status;
            error.data = data;
            
            // Log chi tiết lỗi
            console.error(`API Error [${response.status}]:`, {
                url: url,
                status: response.status,
                error: errorMessage,
                data: data
            });
            
            // Nếu là lỗi 401 hoặc 422, có thể token không hợp lệ
            if (response.status === 401 || response.status === 422) {
                console.warn('Authentication error - token may be invalid');
                // Nếu đang ở trang admin và token không hợp lệ, xóa token
                if (window.location.pathname.includes('/admin/')) {
                    console.warn('Admin page with invalid token, will redirect');
                }
            }
            
            throw error;
        }
        
        return data;
    } catch (error) {
        console.error('API Request Error:', {
            url: url,
            error: error.message,
            status: error.status
        });
        // Nếu là lỗi network (không có response), thêm status 0
        if (!error.status) {
            error.status = 0;
        }
        throw error;
    }
}

/**
 * API Methods
 */
const API = {
    // Auth
    login: (email, password) => {
        return apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },

    register: (payload) => {
        return apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },
    
    getCurrentUser: () => {
        return apiRequest('/auth/me');
    },
    
    logout: () => {
        return apiRequest('/auth/logout', {
            method: 'POST'
        });
    },
    
    // Services
    getServices: (categoryId = null) => {
        const params = categoryId ? `?category_id=${categoryId}` : '';
        return apiRequest(`/services${params}`);
    },
    
    getService: (serviceId) => {
        return apiRequest(`/services/${serviceId}`);
    },
    
    getCategories: () => {
        return apiRequest('/services/categories');
    },
    
    // Orders
    getOrders: (statusId = null) => {
        const params = statusId ? `?status_id=${statusId}` : '';
        return apiRequest(`/orders${params}`);
    },
    
    createOrder: (orderData) => {
        return apiRequest('/orders', {
            method: 'POST',
            body: JSON.stringify(orderData)
        });
    },
    
    getOrder: (orderId) => {
        return apiRequest(`/orders/${orderId}`);
    },
    
    updateOrderStatus: (orderId, statusCode, reason = null) => {
        return apiRequest(`/orders/${orderId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status_code: statusCode, reason })
        });
    },
    
    addProgress: (orderId, progressData) => {
        return apiRequest(`/orders/${orderId}/progress`, {
            method: 'POST',
            body: JSON.stringify(progressData)
        });
    },
    
    getProgress: (orderId) => {
        return apiRequest(`/orders/${orderId}/progress`);
    },
    
    // Content
    getContent: (contentType) => {
        return apiRequest(`/content/${contentType}`);
    },
    
    // Admin APIs
    // Dashboard
    getDashboardStats: () => {
        return apiRequest('/admin/dashboard/stats');
    },
    
    // Admin Services
    adminGetServices: () => {
        return apiRequest('/admin/services');
    },
    
    adminCreateService: (serviceData) => {
        return apiRequest('/admin/services', {
            method: 'POST',
            body: JSON.stringify(serviceData)
        });
    },
    
    adminGetService: (serviceId) => {
        return apiRequest(`/admin/services/${serviceId}`);
    },
    
    adminUpdateService: (serviceId, serviceData) => {
        return apiRequest(`/admin/services/${serviceId}`, {
            method: 'PUT',
            body: JSON.stringify(serviceData)
        });
    },
    
    adminDeleteService: (serviceId) => {
        return apiRequest(`/admin/services/${serviceId}`, {
            method: 'DELETE'
        });
    },
    
    // Admin Categories
    adminGetCategories: () => {
        return apiRequest('/admin/categories');
    },
    
    adminCreateCategory: (categoryData) => {
        return apiRequest('/admin/categories', {
            method: 'POST',
            body: JSON.stringify(categoryData)
        });
    },
    
    adminUpdateCategory: (categoryId, categoryData) => {
        return apiRequest(`/admin/categories/${categoryId}`, {
            method: 'PUT',
            body: JSON.stringify(categoryData)
        });
    },
    
    adminDeleteCategory: (categoryId) => {
        return apiRequest(`/admin/categories/${categoryId}`, {
            method: 'DELETE'
        });
    },
    
    // Admin Users
    adminGetUsers: (role = null) => {
        const params = role ? `?role=${role}` : '';
        return apiRequest(`/admin/users${params}`);
    },
    
    adminGetUser: (userId) => {
        return apiRequest(`/admin/users/${userId}`);
    },
    
    adminUpdateUserStatus: (userId, statusData) => {
        return apiRequest(`/admin/users/${userId}/status`, {
            method: 'PUT',
            body: JSON.stringify(statusData)
        });
    },
    
    // Admin Staff
    adminGetStaff: () => {
        return apiRequest('/admin/staff');
    },
    
    // Admin Orders
    adminAssignOrder: (orderId, assignmentData) => {
        return apiRequest(`/admin/orders/${orderId}/assign`, {
            method: 'POST',
            body: JSON.stringify(assignmentData)
        });
    },
    
    // Admin Content
    adminGetContent: (contentType = null) => {
        const params = contentType ? `?content_type=${contentType}` : '';
        return apiRequest(`/admin/content${params}`);
    },
    
    adminCreateContent: (contentData) => {
        return apiRequest('/admin/content', {
            method: 'POST',
            body: JSON.stringify(contentData)
        });
    },
    
    adminUpdateContent: (contentId, contentData) => {
        return apiRequest(`/admin/content/${contentId}`, {
            method: 'PUT',
            body: JSON.stringify(contentData)
        });
    },
    
    adminDeleteContent: (contentId) => {
        return apiRequest(`/admin/content/${contentId}`, {
            method: 'DELETE'
        });
    }
};
