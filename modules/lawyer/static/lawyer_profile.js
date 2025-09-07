    function toggleDay(element) {
      const checkbox = element.querySelector('input[type="checkbox"]');
      checkbox.checked = !checkbox.checked;
      element.classList.toggle('checked', checkbox.checked);
    }

    // Initialize day items and time slots
    document.addEventListener('DOMContentLoaded', function() {
      document.querySelectorAll('.day-item').forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox.checked) {
          item.classList.add('checked');
        }
      });

      // Parse existing availability text and set radio buttons
      const availabilityText = document.getElementById('avb_time_text').value;
      if (availabilityText) {
        parseAvailabilityText(availabilityText);
      }

      // Add event listeners to time slot radio buttons
      document.querySelectorAll('input[name="weekday_slot"], input[name="weekend_slot"]').forEach(radio => {
        radio.addEventListener('change', updateAvailabilityText);
      });

      // File input preview
      const fileInput = document.querySelector('.file-input');
      if (fileInput) {
        fileInput.addEventListener('change', function(e) {
          const file = e.target.files[0];
          if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
              document.querySelector('.avatar').src = e.target.result;
            };
            reader.readAsDataURL(file);
          }
        });
      }
    });

    // Initialize day items and time slots
    document.addEventListener('DOMContentLoaded', function() {
      document.querySelectorAll('.day-item').forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox.checked) {
          item.classList.add('checked');
        }
      });

      // Initialize time slot selection
      initializeTimeSlots();

      // Add event listeners to time slot radio buttons
      document.querySelectorAll('input[name="weekday_slot"], input[name="weekend_slot"]').forEach(radio => {
        radio.addEventListener('change', function() {
          updateTimeSlotStyles();
          updateAvailabilityText();
        });
      });

      // Parse existing availability text and set radio buttons
      const availabilityText = document.getElementById('avb_time_text').value;
      if (availabilityText) {
        parseAvailabilityText(availabilityText);
      }

      // File input preview
      const fileInput = document.querySelector('.file-input');
      if (fileInput) {
        fileInput.addEventListener('change', function(e) {
          const file = e.target.files[0];
          if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
              document.querySelector('.avatar').src = e.target.result;
            };
            reader.readAsDataURL(file);
          }
        });
      }
    });

    function initializeTimeSlots() {
      // Set default selections if none are selected - but independently
      const weekdayChecked = document.querySelector('input[name="weekday_slot"]:checked');
      const weekendChecked = document.querySelector('input[name="weekend_slot"]:checked');
      
      if (!weekdayChecked) {
        document.querySelector('input[name="weekday_slot"][value="morning"]').checked = true;
      }
      
      if (!weekendChecked) {
        document.querySelector('input[name="weekend_slot"][value="morning"]').checked = true;
      }
      
      updateTimeSlotStyles();
      updateAvailabilityText();
    }

    function updateTimeSlotStyles() {
      // Update weekday slots
      document.querySelectorAll('.time-slot-item').forEach(item => {
        const radio = item.querySelector('input[type="radio"]');
        if (radio.checked) {
          item.classList.add('selected');
        } else {
          item.classList.remove('selected');
        }
      });
    }

    function parseAvailabilityText(text) {
      if (!text) return;
      
      const lowerText = text.toLowerCase();
      
      // Parse weekday slots
      if (lowerText.includes('weekdays')) {
        if (lowerText.includes('8:00 am - 12:00 pm') || lowerText.includes('morning')) {
          document.querySelector('input[name="weekday_slot"][value="morning"]').checked = true;
        } else if (lowerText.includes('12:00 pm - 4:00 pm') || lowerText.includes('afternoon')) {
          document.querySelector('input[name="weekday_slot"][value="afternoon"]').checked = true;
        } else if (lowerText.includes('8:00 am - 4:00 pm') || lowerText.includes('full day')) {
          document.querySelector('input[name="weekday_slot"][value="fullday"]').checked = true;
        } else if (lowerText.includes('4:00 pm - 8:00 pm') || lowerText.includes('evening')) {
          document.querySelector('input[name="weekday_slot"][value="evening"]').checked = true;
        }
      }
      
      // Parse weekend slots
      if (lowerText.includes('weekends')) {
        if (lowerText.includes('8:00 am - 12:00 pm') || (lowerText.includes('weekend') && lowerText.includes('morning'))) {
          document.querySelector('input[name="weekend_slot"][value="morning"]').checked = true;
        } else if (lowerText.includes('12:00 pm - 4:00 pm') || (lowerText.includes('weekend') && lowerText.includes('afternoon'))) {
          document.querySelector('input[name="weekend_slot"][value="afternoon"]').checked = true;
        } else if (lowerText.includes('8:00 am - 4:00 pm') || (lowerText.includes('weekend') && lowerText.includes('full day'))) {
          document.querySelector('input[name="weekend_slot"][value="fullday"]').checked = true;
        } else if (lowerText.includes('4:00 pm - 8:00 pm') || (lowerText.includes('weekend') && lowerText.includes('evening'))) {
          document.querySelector('input[name="weekend_slot"][value="evening"]').checked = true;
        }
      }
      
      updateTimeSlotStyles();
    }

    function updateAvailabilityText() {
      const weekdaySlot = document.querySelector('input[name="weekday_slot"]:checked');
      const weekendSlot = document.querySelector('input[name="weekend_slot"]:checked');
      
      // Update hidden fields for backend
      document.getElementById('weekday_slot_hidden').value = weekdaySlot ? weekdaySlot.value : '';
      document.getElementById('weekend_slot_hidden').value = weekendSlot ? weekendSlot.value : '';
      
      let availabilityText = '';
      
      if (weekdaySlot) {
        const weekdayTime = getTimeSlotText(weekdaySlot.value);
        availabilityText += `Weekdays: ${weekdayTime}`;
      }
      
      if (weekendSlot) {
        const weekendTime = getTimeSlotText(weekendSlot.value);
        if (availabilityText) availabilityText += '\n';
        availabilityText += `Weekends: ${weekendTime}`;
      }
      
      // Update the text field that your backend expects
      document.getElementById('avb_time_text').value = availabilityText;
      
      console.log('Updated availability:', availabilityText); // Debug log
    }

    function getTimeSlotText(slot) {
      const timeSlots = {
        'morning': '8:00 AM - 12:00 PM',
        'afternoon': '12:00 PM - 4:00 PM',
        'fullday': '8:00 AM - 4:00 PM',
        'evening': '4:00 PM - 8:00 PM'
      };
      return timeSlots[slot] || '';
    }

    function prepareFormData() {
      // Ensure all data is properly set before form submission
      updateAvailabilityText();
      
      // Log the data being sent for debugging
      const formData = new FormData(document.querySelector('form'));
      console.log('Form data being submitted:');
      for (let [key, value] of formData.entries()) {
        if (key === 'avb_time_text' || key === 'weekday_slot' || key === 'weekend_slot') {
          console.log(key + ': ' + value);
        }
      }
      
      return true; // Allow form submission
    }
