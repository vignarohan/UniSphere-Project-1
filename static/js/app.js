'use strict';

const menuButton = document.getElementById('nav-toggle');
const sidebar = document.getElementById('sidebar');
const backdrop = document.getElementById('nav-backdrop');
const mobile = window.matchMedia('(max-width: 760px)');
function setMenu(open) {
  if (!sidebar) return;
  sidebar.classList.toggle('open', open);
  sidebar.inert = mobile.matches && !open;
  menuButton?.setAttribute('aria-expanded', String(open));
  menuButton?.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  if (backdrop) backdrop.hidden = !open;
}
menuButton?.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
backdrop?.addEventListener('click', () => setMenu(false));
mobile.addEventListener('change', () => setMenu(false));
document.addEventListener('keydown', event => { if (event.key === 'Escape') setMenu(false); });
setMenu(false);

const helper = document.getElementById('helper-dialog');
document.getElementById('helper-open')?.addEventListener('click', () => helper.showModal());
document.getElementById('helper-close')?.addEventListener('click', () => helper.close());
const results = document.getElementById('helper-results');
document.querySelectorAll('[data-lookup]').forEach(button => {
  button.addEventListener('click', async () => {
    document.querySelectorAll('[data-lookup]').forEach(item => { item.disabled = true; });
    results.textContent = 'Looking up your records…';
    try {
      const response = await fetch(`${results.dataset.endpoint}?topic=${encodeURIComponent(button.dataset.lookup)}`, { credentials: 'same-origin', cache: 'no-store', headers: { Accept: 'application/json' } });
      if (!response.ok || response.redirected) throw new Error('Lookup unavailable');
      const data = await response.json();
      results.replaceChildren();
      const heading = document.createElement('p');
      heading.className = 'helper-results-title';
      heading.textContent = data.heading;
      results.appendChild(heading);
      for (const item of data.items) {
        const link = document.createElement('a');
        link.className = 'helper-result';
        link.href = item.url;
        link.textContent = item.title;
        const detail = document.createElement('span');
        detail.textContent = item.detail;
        link.appendChild(detail);
        results.appendChild(link);
      }
    } catch {
      results.textContent = 'Your records could not be loaded. Check your connection and sign in again if needed.';
    } finally {
      document.querySelectorAll('[data-lookup]').forEach(item => { item.disabled = false; });
    }
  });
});

let installPrompt;
window.addEventListener('beforeinstallprompt', event => { event.preventDefault(); installPrompt = event; });
const installDialog = document.getElementById('install-dialog');
document.querySelectorAll('.install-trigger').forEach(button => {
  button.addEventListener('click', async () => {
    if (window.matchMedia('(display-mode: standalone)').matches) {
      installDialog.querySelector('p').textContent = 'UniSphere is already running in an app window.';
      installDialog.showModal();
    } else if (installPrompt) {
      try { await installPrompt.prompt(); await installPrompt.userChoice; }
      finally { installPrompt = null; }
    } else { installDialog.showModal(); }
  });
});
document.getElementById('install-close')?.addEventListener('click', () => installDialog.close());
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js').catch(() => {
      // The portal remains fully usable when installation support is unavailable.
    });
  });
}
