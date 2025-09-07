document.addEventListener('DOMContentLoaded', function() {
    // Enhance the profile view with additional functionality
    
    // Format dates if needed
    const memberSince = document.querySelector('td:contains("Member Since") + td');
    if (memberSince) {
        const date = new Date(memberSince.textContent);
        memberSince.textContent = date.toLocaleDateString('en-US', {
            year: 'numeric', 
            month: 'long', 
            day: 'numeric'
        });
    }
    
    // Add click effect for profile image
    const profileImg = document.querySelector('.profile-image');
    if (profileImg) {
        profileImg.addEventListener('click', function() {
            this.classList.toggle('profile-zoomed');
        });
    }
    
    // Tooltips for action buttons
    $('[data-toggle="tooltip"]').tooltip();
    
    // Smooth scroll for page load
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
    
    // Add confirmation for important actions
    const deleteBtn = document.querySelector('.btn-delete');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this lawyer profile?')) {
                e.preventDefault();
            }
        });
    }
    
    // Format availability days as badges
    const avbDaysCell = document.querySelector('td:contains("Days Available") + td');
    if (avbDaysCell) {
        const days = avbDaysCell.textContent.split(', ');
        avbDaysCell.innerHTML = '';
        days.forEach(day => {
            const badge = document.createElement('span');
            badge.className = 'availability-badge';
            badge.textContent = day.trim();
            avbDaysCell.appendChild(badge);
        });
    }
});