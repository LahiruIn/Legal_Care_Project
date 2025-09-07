document.addEventListener('DOMContentLoaded', function() {
            // Status Toggle Functionality
            const statusToggle = document.getElementById('status');
            const statusText = document.getElementById('statusText');
            
            statusToggle.addEventListener('change', function() {
                if (this.checked) {
                    statusText.textContent = 'Active';
                    statusText.classList.remove('status-inactive');
                    statusText.classList.add('status-active');
                } else {
                    statusText.textContent = 'Inactive';
                    statusText.classList.remove('status-active');
                    statusText.classList.add('status-inactive');
                }
            });
            
            // Enhanced Image Upload Functionality
            const imageUpload = document.getElementById('imageUpload');
            const imageInput = document.getElementById('lawyer_img');
            const imagePreview = document.getElementById('imagePreview');
            const changeImageBtn = document.getElementById('changeImageBtn');
            const removeImageBtn = document.getElementById('removeImageBtn');
            const openCameraBtn = document.getElementById('openCameraBtn');
            
            // Click to upload
            imageUpload.addEventListener('click', function(e) {
                if (!e.target.closest('.upload-btn')) {
                    imageInput.click();
                }
            });
            
            // Drag and drop
            imageUpload.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.style.borderColor = 'var(--primary-color)';
                this.style.backgroundColor = '#f0f4f8';
            });
            
            imageUpload.addEventListener('dragleave', function() {
                this.style.borderColor = 'var(--border-color)';
                this.style.backgroundColor = 'var(--light-color)';
            });
            
            imageUpload.addEventListener('drop', function(e) {
                e.preventDefault();
                this.style.borderColor = 'var(--border-color)';
                this.style.backgroundColor = 'var(--light-color)';
                
                if (e.dataTransfer.files.length) {
                    imageInput.files = e.dataTransfer.files;
                    updateImagePreview();
                }
            });
            
            // File selection
            imageInput.addEventListener('change', updateImagePreview);
            
            function updateImagePreview() {
                if (imageInput.files && imageInput.files[0]) {
                    const file = imageInput.files[0];
                    
                    // Validate file type and size
                    if (!file.type.match('image.*')) {
                        alert('Please select an image file (JPEG, PNG)');
                        return;
                    }
                    
                    if (file.size > 2 * 1024 * 1024) {
                        alert('Image size should be less than 2MB');
                        return;
                    }
                    
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        imagePreview.src = e.target.result;
                        imagePreview.style.display = 'block';
                        imageUpload.querySelector('i').style.display = 'none';
                        imageUpload.querySelector('p').style.display = 'none';
                        imageUpload.querySelector('small').style.display = 'none';
                        
                        // Show action buttons
                        changeImageBtn.style.display = 'inline-flex';
                        removeImageBtn.style.display = 'inline-flex';
                    }
                    
                    reader.readAsDataURL(file);
                }
            }
            
            // Change image button
            changeImageBtn.addEventListener('click', function() {
                imageInput.click();
            });
            
            // Remove image button
            removeImageBtn.addEventListener('click', function() {
                imageInput.value = '';
                imagePreview.style.display = 'none';
                imagePreview.src = '';
                imageUpload.querySelector('i').style.display = 'block';
                imageUpload.querySelector('p').style.display = 'block';
                imageUpload.querySelector('small').style.display = 'block';
                
                // Hide action buttons
                changeImageBtn.style.display = 'none';
                removeImageBtn.style.display = 'none';
            });
            
            // Open camera (placeholder functionality)
            openCameraBtn.addEventListener('click', function() {
                alert('Camera functionality would be implemented here in a production environment');
            });
            
            // Day type selection functionality
            const weekdayCard = document.getElementById('weekdayCard');
            const weekendCard = document.getElementById('weekendCard');
            const weekdayCheckbox = document.getElementById('weekdays');
            const weekendCheckbox = document.getElementById('weekend');
            const weekdayDaySelection = document.getElementById('weekday-day-selection');
            const weekendDaySelection = document.getElementById('weekend-day-selection');
            const weekdaysAvailability = document.getElementById('weekdays-availability');
            const weekendAvailability = document.getElementById('weekend-availability');
            
            weekdayCard.addEventListener('click', function() {
                weekdayCheckbox.checked = !weekdayCheckbox.checked;
                if (weekdayCheckbox.checked) {
                    weekdayCard.classList.add('active');
                    weekdayDaySelection.classList.add('active');
                    weekdaysAvailability.classList.add('active');
                } else {
                    weekdayCard.classList.remove('active');
                    weekdayDaySelection.classList.remove('active');
                    weekdaysAvailability.classList.remove('active');
                    // Uncheck all weekday days and time slots
                    document.querySelectorAll('[name="weekday_days[]"]').forEach(d => d.checked = false);
                    document.querySelectorAll('[name="weekday_time"]').forEach(t => t.checked = false);
                }
            });
            
            weekendCard.addEventListener('click', function() {
                weekendCheckbox.checked = !weekendCheckbox.checked;
                if (weekendCheckbox.checked) {
                    weekendCard.classList.add('active');
                    weekendDaySelection.classList.add('active');
                    weekendAvailability.classList.add('active');
                } else {
                    weekendCard.classList.remove('active');
                    weekendDaySelection.classList.remove('active');
                    weekendAvailability.classList.remove('active');
                    // Uncheck all weekend days and time slots
                    document.querySelectorAll('[name="weekend_days[]"]').forEach(d => d.checked = false);
                    document.querySelectorAll('[name="weekend_time"]').forEach(t => t.checked = false);
                }
            });
            
            // Form submission
            document.getElementById('addLawyerForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Validate form
                if (!validateForm()) return;
                
                // Show loading state
                const saveBtn = document.getElementById('saveBtn');
                saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
                saveBtn.disabled = true;
                
                // Simulate form submission
                setTimeout(() => {
                    const form = document.getElementById('addLawyerForm');
                    const formData = new FormData(form);

                    fetch(form.action, {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.text(); // Change to response.json() if your backend returns JSON
                    })
                    .then(result => {
                        alert('✅ Lawyer profile saved successfully!');
                        saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Lawyer Profile';
                        saveBtn.disabled = false;

                        form.reset();
                        resetImageUpload();
                    })
                    .catch(error => {
                        alert('❌ Failed to save lawyer profile. Please try again.');
                        console.error('Error:', error);
                        saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Lawyer Profile';
                        saveBtn.disabled = false;
                    });
                }, 1500);
              });
            
            function validateForm() {
                // Basic validation example
                if (!document.getElementById('full_name').value) {
                    alert('Please enter the lawyer\'s full name');
                    return false;
                }
                
                // Validate at least one day type is selected
                if (!weekdayCheckbox.checked && !weekendCheckbox.checked) {
                    alert('Please select at least one day type (Weekdays or Weekend)');
                    return false;
                }
                
                // Validate at least one day is selected for each active day type
                if (weekdayCheckbox.checked) {
                    const weekdayDaysSelected = document.querySelectorAll('[name="weekday_days[]"]:checked').length > 0;
                    if (!weekdayDaysSelected) {
                        alert('Please select at least one weekday');
                        return false;
                    }
                    
                    const weekdayTimeSelected = document.querySelectorAll('[name="weekday_time"]:checked').length > 0;
                    if (!weekdayTimeSelected) {
                        alert('Please select a time slot for weekdays');
                        return false;
                    }
                }
                
                if (weekendCheckbox.checked) {
                    const weekendDaysSelected = document.querySelectorAll('[name="weekend_days[]"]:checked').length > 0;
                    if (!weekendDaysSelected) {
                        alert('Please select at least one weekend day');
                        return false;
                    }
                    
                    const weekendTimeSelected = document.querySelectorAll('[name="weekend_time"]:checked').length > 0;
                    if (!weekendTimeSelected) {
                        alert('Please select a time slot for weekend');
                        return false;
                    }
                }
                
                return true;
            }
            
            function resetImageUpload() {
                imageInput.value = '';
                imagePreview.style.display = 'none';
                imagePreview.src = '';
                imageUpload.querySelector('i').style.display = 'block';
                imageUpload.querySelector('p').style.display = 'block';
                imageUpload.querySelector('small').style.display = 'block';
                
                // Hide action buttons
                changeImageBtn.style.display = 'none';
                removeImageBtn.style.display = 'none';
            }
            
            // Cancel button
            document.getElementById('cancelBtn').addEventListener('click', function() {
                if (confirm('Are you sure you want to cancel? All unsaved changes will be lost.')) {
                    // Reset form
                    document.getElementById('addLawyerForm').reset();
                    resetImageUpload();
                    
                    // Reset status toggle
                    statusToggle.checked = true;
                    statusText.textContent = 'Active';
                    statusText.classList.remove('status-inactive');
                    statusText.classList.add('status-active');
                    
                    // Reset day type selection
                    weekdayCheckbox.checked = false;
                    weekendCheckbox.checked = false;
                    weekdayCard.classList.remove('active');
                    weekendCard.classList.remove('active');
                    weekdayDaySelection.classList.remove('active');
                    weekendDaySelection.classList.remove('active');
                    weekdaysAvailability.classList.remove('active');
                    weekendAvailability.classList.remove('active');
                    
                    // Uncheck all days and time slots
                    document.querySelectorAll('.day-checkbox').forEach(d => d.checked = false);
                    document.querySelectorAll('.time-checkbox').forEach(t => t.checked = false);
                }
            });
        });