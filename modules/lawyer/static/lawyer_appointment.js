        document.addEventListener('DOMContentLoaded', function() {
            const flashMessages = document.querySelectorAll('.flash');
            flashMessages.forEach(function(flash) {
                setTimeout(function() {
                    flash.style.opacity = '0';
                    flash.style.transform = 'translateY(-20px)';
                    setTimeout(function() {
                        flash.remove();
                    }, 300);
                }, 5000);
            });

            // Add loading state to filter button
            const filterForm = document.querySelector('.filters-form');
            if (filterForm) {
                filterForm.addEventListener('submit', function() {
                    const filterBtn = filterForm.querySelector('.filter-btn');
                    filterBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Filtering...';
                    filterBtn.disabled = true;
                });
            }

            // Add loading state to action buttons
            const actionForms = document.querySelectorAll('.action-form');
            actionForms.forEach(function(form) {
                form.addEventListener('submit', function(e) {
                    const button = form.querySelector('.action-btn');
                    const originalContent = button.innerHTML;
                    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                    button.disabled = true;

                    // Re-enable button after 2 seconds in case of network issues
                    setTimeout(function() {
                        button.innerHTML = originalContent;
                        button.disabled = false;
                    }, 2000);
                });
            });

            // Enhanced table row hover effects
            const tableRows = document.querySelectorAll('tbody tr');
            tableRows.forEach(function(row) {
                row.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateX(2px)';
                    this.style.transition = 'all 0.2s ease';
                });
                
                row.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateX(0)';
                });
            });

            // Status badge animation on load
            const statusBadges = document.querySelectorAll('.status-badge');
            statusBadges.forEach(function(badge, index) {
                badge.style.opacity = '0';
                badge.style.transform = 'scale(0.8)';
                setTimeout(function() {
                    badge.style.transition = 'all 0.3s ease';
                    badge.style.opacity = '1';
                    badge.style.transform = 'scale(1)';
                }, index * 50);
            });

            // Smooth scrolling for long tables
            const tableContainer = document.querySelector('.table-container');
            if (tableContainer) {
                tableContainer.style.scrollBehavior = 'smooth';
            }

            // Dynamic stats update animation
            const statNumbers = document.querySelectorAll('.stat-number');
            statNumbers.forEach(function(stat) {
                const finalValue = parseInt(stat.textContent);
                let currentValue = 0;
                const increment = finalValue / 20;
                const timer = setInterval(function() {
                    currentValue += increment;
                    if (currentValue >= finalValue) {
                        currentValue = finalValue;
                        clearInterval(timer);
                    }
                    stat.textContent = Math.floor(currentValue);
                }, 50);
            });
        });

        // Enhanced confirmation dialog for delete actions
        function confirmDelete(appointmentId, userName) {
            return confirm(`Are you sure you want to delete the appointment for ${userName}? This action cannot be undone.`);
        }

        // Status change confirmation
        function confirmStatusChange(newStatus, userName) {
            const statusMessages = {
                'confirmed': 'confirm',
                'done': 'mark as completed',
                'cancelled': 'cancel',
                'pending': 'mark as pending'
            };
            
            const action = statusMessages[newStatus] || 'update';
            return confirm(`Are you sure you want to ${action} the appointment for ${userName}?`);
        }

        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + F to focus search input
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                const searchInput = document.querySelector('input[name="q"]');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
            
            // Escape to clear filters
            if (e.key === 'Escape') {
                const form = document.querySelector('.filters-form');
                if (form) {
                    form.reset();
                    const searchInput = form.querySelector('input[name="q"]');
                    if (searchInput) {
                        searchInput.blur();
                    }
                }
            }
        });

        // Real-time search functionality
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                const searchTerm = this.value.toLowerCase().trim();
                
                searchTimeout = setTimeout(function() {
                    const rows = document.querySelectorAll('tbody tr:not(:first-child)');
                    
                    rows.forEach(function(row) {
                        const text = row.textContent.toLowerCase();
                        const shouldShow = !searchTerm || text.includes(searchTerm);
                        
                        if (shouldShow) {
                            row.style.display = '';
                            row.style.animation = 'fadeIn 0.3s ease';
                        } else {
                            row.style.display = 'none';
                        }
                    });
                    
                    // Update empty state visibility
                    const visibleRows = document.querySelectorAll('tbody tr:not([style*="display: none"]):not(:first-child)');
                    const emptyState = document.querySelector('.empty-state');
                    if (emptyState && visibleRows.length === 0 && searchTerm) {
                        emptyState.parentElement.parentElement.style.display = '';
                        emptyState.querySelector('h3').textContent = 'No matching appointments';
                        emptyState.querySelector('p').textContent = `No appointments match "${searchTerm}".`;
                    }
                }, 300);
            });
        }

        // Add print functionality
        function printTable() {
            window.print();
        }

        // Add export functionality placeholder
        function exportData() {
            alert('Export functionality would be implemented here with your backend.');
        }

        // Enhanced responsive table handling
        function handleResponsiveTable() {
            const table = document.querySelector('table');
            const container = document.querySelector('.table-container');
            
            if (table && container) {
                const containerWidth = container.offsetWidth;
                const tableWidth = table.offsetWidth;
                
                if (tableWidth > containerWidth) {
                    container.style.overflowX = 'auto';
                    container.style.paddingBottom = '10px';
                    
                    // Add scroll indicator for mobile
                    if (window.innerWidth <= 768) {
                        container.setAttribute('title', 'Scroll horizontally to see more columns');
                    }
                } else {
                    container.style.overflowX = 'visible';
                    container.style.paddingBottom = '0';
                }
            }
        }

        // Mobile touch improvements
        function initMobileOptimizations() {
            if (window.innerWidth <= 768) {
                // Add touch-friendly classes
                document.body.classList.add('mobile-view');
                
                // Improve button touch targets
                const buttons = document.querySelectorAll('.action-btn');
                buttons.forEach(btn => {
                    btn.style.minHeight = '44px';
                    btn.style.minWidth = '44px';
                });
                
                // Add swipe indicator for table
                const tableContainer = document.querySelector('.table-container');
                if (tableContainer && !document.querySelector('.scroll-indicator')) {
                    const indicator = document.createElement('div');
                    indicator.className = 'scroll-indicator';
                    indicator.innerHTML = '<i class="fas fa-arrows-alt-h"></i> Swipe to scroll';
                    indicator.style.cssText = `
                        position: absolute;
                        top: 10px;
                        right: 10px;
                        background: rgba(59, 130, 246, 0.9);
                        color: white;
                        padding: 5px 10px;
                        border-radius: 15px;
                        font-size: 11px;
                        z-index: 100;
                        animation: fadeOut 3s ease-out forwards;
                    `;
                    tableContainer.style.position = 'relative';
                    tableContainer.appendChild(indicator);
                    
                    // Add fadeOut animation
                    const style = document.createElement('style');
                    style.textContent = `
                        @keyframes fadeOut {
                            0%, 70% { opacity: 1; }
                            100% { opacity: 0; visibility: hidden; }
                        }
                    `;
                    document.head.appendChild(style);
                }
                
                // Improve form inputs for mobile
                const inputs = document.querySelectorAll('.form-input, .form-select');
                inputs.forEach(input => {
                    input.addEventListener('focus', function() {
                        // Prevent zoom on iOS
                        if (this.style.fontSize === '') {
                            this.style.fontSize = '16px';
                        }
                    });
                });
            }
        }

        // Handle window resize with debouncing
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                handleResponsiveTable();
                initMobileOptimizations();
            }, 250);
        });
        
        window.addEventListener('load', function() {
            handleResponsiveTable();
            initMobileOptimizations();
        });
