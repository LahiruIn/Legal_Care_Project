document.addEventListener('DOMContentLoaded', function () {
  // Elements
  const weekdayCard = document.getElementById('weekdayCard');
  const weekendCard = document.getElementById('weekendCard');
  const weekdayCheckbox = document.getElementById('weekdays');
  const weekendCheckbox = document.getElementById('weekend');

  const weekdayDaySelection = document.getElementById('weekday-day-selection');
  const weekendDaySelection = document.getElementById('weekend-day-selection');

  const weekdayAvailability = document.getElementById('weekday-availability');
  const weekendAvailability = document.getElementById('weekend-availability');

  // Helper: Toggle availability section visibility
  function toggleAvailability(type, isChecked) {
    const card = document.getElementById(`${type}Card`);
    const daySelection = document.getElementById(`${type}-day-selection`);
    const timeSlot = document.getElementById(`${type}-availability`);

    if (!card || !daySelection || !timeSlot) return;

    if (isChecked) {
      card.classList.add('selected');
      daySelection.classList.add('active');
      timeSlot.classList.add('active');
      daySelection.style.display = 'block';
      timeSlot.style.display = 'block';
    } else {
      card.classList.remove('selected');
      daySelection.classList.remove('active');
      timeSlot.classList.remove('active');
      daySelection.style.display = 'none';
      timeSlot.style.display = 'none';

      // Clear all related checkboxes
      document.querySelectorAll(`input[name="${type}_days[]"]`).forEach(el => el.checked = false);
      document.querySelectorAll(`input[name="${type}_time"]`).forEach(el => el.checked = false);
    }
  }

  // Click handlers for cards (toggle checkbox + availability UI)
  if (weekdayCard && weekdayCheckbox) {
    weekdayCard.addEventListener('click', () => {
      weekdayCheckbox.checked = !weekdayCheckbox.checked;
      toggleAvailability('weekday', weekdayCheckbox.checked);
    });
  }

  if (weekendCard && weekendCheckbox) {
    weekendCard.addEventListener('click', () => {
      weekendCheckbox.checked = !weekendCheckbox.checked;
      toggleAvailability('weekend', weekendCheckbox.checked);
    });
  }

  // On load: restore UI based on checkbox state (used in update/edit mode)
  toggleAvailability('weekday', weekdayCheckbox?.checked);
  toggleAvailability('weekend', weekendCheckbox?.checked);

  // Status toggle
  const statusToggle = document.querySelector('input[name="status"]');
  const statusText = document.getElementById('statusText');

  if (statusToggle && statusText) {
    // Set initial text on load
    if (statusToggle.checked) {
      statusText.textContent = 'Active';
      statusText.classList.add('status-active');
      statusText.classList.remove('status-inactive');
    } else {
      statusText.textContent = 'Inactive';
      statusText.classList.add('status-inactive');
      statusText.classList.remove('status-active');
    }

    // Listen for changes
    statusToggle.addEventListener('change', function () {
      if (this.checked) {
        statusText.textContent = 'Active';
        statusText.classList.add('status-active');
        statusText.classList.remove('status-inactive');
      } else {
        statusText.textContent = 'Inactive';
        statusText.classList.add('status-inactive');
        statusText.classList.remove('status-active');
      }
    });
  }
});
