 document.addEventListener('DOMContentLoaded', function() {
      // Character counters
      function setupCharCounter(inputId, counterId, maxLength) {
        const input = document.getElementById(inputId);
        const counter = document.getElementById(counterId);
        
        if (input && counter) {
          function updateCounter() {
            const length = input.value.length;
            counter.textContent = `${length} / ${maxLength} characters`;
            
            if (length > maxLength * 0.9) {
              counter.className = 'char-counter danger';
            } else if (length > maxLength * 0.75) {
              counter.className = 'char-counter warning';
            } else {
              counter.className = 'char-counter';
            }
          }
          
          input.addEventListener('input', updateCounter);
          updateCounter();
        }
      }

      setupCharCounter('titleInput', 'titleCounter', 200);
      setupCharCounter('summaryInput', 'summaryCounter', 500);

      // File input handling
      function setupFileInput(inputId, labelId, noteId) {
        const input = document.getElementById(inputId);
        const label = document.getElementById(labelId);
        const note = document.getElementById(noteId);
        
        if (input && label) {
          input.addEventListener('change', function() {
            const file = this.files[0];
            const span = label.querySelector('span');
            
            if (file) {
              span.textContent = file.name;
              label.classList.add('has-file');
              label.querySelector('i').className = 'fas fa-check-circle';
            } else {
              span.textContent = 'Choose file';
              label.classList.remove('has-file');
              label.querySelector('i').className = 'fas fa-cloud-upload-alt';
            }
          });
        }
      }

      setupFileInput('imageFile', 'imageLabel', 'imageNote');
      setupFileInput('docFile', 'docLabel', 'docNote');

      // Content type validation
      const contentType = document.getElementById('contentType');
      const imageNote = document.getElementById('imageNote');
      const docNote = document.getElementById('docNote');

      if (contentType) {
        contentType.addEventListener('change', function() {
          const type = this.value;
          
          // Update file requirements based on content type
          if (type === 'image') {
            imageNote.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Required for Image content type';
            imageNote.classList.add('required');
          } else {
            imageNote.innerHTML = '<i class="fas fa-info-circle"></i> Supports PNG, JPG, GIF, WEBP formats';
            imageNote.classList.remove('required');
          }
          
          if (type === 'document') {
            docNote.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Required for Document content type';
            docNote.classList.add('required');
          } else {
            docNote.innerHTML = '<i class="fas fa-info-circle"></i> Supports PDF, DOC, PPT, XLS, TXT formats';
            docNote.classList.remove('required');
          }
        });
      }

      // Form submission handling
      const form = document.getElementById('contentForm');
      const submitBtn = document.getElementById('submitBtn');

      if (form && submitBtn) {
        form.addEventListener('submit', function(e) {
          submitBtn.classList.add('loading');
          submitBtn.disabled = true;
          
          // Re-enable after 5 seconds in case of issues
          setTimeout(() => {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
          }, 5000);
        });
      }

      // URL validation
      const externalLink = document.getElementById('externalLink');
      if (externalLink) {
        externalLink.addEventListener('blur', function() {
          const url = this.value.trim();
          if (url && !url.match(/^https?:\/\/.+/)) {
            this.setCustomValidity('Please enter a valid URL starting with http:// or https://');
          } else {
            this.setCustomValidity('');
          }
        });
      }
    });