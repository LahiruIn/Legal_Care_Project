
/* ----------  SIDEBAR TOGGLE  ---------- */
const menuToggleBtn = document.getElementById('toggleMenu');   // <button id="toggleMenu">
const sidebar       = document.querySelector('.sidebar');      // <div class="sidebar">

if (menuToggleBtn && sidebar) {
  menuToggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');      // for desktop shrink/expand
    if (window.innerWidth <= 768) {
      sidebar.classList.toggle('active');       // slide-in on mobile
    }
  });
}

/* ----------  ACTIVE STATE FOR NAV LINKS  ---------- */
const navLinks = document.querySelectorAll('.menu-link');      // class used in your HTML

navLinks.forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();                                       // remove if you need real navigation
    navLinks.forEach(l => l.classList.remove('active'));
    link.classList.add('active');
  });
});

/* ----------  SEARCH INPUT FOCUS EFFECT  ---------- */
const searchInput = document.querySelector('.search-input');   // only if you have one
if (searchInput) {
  searchInput.addEventListener('focus', () => {
    searchInput.parentElement.style.transform = 'scale(1.02)';
  });
  searchInput.addEventListener('blur', () => {
    searchInput.parentElement.style.transform = 'scale(1)';
  });
}

/* ----------  NOTIFICATION CLICK  ---------- */
const notificationBtn = document.querySelector('.header-btn'); // ensure this exists in HTML
if (notificationBtn) {
  notificationBtn.addEventListener('click', () => {
    alert('You have 3 new notifications!');
  });
}

/* ----------  COUNTER ANIMATION  ---------- */
function animateCounters() {
  const counters = document.querySelectorAll('.stat-value[data-value]');
  counters.forEach(counter => {
    const target   = parseInt(counter.dataset.value, 10);
    const isDollar = counter.textContent.trim().includes('$');
    let current    = 0;
    const increment = target / 60; // ≈1 s at 60 fps

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      const value = Math.floor(current).toLocaleString();
      counter.textContent = isDollar ? '$' + value : value;
    }, 16); // 60 fps
  });
}

/* ----------  CHART FILTER FADE EFFECT  ---------- */
document.querySelectorAll('.chart-filter').forEach(filter => {
  filter.addEventListener('change', e => {
    const chart = e.target.closest('.chart-card')?.querySelector('.chart-content');
    if (!chart) return;
    chart.style.opacity = '0.5';
    setTimeout(() => (chart.style.opacity = '1'), 300);
  });
});

/* ----------  RESPONSIVE SIDEBAR RESIZE  ---------- */
window.addEventListener('resize', () => {
  if (window.innerWidth > 768) {
    sidebar?.classList.remove('active');
  }
});

/* ----------  CARD HOVER LIFT  ---------- */
document.querySelectorAll('.stat-card, .chart-card, .activity-card').forEach(card => {
  card.addEventListener('mouseenter', () => (card.style.transform = 'translateY(-2px)'));
  card.addEventListener('mouseleave', () => (card.style.transform = 'translateY(0)'));
});

/* ----------  PAGE-LOAD ANIMATIONS  ---------- */
window.addEventListener('load', () => {
  document.querySelector('.dashboard-content')?.classList.add('fade-in');
  setTimeout(animateCounters, 500);
  setTimeout(simulateRealTimeUpdates, 2000);
});

/* ----------  REAL-TIME ACTIVITY FEED  ---------- */
function simulateRealTimeUpdates() {
  const activities = [
    { icon: 'fa-user-plus',    text: 'New user registration', time: 'Just now', value: '+1',       color: 'var(--success-color)' },
    { icon: 'fa-car',          text: 'Ride completed',        time: 'Just now', value: '$32.50',  color: 'var(--primary-color)' },
    { icon: 'fa-credit-card',  text: 'Payment received',      time: 'Just now', value: '$28.75',  color: 'var(--warning-color)' }
  ];

  setInterval(() => {
    const activityList = document.querySelector('.activity-list');
    if (!activityList) return;

    const { icon, text, time, value, color } = activities[Math.floor(Math.random() * activities.length)];

    const item = document.createElement('div');
    item.className = 'activity-item';
    item.style.opacity = '0';
    item.innerHTML = `
      <div class="activity-avatar" style="background: linear-gradient(135deg, ${color}, ${color}dd);">
        <i class="fas ${icon}"></i>
      </div>
      <div class="activity-content">
        <div class="activity-text">${text}</div>
        <div class="activity-time">${time}</div>
      </div>
      <div class="activity-value">${value}</div>
    `;

    activityList.prepend(item);              // add to top
    requestAnimationFrame(() => item.style.opacity = '1'); // fade-in

    // keep max 6 items
    const items = activityList.querySelectorAll('.activity-item');
    if (items.length > 6) items[items.length - 1].remove();
  }, 15_000); // every 15 s
}

