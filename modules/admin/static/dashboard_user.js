document.addEventListener('DOMContentLoaded', function () {
  // Sidebar toggle
  const sidebar = document.getElementById('sidebar');
  const menuToggle = document.getElementById('menuToggle');
  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }

  // Modal handling - Removed since no "Add User" functionality needed

  // Select all checkboxes
  const selectAllCheckbox = document.getElementById('selectAll');
  const rowCheckboxes = document.querySelectorAll('.user-checkbox');
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', function () {
      rowCheckboxes.forEach(cb => cb.checked = this.checked);
    });
  }

  // Filter and search
  const searchInput = document.getElementById('user-search');
  const filterDropdown = document.getElementById('user-filter');

  function filterTable() {
    const searchTerm = searchInput?.value.toLowerCase() || '';
    const filterValue = filterDropdown?.value || 'all';
    const tableRows = document.querySelectorAll('.user-table tbody tr');

    tableRows.forEach(row => {
      const name = row.querySelector('.user-name')?.textContent.toLowerCase() || '';
      const email = row.querySelector('.user-email')?.textContent.toLowerCase() || '';
      const userId = row.children[1]?.textContent.toLowerCase() || ''; // User ID
      const status = row.getAttribute('data-status');

      const matchesSearch =
        name.includes(searchTerm) ||
        email.includes(searchTerm) ||
        userId.includes(searchTerm);

      const matchesFilter =
        filterValue === 'all' ||
        (filterValue === 'active' && status === '1') ||
        (filterValue === 'inactive' && status === '0');

      row.style.display = (matchesSearch && matchesFilter) ? '' : 'none';
    });
  }

  if (searchInput) searchInput.addEventListener('input', filterTable);
  if (filterDropdown) filterDropdown.addEventListener('change', filterTable);

  // View and Edit buttons
  document.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const userId = this.closest('tr')?.querySelector('td:nth-child(2)')?.textContent || '';
      alert(`Viewing user: ${userId}`);
    });
  });

  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const userId = this.closest('tr')?.querySelector('td:nth-child(2)')?.textContent || '';
      alert(`Editing user: ${userId}`);
    });
  });

  // ✅ DELETE using fetch()
  document.addEventListener('DOMContentLoaded', function () {
    // Attach to all forms that match the delete route
    document.querySelectorAll('form[action*="/dashboard/users/delete/"]').forEach(form => {
      form.addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent default form submit

        const confirmed = confirm("Are you sure you want to delete this user?");
        if (!confirmed) return;

        const row = this.closest('tr');
        const userName = row?.querySelector('.user-name')?.textContent || 'this user';

        fetch(this.action, {
          method: 'POST'
        })
        .then(res => {
          if (res.ok) {
            row.remove();
            alert(`${userName} deleted.`);
          } else {
            alert("Failed to delete user.");
          }
        })
        .catch(() => {
          alert("Error while deleting user.");
        });
      });
    });
  });

  // Update visible stats after delete
  function updateCounts() {
    const totalEl = document.getElementById('visible-users');
    let total = 0;
    let active = 0;
    let inactive = 0;

    document.querySelectorAll('.user-table tbody tr').forEach(row => {
      const status = row.getAttribute('data-status');
      if (status === '1') active++;
      else if (status === '0') inactive++;
      total++;
    });

    if (totalEl) totalEl.textContent = total;
    if (activeEl) activeEl.textContent = active;
    if (inactiveEl) inactiveEl.textContent = inactive;
  }

  updateCounts(); // Call on load
});
