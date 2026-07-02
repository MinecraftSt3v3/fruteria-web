// Frutería Elí — Main JS

document.addEventListener('DOMContentLoaded', () => {
  // Mobile nav toggle
  const navToggle = document.querySelector('.nav-toggle');
  if (navToggle) {
    const navLinks = document.querySelector('.nav-links');
    const langToggle = document.querySelector('.lang-toggle');
    navToggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      langToggle.classList.toggle('open', isOpen);
      navToggle.innerHTML = isOpen ? '&#x2715;' : '&#9776;';
    });
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        langToggle.classList.remove('open');
        navToggle.innerHTML = '&#9776;';
      });
    });
  }
});

// Add to cart AJAX
document.addEventListener('DOMContentLoaded', () => {
  // Animate cart badge on add
  document.querySelectorAll('.btn-add').forEach(btn => {
    btn.addEventListener('click', (e) => {
      // Simple bounce animation
      btn.style.transform = 'scale(0.95)';
      setTimeout(() => btn.style.transform = '', 150);
    });
  });

  // Auto-dismiss alerts
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.5s';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });
});
