// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const inputs = form.querySelectorAll('input[required], textarea[required]');
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#f44336';
                } else {
                    input.style.borderColor = '#ddd';
                }
            });

            // Email validation
            const emailInputs = form.querySelectorAll('input[type="email"]');
            emailInputs.forEach(input => {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (input.value && !emailRegex.test(input.value)) {
                    isValid = false;
                    input.style.borderColor = '#f44336';
                }
            });

            // Password validation for register
            if (form.id === 'registerForm') {
                const password = form.querySelector('input[name="password"]');
                const confirmPassword = form.querySelector('input[name="confirmPassword"]');
                if (password && confirmPassword) {
                    if (password.value !== confirmPassword.value) {
                        isValid = false;
                        confirmPassword.style.borderColor = '#f44336';
                        alert('Mật khẩu xác nhận không khớp!');
                    }
                    if (password.value.length < 6) {
                        isValid = false;
                        password.style.borderColor = '#f44336';
                        alert('Mật khẩu phải có ít nhất 6 ký tự!');
                    }
                }
            }

            if (!isValid) {
                e.preventDefault();
                alert('Vui lòng điền đầy đủ thông tin!');
            } else {
                // Simulate form submission
                e.preventDefault();
                alert('Cảm ơn bạn! Thông tin đã được gửi thành công.');
                form.reset();
            }
        });
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.feature-card, .service-card, .pricing-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        observer.observe(card);
    });

    // Mobile menu toggle (if needed)
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
});

