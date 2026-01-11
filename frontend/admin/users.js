// Users Management

let currentPage = 1;
let roles = [];
let memberLevels = [];

// Load roles and member levels
async function loadRoles() {
    try {
        // Get roles from users endpoint or create a roles endpoint
        // For now, we'll use hardcoded roles
        roles = [
            { role_id: 1, role_name: 'CUSTOMER' },
            { role_id: 2, role_name: 'STAFF' },
            { role_id: 3, role_name: 'ADMIN' }
        ];
        
        const roleSelect = document.getElementById('roleId');
        roleSelect.innerHTML = '<option value="">Chọn role...</option>';
        roles.forEach(role => {
            const option = document.createElement('option');
            option.value = role.role_id;
            option.textContent = role.role_name;
            roleSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading roles:', error);
    }
}

async function loadMemberLevels() {
    try {
        const response = await API.get(API_CONFIG.ENDPOINTS.MEMBER_LEVELS);
        memberLevels = response.member_levels || [];
        
        const levelSelect = document.getElementById('memberLevelId');
        levelSelect.innerHTML = '<option value="">Không có</option>';
        memberLevels.forEach(level => {
            const option = document.createElement('option');
            option.value = level.member_level_id;
            option.textContent = `${level.level_name} (${level.discount_percentage}%)`;
            levelSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading member levels:', error);
    }
}

// Load users
async function loadUsers(page = 1) {
    try {
        currentPage = page;
        const search = document.getElementById('searchInput').value;
        const roleFilter = document.getElementById('roleFilter').value;
        const memberLevelFilter = document.getElementById('memberLevelFilter').value;
        
        const params = {
            page: page,
            per_page: 20
        };
        
        if (search) params.search = search;
        if (roleFilter) params.role = roleFilter;
        if (memberLevelFilter) params.member_level = memberLevelFilter;
        
        const response = await API.get(API_CONFIG.ENDPOINTS.USERS, params);
        
        // Update total count
        document.getElementById('totalCount').textContent = response.total || 0;
        
        // Render table
        renderUsersTable(response.items || []);
        
        // Create pagination
        createPagination(response.page, response.pages, loadUsers);
        
    } catch (error) {
        console.error('Error loading users:', error);
        showToast('Không thể tải danh sách users: ' + error.message, 'error');
    }
}

// Render users table
function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">Không có dữ liệu</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.user_id}</td>
            <td>${user.username}</td>
            <td>${user.full_name}</td>
            <td>${user.email}</td>
            <td><span class="badge bg-primary">${user.role_name}</span></td>
            <td>${user.member_level_name ? `<span class="badge bg-warning">${user.member_level_name}</span>` : '-'}</td>
            <td>
                ${user.is_active ? '<span class="badge status-active">Active</span>' : '<span class="badge status-inactive">Inactive</span>'}
                ${user.is_locked ? '<span class="badge status-locked ms-1">Locked</span>' : ''}
            </td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editUser(${user.user_id})">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.user_id}, '${user.username}')">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Show add user modal
function showAddUserModal() {
    document.getElementById('userModalTitle').textContent = 'Thêm User';
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    document.getElementById('passwordRequired').style.display = 'inline';
    document.getElementById('passwordHint').style.display = 'none';
    document.getElementById('password').required = true;
    
    const modal = new bootstrap.Modal(document.getElementById('userModal'));
    modal.show();
}

// Edit user
async function editUser(userId) {
    try {
        const user = await API.get(`${API_CONFIG.ENDPOINTS.USERS}/${userId}`);
        
        document.getElementById('userModalTitle').textContent = 'Sửa User';
        document.getElementById('userId').value = user.user.user_id;
        document.getElementById('username').value = user.user.username;
        document.getElementById('email').value = user.user.email;
        document.getElementById('fullName').value = user.user.full_name;
        document.getElementById('phoneNumber').value = user.user.phone_number || '';
        document.getElementById('address').value = user.user.address || '';
        document.getElementById('roleId').value = user.user.role_id;
        document.getElementById('memberLevelId').value = user.user.member_level_id || '';
        document.getElementById('isActive').checked = user.user.is_active;
        document.getElementById('isLocked').checked = user.user.is_locked;
        
        document.getElementById('passwordRequired').style.display = 'none';
        document.getElementById('passwordHint').style.display = 'inline';
        document.getElementById('password').required = false;
        
        // Update member level options based on role
        updateMemberLevelOptions(user.user.role_name);
        
        const modal = new bootstrap.Modal(document.getElementById('userModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading user:', error);
        showToast('Không thể tải thông tin user: ' + error.message, 'error');
    }
}

// Update member level options based on role
function updateMemberLevelOptions(roleName) {
    const memberLevelSelect = document.getElementById('memberLevelId');
    const roleSelect = document.getElementById('roleId');
    
    roleSelect.addEventListener('change', function() {
        if (this.value && roles.find(r => r.role_id == this.value)?.role_name === 'CUSTOMER') {
            memberLevelSelect.disabled = false;
        } else {
            memberLevelSelect.disabled = true;
            memberLevelSelect.value = '';
        }
    });
}

// Save user
async function saveUser() {
    try {
        const form = document.getElementById('userForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const userId = document.getElementById('userId').value;
        const data = {
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            full_name: document.getElementById('fullName').value,
            phone_number: document.getElementById('phoneNumber').value || null,
            address: document.getElementById('address').value || null,
            role_id: parseInt(document.getElementById('roleId').value),
            member_level_id: document.getElementById('memberLevelId').value || null,
            is_active: document.getElementById('isActive').checked,
            is_locked: document.getElementById('isLocked').checked
        };
        
        const password = document.getElementById('password').value;
        if (password) {
            data.password = password;
        }
        
        if (userId) {
            // Update
            await API.put(`${API_CONFIG.ENDPOINTS.USERS}/${userId}`, data);
            showToast('Cập nhật user thành công!', 'success');
        } else {
            // Create
            await API.post(API_CONFIG.ENDPOINTS.USERS, data);
            showToast('Tạo user thành công!', 'success');
        }
        
        bootstrap.Modal.getInstance(document.getElementById('userModal')).hide();
        loadUsers(currentPage);
        
    } catch (error) {
        console.error('Error saving user:', error);
        showToast('Lỗi: ' + error.message, 'error');
    }
}

// Delete user
async function deleteUser(userId, username) {
    if (!confirm(`Bạn có chắc chắn muốn xóa user "${username}"?`)) {
        return;
    }
    
    try {
        await API.delete(`${API_CONFIG.ENDPOINTS.USERS}/${userId}`);
        showToast('Xóa user thành công!', 'success');
        loadUsers(currentPage);
    } catch (error) {
        console.error('Error deleting user:', error);
        showToast('Lỗi: ' + error.message, 'error');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadRoles();
    loadMemberLevels();
    loadUsers();
    
    // Search on Enter
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            loadUsers(1);
        }
    });
    
    // Update member level options
    updateMemberLevelOptions();
});
