document.addEventListener('DOMContentLoaded', function () {
  var navbar = document.querySelector('.dc-navbar');
  if (!navbar) return;

  var ticking = false;

  window.addEventListener('scroll', function () {
    if (!ticking) {
      requestAnimationFrame(function () {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
});
