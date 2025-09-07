        // Navigation scroll effect
        function handleScrollEffect() {
            const header = document.getElementById('header');
            const scrollY = window.scrollY;
            
            if (scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }

        // Mobile menu toggle
        function initMobileMenu() {
            const mobileMenuBtn = document.getElementById('mobileMenuBtn');
            const mobileMenu = document.getElementById('mobileMenu');
            const body = document.body;
            
            mobileMenuBtn.addEventListener('click', function() {
                const isActive = mobileMenu.classList.contains('active');
                
                if (isActive) {
                    // Close menu
                    mobileMenu.classList.remove('active');
                    mobileMenuBtn.classList.remove('active');
                    body.style.overflow = '';
                    
                    // Change icon back to hamburger
                    const icon = mobileMenuBtn.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                } else {
                    // Open menu
                    mobileMenu.classList.add('active');
                    mobileMenuBtn.classList.add('active');
                    body.style.overflow = 'hidden';
                    
                    // Change icon to close
                    const icon = mobileMenuBtn.querySelector('i');
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                }
            });

            // Close mobile menu when clicking on links
            const mobileNavLinks = mobileMenu.querySelectorAll('.mobile-nav a');
            mobileNavLinks.forEach(link => {
                link.addEventListener('click', () => {
                    mobileMenu.classList.remove('active');
                    mobileMenuBtn.classList.remove('active');
                    body.style.overflow = '';
                    
                    const icon = mobileMenuBtn.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                });
            });

            // Close mobile menu on window resize
            window.addEventListener('resize', () => {
                if (window.innerWidth > 768) {
                    mobileMenu.classList.remove('active');
                    mobileMenuBtn.classList.remove('active');
                    body.style.overflow = '';
                    
                    const icon = mobileMenuBtn.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            });
        }

        // Active nav link management
        function initNavigation() {
            const navLinks = document.querySelectorAll('.nav-links a, .mobile-nav a');
            
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Remove active class from all links
                    navLinks.forEach(l => l.classList.remove('active'));
                    
                    // Add active class to clicked link
                    this.classList.add('active');
                    
                    // For demo purposes, you would normally navigate here
                    console.log('Navigating to:', this.textContent);
                });
            });
        }

        // Smooth scrolling for anchor links
        function initSmoothScroll() {
            const links = document.querySelectorAll('a[href^="#"]');
            
            links.forEach(link => {
                link.addEventListener('click', function(e) {
                    const href = this.getAttribute('href');
                    if (href === '#') return;
                    
                    e.preventDefault();
                    const target = document.querySelector(href);
                    
                    if (target) {
                        const headerHeight = document.querySelector('.header').offsetHeight;
                        const targetPosition = target.offsetTop - headerHeight;
                        
                        window.scrollTo({
                            top: targetPosition,
                            behavior: 'smooth'
                        });
                    }
                });
            });
        }

        // Button ripple effect
        function initButtonEffects() {
            const buttons = document.querySelectorAll('.btn');
            
            buttons.forEach(button => {
                button.addEventListener('click', function(e) {
                    const ripple = document.createElement('span');
                    const rect = this.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size / 2;
                    const y = e.clientY - rect.top - size / 2;
                    
                    ripple.style.cssText = `
                        position: absolute;
                        width: ${size}px;
                        height: ${size}px;
                        left: ${x}px;
                        top: ${y}px;
                        background: rgba(255, 255, 255, 0.3);
                        border-radius: 50%;
                        transform: scale(0);
                        animation: ripple-animation 0.6s linear;
                        pointer-events: none;
                    `;
                    
                    this.appendChild(ripple);
                    
                    setTimeout(() => {
                        ripple.remove();
                    }, 600);
                });
            });
        }

        // Dropdown menu management
        function initDropdowns() {
            const dropdownItems = document.querySelectorAll('.nav-item');
            
            dropdownItems.forEach(item => {
                const dropdown = item.querySelector('.dropdown');
                let timeout;
                
                item.addEventListener('mouseenter', () => {
                    clearTimeout(timeout);
                    dropdown.style.display = 'block';
                });
                
                item.addEventListener('mouseleave', () => {
                    timeout = setTimeout(() => {
                        dropdown.style.display = 'none';
                    }, 100);
                });
            });
        }

        // Initialize everything when DOM is loaded
        document.addEventListener('DOMContentLoaded', function() {
            initMobileMenu();
            initNavigation();
            initSmoothScroll();
            initButtonEffects();
            initDropdowns();
            
            // Add scroll listener
            window.addEventListener('scroll', handleScrollEffect);
            
            // Initial call to set header state
            handleScrollEffect();
        });

        // Add ripple animation CSS
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple-animation {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
