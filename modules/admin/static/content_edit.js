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
      function setupFileInput(inputId, groupId, noteId) {
        const input = document.getElementById(inputId);
        const group = document.getElementById(groupId);
        const note = document.getElementById(noteId);
        
        if (input && group) {
          input.addEventListener('change', function() {
            const file = this.files[0];
            
            if (file) {
              group.classList.add('has-file');
              group.innerHTML = `
                <i class="fas fa-check-circle" style="font-size: 32px; color: var(--success-color); margin-bottom: 12px;"></i>
                <p style="margin-bottom: 8px; font-weight: 600; color: var(--success-color);">File Selected</p>
                <p style="font-size: 14px; color: var(--dark-color); margin-bottom: 8px;">${file.name}</p>
                <p style="font-size: 12px; color: var(--secondary-color);">File size: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
              `;
              
              if (note) {
                note.innerHTML = '<i class="fas fa-check-circle"></i> New file will replace the current one when saved';
                note.style.borderLeftColor = 'var(--success-color)';
                note.style.background = 'var(--success-light)';
                note.style.color = '#065f46';
              }
            }
          });
        }
      }

      setupFileInput('imageFile', 'imageInputGroup', 'imageNote');
      setupFileInput('docFile', 'docInputGroup', 'docNote');

      // Content type validation and UI updates
      const contentType = document.getElementById('contentType');
      const imageNote = document.getElementById('imageNote');
      const docNote = document.getElementById('docNote');

      if (contentType) {
        contentType.addEventListener('change', function() {
          const type = this.value;
          
          // Update requirements based on content type
          if (type === 'image') {
            imageNote.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Image is required for Image content type';
            imageNote.className = 'note required';
          } else {
            imageNote.innerHTML = '<i class="fas fa-info-circle"></i> Upload a new image to replace the current one';
            imageNote.className = 'note';
          }
          
          if (type === 'document') {
            docNote.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Document is required for Document content type';
            docNote.className = 'note required';
          } else {
            docNote.innerHTML = '<i class="fas fa-info-circle"></i> Upload a new document to replace the current one';
            docNote.className = 'note';
          }
        });
        
        // Trigger initial update
        contentType.dispatchEvent(new Event('change'));
      }

      // Remove file checkboxes
      const removeImage = document.getElementById('removeImage');
      const removeDoc = document.getElementById('removeDoc');
      
      if (removeImage) {
        removeImage.addEventListener('change', function() {
          const wrapper = this.closest('.remove-file-wrapper');
          if (this.checked) {
            wrapper.style.background = 'var(--danger-light)';
            wrapper.style.borderColor = 'var(--danger-color)';
          } else {
            wrapper.style.background = 'var(--warning-light)';
            wrapper.style.borderColor = '#f59e0b';
          }
        });
      }
      
      if (removeDoc) {
        removeDoc.addEventListener('change', function() {
          const wrapper = this.closest('.remove-file-wrapper');
          if (this.checked) {
            wrapper.style.background = 'var(--danger-light)';
            wrapper.style.borderColor = 'var(--danger-color)';
          } else {
            wrapper.style.background = 'var(--warning-light)';
            wrapper.style.borderColor = '#f59e0b';
          }
        });
      }

      // Form submission handling
      const form = document.getElementById('editForm');
      const saveBtn = document.getElementById('saveBtn');

      if (form && saveBtn) {
        form.addEventListener('submit', function(e) {
          saveBtn.classList.add('loading');
          saveBtn.disabled = true;
          
          // Re-enable after 10 seconds in case of issues
          setTimeout(() => {
            saveBtn.classList.remove('loading');
            saveBtn.disabled = false;
          }, 10000);
        });
      }

      // Preview functionality
      window.previewContent = function() {
        const form = document.getElementById('editForm');
        const formData = new FormData(form);
        
        // Create preview in new window/tab
        const previewWindow = window.open('', '_blank');
        previewWindow.document.write(`
          <html>
            <head>
              <title>Preview: ${formData.get('title')}</title>
              <style>
                body { font-family: system-ui, Arial; margin: 40px; line-height: 1.6; }
                .preview-header { background: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .preview-title { font-size: 24px; font-weight: bold; margin-bottom: 8px; }
                .preview-meta { color: #64748b; font-size: 14px; }
                .preview-content { background: #fff; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; }
                .preview-section { margin-bottom: 20px; }
                .preview-section h3 { color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }
                .preview-warning { background: #fef3c7; color: #92400e; padding: 12px; border-radius: 6px; margin-bottom: 20px; }
              </style>
            </head>
            <body>
              <div class="preview-warning">
                <strong>⚠️ Preview Mode</strong> - This is how your content will appear. Changes are not saved yet.
              </div>
              <div class="preview-header">
                <div class="preview-title">${formData.get('title')}</div>
                <div class="preview-meta">
                  Type: ${formData.get('kind')} • 
                  Status: ${formData.get('published') ? 'Published' : 'Draft'}
                </div>
              </div>
              <div class="preview-content">
                ${formData.get('summary') ? `
                  <div class="preview-section">
                    <h3>Summary</h3>
                    <p>${formData.get('summary')}</p>
                  </div>
                ` : ''}
                ${formData.get('body') ? `
                  <div class="preview-section">
                    <h3>Content</h3>
                    <div style="white-space: pre-wrap;">${formData.get('body')}</div>
                  </div>
                ` : ''}
                ${formData.get('external_link') ? `
                  <div class="preview-section">
                    <h3>External Link</h3>
                    <p><a href="${formData.get('external_link')}" target="_blank">${formData.get('external_link')}</a></p>
                  </div>
                ` : ''}
              </div>
            </body>
          </html>
        `);
        previewWindow.document.close();
      };

      // Toast notification system
      window.showToast = function(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        
        const icons = {
          success: 'check-circle',
          error: 'exclamation-circle',
          warning: 'exclamation-triangle',
          info: 'info-circle'
        };

        toast.className = `flash ${type}`;
        toast.style.cssText = `
          margin-bottom: 8px;
          min-width: 300px;
          transform: translateX(100%);
          transition: transform 0.3s ease-out;
          position: relative;
          z-index: 1001;
        `;
        
        toast.innerHTML = `
          <i class="fas fa-${icons[type] || 'info-circle'}"></i>
          ${message}
          <button onclick="this.parentElement.remove()" style="background:none;border:none;color:inherit;margin-left:auto;cursor:pointer;font-size:16px;">×</button>
        `;
        
        container.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
          toast.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
          if (toast.parentElement) {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
              if (toast.parentElement) {
                toast.remove();
              }
            }, 300);
          }
        }, 5000);
      };

      // Auto-save functionality (optional)
      let autoSaveTimeout;
      const formInputs = document.querySelectorAll('#editForm input, #editForm select, #editForm textarea');
      
      formInputs.forEach(input => {
        if (input.type !== 'file' && input.type !== 'checkbox') {
          input.addEventListener('input', function() {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
              // This would typically save to localStorage or make an AJAX call
              console.log('Auto-save triggered for:', this.name);
            }, 2000);
          });
        }
      });

      // Keyboard shortcuts
      document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S for save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
          e.preventDefault();
          document.getElementById('editForm').submit();
        }
        
        // Ctrl/Cmd + P for preview
        if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
          e.preventDefault();
          previewContent();
        }
        
        // Escape for cancel
        if (e.key === 'Escape') {
          if (confirm('Are you sure you want to cancel? Any unsaved changes will be lost.')) {
            window.location.href = '{{ url_for("admin.admin_content_view", content_id=item.id) }}';
          }
        }
      });

      // Form change detection
      let formChanged = false;
      const originalFormData = new FormData(document.getElementById('editForm'));
      
      formInputs.forEach(input => {
        input.addEventListener('change', () => {
          formChanged = true;
        });
      });
      
      // Warn before leaving if changes exist
      window.addEventListener('beforeunload', function(e) {
        if (formChanged) {
          e.preventDefault();
          e.returnValue = '';
        }
      });

      // Mark form as submitted to prevent beforeunload warning
      document.getElementById('editForm').addEventListener('submit', function() {
        formChanged = false;
      });

      // Show success message after form submission
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('saved') === 'true') {
        showToast('Content updated successfully!', 'success');
      }
    });