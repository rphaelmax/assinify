(() => {
  const LOGO_TOKEN = 'pk_aFebUAI6TXi3KllA2BUauA';

  const cards = [
    {
      total: 74.70,
      items: [
        { name: 'Netflix', days: 3, amount: 39.90 },
        { name: 'Spotify', days: 12, amount: 21.90 },
        { name: 'iCloud+', days: 18, amount: 12.90 }
      ]
    },
    {
      total: 96.70,
      items: [
        { name: 'Netflix', days: 5, amount: 39.90 },
        { name: 'Prime Video', days: 8, amount: 19.90 },
        { name: 'Spotify', days: 14, amount: 21.90 },
        { name: 'Google One', days: 22, amount: 14.90 }
      ]
    },
    {
      total: 129.70,
      items: [
        { name: 'Disney+', days: 2, amount: 43.90 },
        { name: 'Spotify', days: 9, amount: 21.90 },
        { name: 'Canva', days: 16, amount: 34.90 },
        { name: 'iCloud+', days: 25, amount: 12.90 }
      ]
    },
    {
      total: 83.80,
      items: [
        { name: 'YouTube Premium', days: 4, amount: 41.90 },
        { name: 'Spotify', days: 11, amount: 21.90 },
        { name: 'Dropbox', days: 20, amount: 19.90 }
      ]
    }
  ];

  const money = value => value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  });

  const DOMAINS = {
    "Netflix": "netflix.com",
    "Spotify": "spotify.com",
    "iCloud+": "icloud.com",
    "Prime Video": "primevideo.com",
    "Google One": "one.google.com",
    "Disney+": "disneyplus.com",
    "Canva": "canva.com",
    "YouTube Premium": "youtube.com",
    "Dropbox": "dropbox.com"
  };

  const logoUrl = name => {
    const domain = DOMAINS[name] || name.toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9\s]/g, '')
      .trim()
      .replace(/\s+/g, '') + '.com';

    return `https://img.logo.dev/${domain}?token=${LOGO_TOKEN}&format=webp&retina=true`;
  };

  function logoMarkup(name) {
    const safeName = name.replace(/"/g, '&quot;');
    return `
      <div class="auth-preview-logo" aria-hidden="true">
        <img
          src="${logoUrl(name)}"
          alt="${safeName}"
          loading="eager"
          decoding="async"
          onerror="this.classList.add('is-broken');"
        >
      </div>
    `;
  }

  function render(index) {
    const card = document.querySelector('.auth-preview-card');
    if (!card) return;

    const data = cards[index % cards.length];
    const value = card.querySelector('.auth-preview-value');
    const list = card.querySelector('.auth-preview-items');

    card.classList.add('is-changing');

    window.setTimeout(() => {
      value.textContent = money(data.total);
      list.innerHTML = data.items.map(item => `
        <div class="auth-preview-item">
          ${logoMarkup(item.name)}
          <div class="auth-preview-info">
            <div class="auth-preview-name">${item.name}</div>
            <div class="auth-preview-meta">Renova em ${item.days} dias</div>
          </div>
          <div class="auth-preview-amount">${money(item.amount)}</div>
        </div>
      `).join('');

      card.classList.remove('is-changing');
    }, 180);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const card = document.querySelector('.auth-preview-card');
    if (!card) return;

    const label = card.querySelector('.auth-preview-label');
    if (label) label.textContent = 'Gasto mensal estimado';

    render(0);
    let index = 1;
    window.setInterval(() => render(index++), 3600);
  });
})();
