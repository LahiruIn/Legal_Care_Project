document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const loginBtn = document.getElementById('loginBtn');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const passwordToggle = document.getElementById('passwordToggle');
  const forgotPassword = document.getElementById('forgotPassword');

  const errorAlert = document.getElementById('errorAlert');
  const successAlert = document.getElementById('successAlert');
  const errorMessage = document.getElementById('errorMessage');
  const successMessage = document.getElementById('successMessage');

  let alertTimeout = null;

  // Show/hide password
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

  // Input validation highlight
  function validateInput(input) {
    const value = input.value.trim();
    const isValid = value.length > 0;
    input.style.borderColor = isValid ? 'var(--success)' : 'var(--error)';
    input.style.boxShadow = isValid
      ? '0 0 0 4px rgba(16, 185, 129, 0.1)'
      : '0 0 0 4px rgba(239, 68, 68, 0.1)';
    return isValid;
  }

  // Show custom alert
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

  function hideAlerts() {
    if (errorAlert) errorAlert.style.display = 'none';
    if (successAlert) successAlert.style.display = 'none';
    clearTimeout(alertTimeout);
  }

  // Input validation on typing
  if (usernameInput) {
    usernameInput.addEventListener('input', () => {
      validateInput(usernameInput);
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
      // Use HTML5 validation first
      if (!loginForm.checkValidity()) {
        e.preventDefault();
        loginForm.reportValidity(); // shows "Please fill out this field"
        return;
      }

      const username = usernameInput.value.trim();
      const password = passwordInput.value.trim();
      let isValid = true;

      // Additional custom validations
      if (password.length < 6) {
        e.preventDefault();
        showAlert('error', 'Password must be at least 6 characters');
        validateInput(passwordInput);
        isValid = false;
      }

      if (!isValid) return;

      // UI feedback
      loginBtn.disabled = true;
      if (loadingSpinner) loadingSpinner.style.display = 'inline-block';
      loginBtn.style.opacity = '0.8';
    });
  }

  // Forgot password alert
  if (forgotPassword) {
    forgotPassword.addEventListener('click', (e) => {
      e.preventDefault();
      showAlert('success', 'Reset instructions sent to your email.');
    });
  }

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.altKey && e.key === 'u' && usernameInput) {
      e.preventDefault();
      usernameInput.focus();
    }
    if (e.altKey && e.key === 'p' && passwordInput) {
      e.preventDefault();
      passwordInput.focus();
    }
  });

  // Autofocus on load
  window.addEventListener('load', () => {
    if (usernameInput) usernameInput.focus();
  });

  console.log('%c⚖️ Lawyer Portal Ready', 'color: #2f855a; font-size: 16px; font-weight: bold;');
});
