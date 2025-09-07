    document.addEventListener('DOMContentLoaded', function() {
      // Add confirmation for delete actions
      const deleteForms = document.querySelectorAll('form[action*="delete"]');
      deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
          if (!confirm('Are you sure you want to delete this content? This action cannot be undone.')) {
            e.preventDefault();
          }
        });
      });
      
      // Enhance filter functionality
      const filterForm = document.querySelector('.filters');
      const filterSelect = filterForm.querySelector('select[name="kind"]');
      const searchInput = filterForm.querySelector('input[name="q"]');
      
      // Save filter state to localStorage
      if (filterSelect.value || searchInput.value) {
        localStorage.setItem('contentFilters', JSON.stringify({
          kind: filterSelect.value,
          q: searchInput.value
        }));
      }
      
      // Load filter state from localStorage
      const savedFilters = localStorage.getItem('contentFilters');
      if (savedFilters) {
        const filters = JSON.parse(savedFilters);
        if (!filterSelect.value) filterSelect.value = filters.kind;
        if (!searchInput.value) searchInput.value = filters.q;
      }
    });
