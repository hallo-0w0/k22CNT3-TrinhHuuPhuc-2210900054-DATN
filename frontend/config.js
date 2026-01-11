// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://192.168.0.3:5000/api',
    // BASE_URL: 'http://localhost:5000/api', // Nếu chạy local
    
    // Endpoints
    ENDPOINTS: {
        AUTH: {
            LOGIN: '/auth/login',
            LOGOUT: '/auth/logout',
            ME: '/auth/me',
            REFRESH: '/auth/refresh'
        },
        USERS: '/users',
        SERVICES: '/services',
        ORDERS: '/orders',
        REVIEWS: '/reviews',
        INVOICES: '/invoices',
        CONSULTATIONS: '/consultations',
        MEMBER_LEVELS: '/member-levels',
        DASHBOARD: '/dashboard/stats'
    }
};

// Storage keys
const STORAGE_KEYS = {
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token',
    USER: 'user'
};

// Helper functions
const API = {
    // Get token from localStorage
    getToken: () => {
        return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    },
    
    // Set token
    setToken: (token) => {
        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token);
    },
    
    // Remove token
    removeToken: () => {
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER);
    },
    
    // Get user
    getUser: () => {
        const userStr = localStorage.getItem(STORAGE_KEYS.USER);
        return userStr ? JSON.parse(userStr) : null;
    },
    
    // Set user
    setUser: (user) => {
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    },
    
    // Make API request
    request: async (endpoint, options = {}) => {
        const token = API.getToken();
        const url = `${API_CONFIG.BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }
        
        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired, redirect to login
                    API.removeToken();
                    window.location.href = '/admin/login.html';
                    throw new Error('Phiên đăng nhập đã hết hạn');
                }
                throw new Error(data.message || 'Có lỗi xảy ra');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    // GET request
    get: (endpoint, params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return API.request(url, { method: 'GET' });
    },
    
    // POST request
    post: (endpoint, data) => {
        return API.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    // PUT request
    put: (endpoint, data) => {
        return API.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    // DELETE request
    delete: (endpoint) => {
        return API.request(endpoint, { method: 'DELETE' });
    }
};

// Check if user is admin
const isAdmin = () => {
    const user = API.getUser();
    return user && user.role_name === 'ADMIN';
};

// Check authentication
const checkAuth = () => {
    const token = API.getToken();
    const user = API.getUser();
    
    if (!token || !user) {
        return false;
    }
    
    if (!isAdmin()) {
        return false;
    }
    
    return true;
};

// Redirect to login if not authenticated
const requireAuth = () => {
    if (!checkAuth()) {
        window.location.href = '/admin/login.html';
        return false;
    }
    return true;
};
