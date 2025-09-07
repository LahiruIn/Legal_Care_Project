
        // Counter animation for stats
        function animateCounters() {
            const counters = document.querySelectorAll('.stat-number');
            
            counters.forEach(counter => {
                const target = parseInt(counter.textContent.replace(/[^\d]/g, '')); // Extract numbers only
                const isPercentage = counter.textContent.includes('%');
                const hasPlus = counter.textContent.includes('+');
                let current = 0;
                const increment = target / 50; // Animation duration control
                
                const updateCounter = () => {
                    if (current < target) {
                        current += increment;
                        let displayValue = Math.ceil(current);
                        
                        if (isPercentage) {
                            counter.textContent = displayValue + '%';
                        } else if (hasPlus) {
                            counter.textContent = displayValue + '+';
                        } else {
                            counter.textContent = displayValue;
                        }
                        
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.textContent = target + (isPercentage ? '%' : hasPlus ? '+' : '');
                    }
                };
                
                updateCounter();
            });
        }

        // Typewriter effect for headline
        function typewriterEffect() {
            const headline = document.querySelector('.hero-text h1');
            const text = headline.innerHTML;
            headline.innerHTML = '';
            headline.style.opacity = '1';
            
            let i = 0;
            const typeSpeed = 50;
            
            function typeChar() {
                if (i < text.length) {
                    headline.innerHTML += text.charAt(i);
                    i++;
                    setTimeout(typeChar, typeSpeed);
                } else {
                    // Start counter animation after headline is complete
                    setTimeout(animateCounters, 500);
                }
            }
            
            setTimeout(typeChar, 1000); // Start after initial animations
        }

        // Enhanced button interactions
        function initButtonEffects() {
            const buttons = document.querySelectorAll('.btn');
            
            buttons.forEach(button => {
                // Ripple effect
                button.addEventListener('click', function(e) {
                    const ripple = document.createElement('span');
                    const rect = this.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size / 2;
                    const y = e.clientY - rect.top - size / 2;
                    
                    ripple.style.width = ripple.style.height = size + 'px';
                    ripple.style.left = x + 'px';
                    ripple.style.top = y + 'px';
                    ripple.classList.add('ripple');
                    
                    this.appendChild(ripple);
                    
                    setTimeout(() => {
                        ripple.remove();
                    }, 600);
                });

                // Enhanced hover effects
                button.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-3px) scale(1.02)';
                });

                button.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                });
            });
        }

        // Dashboard metrics animation
        function animateDashboardMetrics() {
            const metrics = document.querySelectorAll('.metric-number');
            
            metrics.forEach(metric => {
                const originalText = metric.textContent;
                metric.style.opacity = '0';
                
                setTimeout(() => {
                    metric.style.opacity = '1';
                    metric.style.transform = 'scale(1.2)';
                    
                    setTimeout(() => {
                        metric.style.transform = 'scale(1)';
                    }, 300);
                }, 2000);
            });
        }

        // Parallax effect on scroll
        function initParallax() {
            let ticking = false;
            
            function updateParallax() {
                const scrolled = window.pageYOffset;
                const hero = document.querySelector('.hero');
                const dashboard = document.querySelector('.hero-dashboard');
                
                if (hero) {
                    const rate = scrolled * 0.5;
                    hero.style.transform = `translateY(${rate}px)`;
                }
                
                if (dashboard) {
                    const rate = scrolled * -0.2;
                    dashboard.style.transform = `translateY(${rate}px)`;
                }
                
                ticking = false;
            }
            
            window.addEventListener('scroll', function() {
                if (!ticking) {
                    requestAnimationFrame(updateParallax);
                    ticking = true;
                }
            });
        }

        // Mouse tracking effect (only on larger screens)
        function initMouseTracking() {
            if (window.innerWidth <= 768) return;
            
            const hero = document.querySelector('.hero');
            const dashboard = document.querySelector('.hero-dashboard');
            
            if (!hero || !dashboard) return;
            
            hero.addEventListener('mousemove', function(e) {
                const rect = hero.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / centerY * 5;
                const rotateY = (centerX - x) / centerX * 5;
                
                dashboard.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            });
            
            hero.addEventListener('mouseleave', function() {
                dashboard.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
            });
        }

        // Text glow effect on hover
        function initTextEffects() {
            const highlight = document.querySelector('.highlight');
            
            if (highlight) {
                highlight.addEventListener('mouseenter', function() {
                    this.style.textShadow = '0 0 20px rgba(37, 99, 235, 0.5)';
                    this.style.transition = 'text-shadow 0.3s ease';
                });
                
                highlight.addEventListener('mouseleave', function() {
                    this.style.textShadow = 'none';
                });
            }
        }

        // Status indicator pulse effect
        function initStatusIndicator() {
            const statusIndicator = document.querySelector('.dashboard-status');
            
            if (statusIndicator) {
                const pulseInterval = setInterval(() => {
                    statusIndicator.style.transform = 'scale(1.05)';
                    setTimeout(() => {
                        statusIndicator.style.transform = 'scale(1)';
                    }, 200);
                }, 3000);

                // Store interval ID for cleanup if needed
                window.pulseInterval = pulseInterval;
            }
        }

        // Navigation functionality
        function initNavigation() {
            const navbar = document.querySelector('.navbar');
            const mobileToggle = document.querySelector('.mobile-menu-toggle');
            const mobileMenu = document.querySelector('.mobile-menu');
            const mobileOverlay = document.querySelector('.mobile-overlay');
            const mobileClose = document.querySelector('.mobile-menu-close');
            const navLinks = document.querySelectorAll('.nav-link');

            // Navbar scroll effect
            let scrollTimer = null;
            window.addEventListener('scroll', function() {
                if (scrollTimer) clearTimeout(scrollTimer);
                
                scrollTimer = setTimeout(() => {
                    if (window.scrollY > 50) {
                        navbar.classList.add('scrolled');
                    } else {
                        navbar.classList.remove('scrolled');
                    }
                }, 10);
            });

            // Mobile menu functionality
            function openMobileMenu() {
                mobileMenu.classList.add('active');
                mobileOverlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            }

            function closeMobileMenu() {
                mobileMenu.classList.remove('active');
                mobileOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }

            if (mobileToggle) {
                mobileToggle.addEventListener('click', openMobileMenu);
            }

            if (mobileClose) {
                mobileClose.addEventListener('click', closeMobileMenu);
            }

            if (mobileOverlay) {
                mobileOverlay.addEventListener('click', closeMobileMenu);
            }

            // Close mobile menu on link click
            navLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    closeMobileMenu();
                    
                    // Smooth scroll to section (demo purposes)
                    e.preventDefault();
                    const href = link.getAttribute('href');
                    if (href.startsWith('#') && href !== '#') {
                        const targetSection = document.querySelector(href);
                        if (targetSection) {
                            targetSection.scrollIntoView({ behavior: 'smooth' });
                        }
                    }
                    
                    // Update active state
                    navLinks.forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                });
            });

            // Active link based on scroll position (simplified)
            function updateActiveLink() {
                const scrollPosition = window.scrollY + 100;
                
                if (scrollPosition < window.innerHeight / 2) {
                    navLinks.forEach(link => link.classList.remove('active'));
                    document.querySelector('.nav-link[href="#home"]')?.classList.add('active');
                }
            }

            window.addEventListener('scroll', updateActiveLink);

            // Handle window resize
            window.addEventListener('resize', function() {
                if (window.innerWidth > 768) {
                    closeMobileMenu();
                }
            });

            // Escape key to close mobile menu
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    closeMobileMenu();
                }
            });
        }

        // Initialize everything when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            initNavigation();
            initButtonEffects();
            initParallax();
            initMouseTracking();
            initTextEffects();
            initStatusIndicator();
            
            // Start animations with delays
            setTimeout(() => {
                animateCounters();
            }, 1000);
            
            setTimeout(animateDashboardMetrics, 1500);
        });

        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth <= 768) {
                const dashboard = document.querySelector('.hero-dashboard');
                if (dashboard) {
                    dashboard.style.transform = 'none';
                }
            } else {
                initMouseTracking();  // Reinitialize on larger screens
            }
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {
            if (window.pulseInterval) {
                clearInterval(window.pulseInterval);
            }
        });

