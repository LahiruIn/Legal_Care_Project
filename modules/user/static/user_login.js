document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const loginBtn = document.getElementById('loginBtn');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const passwordToggle = document.getElementById('passwordToggle');
  const forgotPassword = document.getElementById('forgotPassword');

  // Optional alerts (Flask flash messages)
  const errorAlert = document.getElementById('errorAlert');
  const successAlert = document.getElementById('successAlert');
  const errorMessage = document.getElementById('errorMessage');
  const successMessage = document.getElementById('successMessage');

  let alertTimeout = null;

  // Show/hide password functionality
  if (passwordToggle && passwordInput) {
    passwordToggle.addEventListener('click', () => {
      const type = passwordInput.type === 'password' ? 'text' : 'password';
      passwordInput.type = type;

      const icon = passwordToggle.querySelector('i');
      if (icon) {
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
      }
    });
  }

  // Email validation function
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  // Input validation highlight
  function validateInput(input, isEmail = false) {
    const value = input.value.trim();
    let isValid = value.length > 0;

    if (isEmail) {
      isValid = validateEmail(value);
    }

    input.style.borderColor = isValid ? 'var(--success)' : 'var(--error)';
    input.style.boxShadow = isValid
      ? '0 0 0 4px rgba(20, 184, 166, 0.1)'
      : '0 0 0 4px rgba(239, 68, 68, 0.1)';
    return isValid;
  }

  // Show alert message
  function showAlert(type, message) {
    clearTimeout(alertTimeout);
    const alert = type === 'error' ? errorAlert : successAlert;
    const messageSpan = type === 'error' ? errorMessage : successMessage;
    if (!alert || !messageSpan) return;

    messageSpan.textContent = message;
    alert.style.display = 'flex';

    alertTimeout = setTimeout(() => {
      alert.style.display = 'none';
    }, 5000);
  }

  // Hide alerts
  function hideAlerts() {
    if (errorAlert) errorAlert.style.display = 'none';
    if (successAlert) successAlert.style.display = 'none';
    clearTimeout(alertTimeout);
  }

  // Real-time validation on typing
  if (emailInput) {
    emailInput.addEventListener('input', () => {
      validateInput(emailInput, true);
      hideAlerts();
    });
  }

  if (passwordInput) {
    passwordInput.addEventListener('input', () => {
      validateInput(passwordInput);
      hideAlerts();
    });
  }

  // Form submission
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      const email = emailInput.value.trim();
      const password = passwordInput.value.trim();
      let isValid = true;

      // Validate email
      if (!email) {
        e.preventDefault();
        showAlert('error', 'Please enter your email address');
        validateInput(emailInput, true);
        isValid = false;
      } else if (!validateEmail(email)) {
        e.preventDefault();
        showAlert('error', 'Please enter a valid email address');
        validateInput(emailInput, true);
        isValid = false;
      }

      // Validate password
      if (!password) {
        e.preventDefault();
        showAlert('error', 'Please enter your password');
        validateInput(passwordInput);
        isValid = false;
      } else if (password.length < 6) {
        e.preventDefault();
        showAlert('error', 'Password must be at least 6 characters');
        validateInput(passwordInput);
        isValid = false;
      }

      // If validation fails, return
      if (!isValid) return;

      // Show loading spinner and feedback
      loginBtn.disabled = true;
      if (loadingSpinner) loadingSpinner.style.display = 'inline-block';
      loginBtn.style.opacity = '0.8';

      // Simulate form submission (replace with actual backend logic)
      setTimeout(() => {
        loadingSpinner.style.display = 'none';
        loginBtn.disabled = false;
        loginBtn.style.opacity = '1';

        // Show success message
        successAlert.style.display = 'flex';
        successMessage.textContent = 'Login successful!';

        // Simulate redirect or other actions after success
        setTimeout(() => {
          successAlert.style.display = 'none';
          window.location.href = '/dashboard'; // Replace with actual redirect
        }, 2000);
      }, 2000); // Simulate 2-second API call delay
    });
  }

  // Keyboard shortcuts for focusing on input fields
  document.addEventListener('keydown', (e) => {
    if (e.altKey && e.key === 'e' && emailInput) {
      e.preventDefault();
      emailInput.focus();
    }
    if (e.altKey && e.key === 'p' && passwordInput) {
      e.preventDefault();
      passwordInput.focus();
    }
  });

  // Autofocus on email input on page load
  window.addEventListener('load', () => {
    if (emailInput) emailInput.focus();
  });

  // Console log message for debugging
  console.log('%c👤 User Portal Ready', 'color: #14b8a6; font-size: 16px; font-weight: bold;');
});
