document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const loginForm = document.getElementById('loginForm');
  const loginBtn = document.getElementById('loginBtn');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const passwordToggle = document.getElementById('passwordToggle');
  const errorAlert = document.getElementById('errorAlert');
  const successAlert = document.getElementById('successAlert');
  const errorMessage = document.getElementById('errorMessage');
  const successMessage = document.getElementById('successMessage');
  const forgotPassword = document.getElementById('forgotPassword');
  const adLogin = document.getElementById('adLogin');
  const samlLogin = document.getElementById('samlLogin');

  let alertTimeout = null;

  // Toggle password visibility
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

  // Alert display
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

  // Submit validation (use browser built-in messages)
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      // Browser validation check
      if (!usernameInput.checkValidity()) {
        e.preventDefault();
        usernameInput.reportValidity();
        return;
      }

      if (!passwordInput.checkValidity()) {
        e.preventDefault();
        passwordInput.reportValidity();
        return;
      }

      // If valid → show loading state
      loginBtn.disabled = true;
      if (loadingSpinner) loadingSpinner.style.display = 'inline-block';
      loginBtn.style.opacity = '0.8';
    });
  }

  // Optional SSO behavior (demo only)
  if (adLogin) {
    adLogin.addEventListener('click', (e) => {
      e.preventDefault();
      showAlert('success', 'Redirecting to Active Directory authentication...');
    });
  }

  if (samlLogin) {
    samlLogin.addEventListener('click', (e) => {
      e.preventDefault();
      showAlert('success', 'Redirecting to SAML SSO provider...');
    });
  }

  if (forgotPassword) {
    forgotPassword.addEventListener('click', (e) => {
      e.preventDefault();
      showAlert('success', 'Password reset instructions sent to your registered email');
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

  // Auto-focus username
  window.addEventListener('load', () => {
    if (usernameInput) usernameInput.focus();
  });

  // 🚨 Check for invalid credential flag in URL
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('error') && urlParams.get('error') === '1') {
    showAlert('error', 'Invalid Credential');
  }

  // Developer console info
  console.log('%c🔐 Web Login Ready', 'color: #3b82f6; font-size: 16px; font-weight: bold;');
});
