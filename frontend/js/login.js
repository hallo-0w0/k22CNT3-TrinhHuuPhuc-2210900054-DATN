/**
 * Login Page Script
 */

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const alertContainer = document.getElementById('alertContainer');
    const registerForm = document.getElementById('registerForm');
    const goRegister = document.getElementById('goRegister');
    const goLogin = document.getElementById('goLogin');
    
    // Nếu đã đăng nhập, redirect
    if (isAuthenticated()) {
        redirectByRole(getUserRole());
        return;
    }

    // Nếu đang ở index.html#auth thì tự mở modal đăng nhập
    try {
        if (window.location.hash === '#auth') {
            const modalEl = document.getElementById('authModal');
            if (modalEl && window.bootstrap?.Modal) {
                const modal = window.bootstrap.Modal.getOrCreateInstance(modalEl);
                modal.show();
            }
        }
    } catch (_) {}

    function showAlert(message, type = 'danger') {
        alertContainer.innerHTML = '';
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        alertContainer.appendChild(alert);
    }

    // Switch tabs helper
    function switchTo(tabId) {
        const btn = document.getElementById(tabId);
        if (btn) btn.click();
    }

    if (goRegister) {
        goRegister.addEventListener('click', (e) => {
            e.preventDefault();
            switchTo('tab-register');
        });
    }
    if (goLogin) {
        goLogin.addEventListener('click', (e) => {
            e.preventDefault();
            switchTo('tab-login');
        });
    }
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Clear previous alerts
        alertContainer.innerHTML = '';
        
        // Show loading
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Đang đăng nhập...';
        
        try {
            const response = await API.login(email, password);
            console.log('Login response:', response);
            
            // Lưu token
            if (response.access_token) {
                localStorage.setItem('access_token', response.access_token);
                console.log('Token saved to localStorage');
            } else {
                console.error('No access_token in response');
                throw new Error('Không nhận được token từ server');
            }
            
            if (response.role) {
                localStorage.setItem('user_role', response.role);
                console.log('Role saved:', response.role);
            } else {
                console.error('No role in response');
            }
            
            // Redirect theo role
            console.log('Redirecting with role:', response.role);
            redirectByRole(response.role);
            
        } catch (error) {
            console.error('Login error:', error);
            showAlert(error.message || 'Đăng nhập thất bại', 'danger');
            
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });

    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            alertContainer.innerHTML = '';

            const payload = {
                register_type: document.getElementById('registerType').value,
                full_name: document.getElementById('regFullName').value.trim(),
                username: document.getElementById('regUsername').value.trim(),
                email: document.getElementById('regEmail').value.trim(),
                password: document.getElementById('regPassword').value,
                phone_number: document.getElementById('regPhone').value.trim(),
                address: document.getElementById('regAddress').value.trim(),
            };

            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Đang tạo tài khoản...';

            try {
                const result = await API.register(payload);
                showAlert('Đăng ký thành công! Đang tự động đăng nhập...', 'success');
                
                // Tự động đăng nhập sau khi đăng ký thành công
                try {
                    const loginResponse = await API.login(payload.email, payload.password);
                    
                    // Lưu token
                    localStorage.setItem('access_token', loginResponse.access_token);
                    localStorage.setItem('user_role', loginResponse.role);
                    
                    // Đóng modal nếu có
                    const modalEl = document.getElementById('authModal');
                    if (modalEl && window.bootstrap?.Modal) {
                        const modal = window.bootstrap.Modal.getInstance(modalEl);
                        if (modal) modal.hide();
                    }
                    
                    // Redirect theo role
                    setTimeout(() => {
                        redirectByRole(loginResponse.role);
                    }, 500);
                    
                } catch (loginError) {
                    // Nếu tự động đăng nhập thất bại, chuyển sang tab login
                    showAlert('Đăng ký thành công! Vui lòng đăng nhập thủ công.', 'success');
                    const loginEmail = document.getElementById('email');
                    if (loginEmail) loginEmail.value = payload.email;
                    switchTo('tab-login');
                }
            } catch (error) {
                showAlert(error.message || 'Đăng ký thất bại', 'danger');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
});
