document.addEventListener('DOMContentLoaded', function () {
  // Sidebar toggle
  const sidebar = document.getElementById('sidebar');
  const menuToggle = document.getElementById('menuToggle');
  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }

  // Modal handling
  const addLawyerBtn = document.getElementById('addLawyerBtn');
  const addLawyerModal = document.getElementById('addLawyerModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const cancelAddBtn = document.getElementById('cancelAddBtn');

  function toggleModal() {
    if (addLawyerModal) addLawyerModal.classList.toggle('active');
  }

  if (addLawyerBtn) addLawyerBtn.addEventListener('click', toggleModal);
  if (closeModalBtn) closeModalBtn.addEventListener('click', toggleModal);
  if (cancelAddBtn) cancelAddBtn.addEventListener('click', toggleModal);

  if (addLawyerModal) {
    addLawyerModal.addEventListener('click', function (e) {
      if (e.target === addLawyerModal) toggleModal();
    });
  }

  // Add form simulation (optional)
  const addForm = document.getElementById('addLawyerForm');
  if (addForm) {
    addForm.addEventListener('submit', function (e) {
      e.preventDefault();
      alert('Lawyer added successfully!');
      toggleModal();
      this.reset();
    });
  }

  // Select all checkboxes
  const selectAllCheckbox = document.getElementById('selectAll');
  const rowCheckboxes = document.querySelectorAll('.lawyer-checkbox');
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', function () {
      rowCheckboxes.forEach(cb => cb.checked = this.checked);
    });
  }

  // Filter and search
  const searchInput = document.getElementById('lawyer-search');
  const filterDropdown = document.getElementById('lawyer-filter');

  function filterTable() {
    const searchTerm = searchInput?.value.toLowerCase() || '';
    const filterValue = filterDropdown?.value || 'all';
    const tableRows = document.querySelectorAll('.lawyer-table tbody tr');

    tableRows.forEach(row => {
      const name = row.querySelector('.user-name')?.textContent.toLowerCase() || '';
      const email = row.querySelector('.user-email')?.textContent.toLowerCase() || '';
      const lawyerId = row.children[1]?.textContent.toLowerCase() || '';
      const status = row.getAttribute('data-status');

      const matchesSearch =
        name.includes(searchTerm) ||
        email.includes(searchTerm) ||
        lawyerId.includes(searchTerm);

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
      const lawyerId = this.closest('tr')?.querySelector('td:nth-child(2)')?.textContent || '';
      alert(`Viewing lawyer: ${lawyerId}`);
    });
  });

  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const lawyerId = this.closest('tr')?.querySelector('td:nth-child(2)')?.textContent || '';
      alert(`Editing lawyer: ${lawyerId}`);
    });
  });

  // ✅ DELETE using fetch()
  document.addEventListener('DOMContentLoaded', function () {
  // Attach to all forms that match the delete route
  document.querySelectorAll('form[action*="/dashboard/lawyers/delete/"]').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault(); // Prevent default form submit

      const confirmed = confirm("Are you sure you want to delete this lawyer?");
      if (!confirmed) return;

      const row = this.closest('tr');
      const lawyerName = row?.querySelector('.user-name')?.textContent || 'this lawyer';

      fetch(this.action, {
        method: 'POST'
      })
      .then(res => {
        if (res.ok) {
          row.remove();
          alert(`${lawyerName} deleted.`);
        } else {
          alert("Failed to delete lawyer.");
        }
      })
      .catch(() => {
        alert("Error while deleting lawyer.");
      });
    });
  });
});


  // Update visible stats after delete
  function updateCounts() {
    const totalEl = document.getElementById('visible-lawyers');
    const activeEl = document.getElementById('active-lawyers');
    const inactiveEl = document.getElementById('inactive-lawyers');

    let total = 0;
    let active = 0;
    let inactive = 0;

    document.querySelectorAll('.lawyer-table tbody tr').forEach(row => {
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
