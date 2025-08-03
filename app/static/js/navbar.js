document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('navbar-nav-toggle');
  const linksContainer = document.getElementById('navbar-nav-links');
  const navLinks = Array.from(document.querySelectorAll('.navbar-nav__link'));

  if (toggle) {
    toggle.addEventListener('click', function (e) {
      const expanded = this.getAttribute('aria-expanded') === 'true';
      this.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      linksContainer.classList.toggle('expanded');
    });

    // close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && linksContainer.classList.contains('expanded')) {
        toggle.setAttribute('aria-expanded', 'false');
        linksContainer.classList.remove('expanded');
      }
    });

    // click outside to close (mobile menu)
    document.addEventListener('click', (e) => {
      if (
        linksContainer.classList.contains('expanded') &&
        !linksContainer.contains(e.target) &&
        !toggle.contains(e.target)
      ) {
        toggle.setAttribute('aria-expanded', 'false');
        linksContainer.classList.remove('expanded');
      }
    });
  }

  // Active link highlighting based on current path
  const currentPath = window.location.pathname.replace(/\/+$/, '') || '/';
  let matched = false;

  navLinks.forEach((link) => {
    const href = link.getAttribute('href');
    if (!href) return;

    // Create absolute URL to extract pathname
    let linkPath;
    try {
      const url = new URL(href, window.location.origin);
      linkPath = url.pathname.replace(/\/+$/, '') || '/';
    } catch {
      linkPath = href.replace(/\/+$/, '') || '/';
    }

    const isExact = linkPath === currentPath;
    const isPrefix = linkPath !== '/' && currentPath.startsWith(linkPath + '/');

    if ((isExact || isPrefix) && !matched) {
      link.classList.add('navbar-nav__link--active');
      link.setAttribute('aria-current', 'page');
      matched = true;
    } else {
      link.classList.remove('navbar-nav__link--active');
      link.removeAttribute('aria-current');
    }
  });

  // fallback to first if nothing matched (optional)
  if (!matched && navLinks.length) {
    navLinks[0].classList.add('navbar-nav__link--active');
    navLinks[0].setAttribute('aria-current', 'page');
  }
});
