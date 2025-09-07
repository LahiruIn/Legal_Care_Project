    // Password toggle functionality
    const passwordToggle = document.getElementById('password-toggle');
    const passwordInput = document.getElementById('password');
    const confirmPasswordToggle = document.getElementById('confirm-password-toggle');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const passwordMatchError = document.getElementById('password-match-error');
    
    passwordToggle.addEventListener('click', function() {
      if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        passwordToggle.innerHTML = '<i class="fas fa-eye-slash"></i>';
      } else {
        passwordInput.type = 'password';
        passwordToggle.innerHTML = '<i class="fas fa-eye"></i>';
      }
    });
    
    confirmPasswordToggle.addEventListener('click', function() {
      if (confirmPasswordInput.type === 'password') {
        confirmPasswordInput.type = 'text';
        confirmPasswordToggle.innerHTML = '<i class="fas fa-eye-slash"></i>';
      } else {
        confirmPasswordInput.type = 'password';
        confirmPasswordToggle.innerHTML = '<i class="fas fa-eye"></i>';
      }
    });

    // Password matching validation
    function validatePasswordMatch() {
      if (passwordInput.value !== confirmPasswordInput.value) {
        passwordMatchError.style.display = 'block';
        confirmPasswordInput.style.borderColor = 'var(--error)';
        return false;
      } else {
        passwordMatchError.style.display = 'none';
        confirmPasswordInput.style.borderColor = 'rgba(29, 78, 216, 0.3)';
        return true;
      }
    }

    confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    passwordInput.addEventListener('input', validatePasswordMatch);

    // Form submission handling
    document.getElementById('register-form').addEventListener('submit', function(e) {
      if (!validatePasswordMatch()) {
        e.preventDefault();
        return;
      }
      
      // Show loading state
      const submitBtn = document.querySelector('.register-btn');
      const btnText = document.querySelector('.btn-text');
      const spinner = document.querySelector('.loading-spinner');
      
      btnText.textContent = 'Creating Account...';
      spinner.style.display = 'block';
      submitBtn.disabled = true;
      
      // Allow form to submit normally
    });
