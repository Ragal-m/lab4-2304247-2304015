(() => {
  const root = document.documentElement;
  const preference = window.matchMedia('(prefers-color-scheme: dark)');
  let chosen = null;
  try { chosen = localStorage.getItem('theme'); } catch (_) {}

  function apply(dark) {
    root.classList.toggle('dark', dark);
    root.style.colorScheme = dark ? 'dark' : 'light';
    const button = document.getElementById('theme-toggle');
    if (button) {
      button.textContent = dark ? '\u2600\uFE0F Light mode' : '\uD83C\uDF19 Dark mode';
      button.setAttribute('aria-pressed', String(dark));
      button.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
    }
  }

  function currentTheme() {
    return chosen === 'dark' || (chosen !== 'light' && preference.matches);
  }

  apply(currentTheme());
  document.addEventListener('DOMContentLoaded', () => {
    apply(currentTheme());
    const button = document.getElementById('theme-toggle');
    if (button) button.addEventListener('click', () => {
      const dark = !root.classList.contains('dark');
      chosen = dark ? 'dark' : 'light';
      try { localStorage.setItem('theme', chosen); } catch (_) {}
      apply(dark);
    });
  });
  preference.addEventListener('change', () => {
    if (chosen !== 'dark' && chosen !== 'light') apply(preference.matches);
  });
  window.addEventListener('storage', event => {
    if (event.key === 'theme' || event.key === null) {
      chosen = event.newValue;
      apply(currentTheme());
    }
  });
})();
