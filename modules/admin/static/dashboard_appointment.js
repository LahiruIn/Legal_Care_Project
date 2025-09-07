    document.addEventListener('DOMContentLoaded', function() {
      // Update stats dynamically when filters are applied
      function updateStats() {
        const rows = document.querySelectorAll('tbody tr');
        let total = 0, pending = 0, confirmed = 0, cancelled = 0, complete = 0;
        
        rows.forEach(row => {
          if (row.style.display !== 'none' && !row.querySelector('.empty-state')) {
            total++;
            const badge = row.querySelector('.badge');
            if (badge) {
              const status = badge.textContent.toLowerCase().trim();
              if (status.includes('pending')) pending++;
              else if (status.includes('confirmed')) confirmed++;
              else if (status.includes('cancelled')) cancelled++;
              else if (status.includes('complete')) complete++;
            }
          }
        });
        
        document.getElementById('total-count').textContent = total;
        document.getElementById('pending-count').textContent = pending;
        document.getElementById('confirmed-count').textContent = confirmed;
        document.getElementById('cancelled-count').textContent = cancelled;
        document.getElementById('complete-count').textContent = complete;
      }
      
      // Call updateStats on page load
      updateStats();
    });
