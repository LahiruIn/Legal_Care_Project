document.addEventListener('DOMContentLoaded', function() {
      // Enhanced delete confirmation
      window.confirmDelete = function() {
        return confirm('⚠️ Are you sure you want to delete this content?\n\nThis action cannot be undone and will permanently remove:\n• The content item\n• Any associated files\n• All metadata\n\nType "DELETE" to confirm this action.');
      };

      // Copy page link functionality
      window.copyPageLink = function() {
        const url = window.location.href;
        
        if (navigator.clipboard) {
          navigator.clipboard.writeText(url).then(() => {
            showToast('Link copied to clipboard!', 'success');
          }).catch(() => {
            fallbackCopyText(url);
          });
        } else {
          fallbackCopyText(url);
        }
      };

      // Fallback copy method
      function fallbackCopyText(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
          document.execCommand('copy');
          showToast('Link copied to clipboard!', 'success');
        } catch (err) {
          showToast('Failed to copy link', 'error');
        }
        
        document.body.removeChild(textArea);
      }

      // Share content functionality
      window.shareContent = function() {
        const shareData = {
          title: '{{ item.title|e }}',
          text: '{{ item.summary|e if item.summary else "Check out this legal content" }}',
          url: window.location.href
        };

        if (navigator.share) {
          navigator.share(shareData).catch((err) => {
            console.log('Error sharing:', err);
            fallbackShare();
          });
        } else {
          fallbackShare();
        }
      };

      // Fallback share method
      function fallbackShare() {
        const url = window.location.href;
        const title = '{{ item.title|e }}';
        const text = `Check out: ${title} - ${url}`;
        
        copyPageLink();
        showToast('Link copied! You can now paste it to share.', 'info');
      }

      // Publish content functionality
      window.publishContent = function() {
        if (confirm('Publish this content now? It will become visible to all users.')) {
          const btn = event.target;
          btn.classList.add('loading');
          btn.disabled = true;
          
          // This would typically make an AJAX call to publish
          // For now, just show a toast and redirect to edit page
          setTimeout(() => {
            showToast('Redirecting to publish...', 'info');
            window.location.href = '{{ url_for("admin.admin_content_edit", content_id=item.id) }}';
          }, 1000);
        }
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

      // Enhanced image loading
      const heroImage = document.querySelector('.hero-image');
      if (heroImage) {
        heroImage.addEventListener('load', function() {
          this.style.opacity = '0';
          this.style.transition = 'opacity 0.3s ease-in-out';
          setTimeout(() => {
            this.style.opacity = '1';
          }, 50);
        });
      }

      // Keyboard shortcuts
      document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + E for edit
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
          e.preventDefault();
          window.location.href = '{{ url_for("admin.admin_content_edit", content_id=item.id) }}';
        }
        
        // Ctrl/Cmd + Backspace for back
        if ((e.ctrlKey || e.metaKey) && e.key === 'Backspace') {
          e.preventDefault();
          window.location.href = '{{ url_for("admin.admin_content_list") }}';
        }
        
        // Ctrl/Cmd + Shift + C for copy link
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
          e.preventDefault();
          copyPageLink();
        }
      });

      // Add keyboard shortcut hints
      const hints = document.createElement('div');
      hints.innerHTML = `
        <div style="position: fixed; bottom: 20px; left: 20px; background: rgba(0,0,0,0.8); color: white; padding: 8px 12px; border-radius: 6px; font-size: 12px; opacity: 0; transition: opacity 0.3s; z-index: 1000;" id="keyboardHints">
          <div><kbd>Ctrl+E</kbd> Edit • <kbd>Ctrl+⌫</kbd> Back • <kbd>Ctrl+Shift+C</kbd> Copy Link</div>
        </div>
      `;
      document.body.appendChild(hints);

      // Show/hide keyboard hints on Alt key
      document.addEventListener('keydown', function(e) {
        if (e.altKey) {
          document.getElementById('keyboardHints').style.opacity = '1';
        }
      });

      document.addEventListener('keyup', function(e) {
        if (!e.altKey) {
          document.getElementById('keyboardHints').style.opacity = '0';
        }
      });

      // Smooth scroll for long content
      if (window.location.hash) {
        setTimeout(() => {
          const element = document.querySelector(window.location.hash);
          if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);
      }

      // Auto-save scroll position
      const scrollPosition = sessionStorage.getItem('contentViewScrollPos');
      if (scrollPosition) {
        window.scrollTo(0, parseInt(scrollPosition));
        sessionStorage.removeItem('contentViewScrollPos');
      }

      // Save scroll position when navigating away
      window.addEventListener('beforeunload', function() {
        sessionStorage.setItem('contentViewScrollPos', window.scrollY);
      });
    });