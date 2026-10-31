/* ==========================================================================
   Shared site runtime: chrome (announcement, header, footer), copy binding,
   product artwork placeholders, cart store + drawer, newsletter forms.
   Depends on window.SITE from config.js. No frameworks, no build step.
   ========================================================================== */
(function () {
  'use strict';
  var S = window.SITE;
  if (!S) { console.error('config.js must load before app.js'); return; }

  /* ---------- helpers ---------- */
  var esc = function (v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  var moneyFmt = new Intl.NumberFormat(S.currency.locale, { style: 'currency', currency: S.currency.code });
  var money = function (n) { return moneyFmt.format(n); };
  var tokens = {
    brand: S.brand.name, email: S.brand.email, city: S.brand.city, founded: S.brand.founded,
    freeShipping: money(S.shipping.freeShipping), flatRate: money(S.shipping.flatRate),
    returnDays: S.shipping.returnDays, processingDays: S.shipping.processingDays
  };
  var fill = function (str) {
    return String(str).replace(/\[BRAND NAME\]/g, S.brand.name).replace(/\{(\w+)\}/g, function (m, k) {
      return Object.prototype.hasOwnProperty.call(tokens, k) ? tokens[k] : m;
    });
  };
  var get = function (path) {
    return path.split('.').reduce(function (o, k) { return o == null ? undefined : o[k]; }, S);
  };
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  var ICON = {
    bag: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 8h14l-1.2 11.2a2 2 0 0 1-2 1.8H8.2a2 2 0 0 1-2-1.8L5 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>',
    menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/></svg>',
    arrow: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    mark: '<svg class="logo-mark" viewBox="0 0 32 32" aria-hidden="true"><path d="M4 26 L14 6 H18 L10 26 Z" fill="#2A2420"/><path d="M14 26 L22 10 H28 L20 26 Z" fill="#B08D57"/></svg>'
  };

  /* ---------- catalogue ---------- */
  var products = S.products;
  var byId = {};
  products.forEach(function (p) { byId[p.id] = p; });
  var categoryLabel = function (id) {
    for (var i = 0; i < S.categories.length; i++) if (S.categories[i].id === id) return S.categories[i].label;
    return id;
  };

  /* Placeholder product artwork (swap by adding real photos to product.images). */
  var artSeq = 0;
  var SILHOUETTE = {
    sleeves: 'M146 62 Q200 46 254 62 L238 436 Q200 450 162 436 Z',
    tops: 'M140 78 L176 66 Q200 92 224 66 L260 78 L342 132 L332 336 L300 336 L294 186 L290 438 L110 438 L106 186 L100 336 L68 336 L58 132 Z',
    leggings: 'M128 58 L272 58 L288 442 L232 442 L206 176 L194 176 L168 442 L112 442 Z'
  };
  function patternDef(id, design, accent) {
    switch (design) {
      case 'circuit':
        return '<pattern id="' + id + '" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M0 30 H18 L30 18 H60 M30 60 V42 L42 30" fill="none" stroke="' + accent + '" stroke-width="2"/><circle cx="30" cy="18" r="3" fill="' + accent + '"/><circle cx="42" cy="30" r="3" fill="' + accent + '"/></pattern>';
      case 'glitch':
        return '<pattern id="' + id + '" width="400" height="64" patternUnits="userSpaceOnUse"><rect x="0" y="10" width="180" height="4" fill="' + accent + '"/><rect x="220" y="28" width="130" height="7" fill="' + accent + '" opacity=".8"/><rect x="60" y="48" width="90" height="3" fill="#2A2420" opacity=".5"/><rect x="290" y="54" width="70" height="2" fill="#B08D57" opacity=".7"/></pattern>';
      case 'grid':
        return '<pattern id="' + id + '" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0 V22 M0 22 H22" fill="none" stroke="' + accent + '" stroke-width="1.2" opacity=".75"/></pattern>';
      default:
        return '<pattern id="' + id + '" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="' + accent + '" stroke-width="1" opacity=".35"/></pattern>';
    }
  }
  function productArt(p, colourKey, view) {
    var c = S.colours[colourKey] || S.colours[p.colours[0]];
    var n = ++artSeq;
    var pid = 'pat' + n, cid = 'clip' + n, gid = 'glow' + n;
    var path = SILHOUETTE[p.category] || SILHOUETTE.tops;
    var zoom = view === 'detail' ? ' transform="translate(-200 -250) scale(2)"' : view === 'back' ? ' transform="translate(400 0) scale(-1 1)"' : '';
    var label = view === 'detail' ? 'Detail' : view === 'back' ? 'Back' : 'Front';
    return '<svg viewBox="0 0 400 500" role="img" aria-label="' + esc(p.name + ', ' + c.label + ', ' + label.toLowerCase() + ' view placeholder') + '" preserveAspectRatio="xMidYMid slice">' +
      '<defs>' + patternDef(pid, p.design, c.accent) +
      '<clipPath id="' + cid + '"><path d="' + path + '"/></clipPath>' +
      '<radialGradient id="' + gid + '" cx="50%" cy="40%" r="70%"><stop offset="0" stop-color="' + c.accent + '" stop-opacity=".22"/><stop offset="1" stop-color="#EFE7DA" stop-opacity="0"/></radialGradient></defs>' +
      '<rect width="400" height="500" fill="#EFE7DA"/><rect width="400" height="500" fill="url(#' + gid + ')"/>' +
      '<g' + zoom + '><path d="' + path + '" fill="#FFFFFF" stroke="' + c.accent + '" stroke-width="2"/>' +
      '<g clip-path="url(#' + cid + ')"><rect width="400" height="500" fill="url(#' + pid + ')"/></g></g>' +
      '<text x="16" y="484" font-family="Orbitron, sans-serif" font-size="11" letter-spacing="3" fill="#6B6052">' + esc(label.toUpperCase()) + ' · PHOTO PLACEHOLDER</text>' +
      '</svg>';
  }
  function productMedia(p, colourKey, index) {
    var imgs = p.images || [];
    if (imgs.length) {
      var src = imgs[Math.min(index || 0, imgs.length - 1)];
      return '<img src="' + esc(src) + '" alt="' + esc(p.name) + '" loading="lazy" decoding="async">';
    }
    return productArt(p, colourKey, ['front', 'back', 'detail'][index || 0] || 'front');
  }
  function priceHTML(p) {
    return '<span>' + money(p.price) + '</span>' + (p.compareAt ? '<s><span class="sr-only">Was </span>' + money(p.compareAt) + '</s>' : '');
  }
  function cardHTML(p) {
    var url = 'product.html?id=' + encodeURIComponent(p.id);
    return '<article class="card">' +
      '<a class="card-media" href="' + url + '" tabindex="-1" aria-hidden="true">' + (p.badge ? '<span class="badge">' + esc(p.badge) + '</span>' : '') + productMedia(p, p.colours[0], 0) + '</a>' +
      '<h3><a href="' + url + '">' + esc(p.name) + '</a></h3>' +
      '<p class="price">' + priceHTML(p) + '</p>' +
      '<ul class="swatches" aria-label="Colours">' + p.colours.map(function (k) {
        return '<li class="swatch-dot" style="background:' + S.colours[k].accent + '" title="' + esc(S.colours[k].label) + '"><span class="sr-only">' + esc(S.colours[k].label) + '</span></li>';
      }).join('') + '</ul>' +
      '<p class="card-sizes"><span class="sr-only">Sizes: </span>' + p.sizes.join(' · ') + '</p>' +
      '</article>';
  }

  /* ---------- chrome ---------- */
  var page = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  var qs = new URLSearchParams(location.search);
  function isCurrent(href) {
    var parts = href.split('?');
    if (parts[0] !== page) return false;
    var hp = new URLSearchParams(parts[1] || '');
    return (hp.get('category') || '') === (qs.get('category') || '');
  }

  function renderChrome() {
    var header = $('[data-header]');
    if (header) {
      header.outerHTML =
        '<div class="announce" role="region" aria-label="Announcement"><span>' + esc(fill(S.announcement)) + '</span></div>' +
        '<header class="site-header"><div class="container bar">' +
        '<a class="logo" href="index.html">' + ICON.mark + '<span>' + esc(S.brand.name) + '</span></a>' +
        '<nav class="main-nav" aria-label="Main"><ul>' + S.nav.map(function (n) {
          return '<li><a href="' + esc(n.href) + '"' + (isCurrent(n.href) ? ' aria-current="page"' : '') + '>' + esc(n.label) + '</a></li>';
        }).join('') + '</ul></nav>' +
        '<button class="icon-btn" type="button" data-cart-open aria-haspopup="dialog" aria-controls="cart-drawer" aria-expanded="false" aria-label="Open cart, 0 items">' + ICON.bag + '<span class="cart-count" data-cart-count aria-hidden="true">0</span></button>' +
        '<button class="icon-btn menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="Menu">' + ICON.menu + '</button>' +
        '</div>' +
        '<nav id="mobile-nav" class="mobile-nav" aria-label="Main" hidden><ul>' + S.nav.concat([{ label: 'Shipping & FAQ', href: 'shipping.html' }, { label: 'Contact', href: 'contact.html' }]).map(function (n) {
          return '<li><a href="' + esc(n.href) + '"' + (isCurrent(n.href) ? ' aria-current="page"' : '') + '>' + esc(n.label) + '</a></li>';
        }).join('') + '</ul></nav></header>';
    }

    var footer = $('[data-footer]');
    if (footer) {
      var col = function (title, links) {
        return '<div><h2>' + esc(title) + '</h2><ul>' + links.map(function (l) {
          return '<li><a href="' + esc(l.href) + '"' + (l.ext ? ' rel="noopener" target="_blank"' : '') + '>' + esc(l.label) + (l.ext ? '<span class="sr-only"> (opens in a new tab)</span>' : '') + '</a></li>';
        }).join('') + '</ul></div>';
      };
      footer.outerHTML =
        '<footer class="site-footer"><div class="container">' +
        '<div class="footer-grid">' +
        '<div style="display:grid;gap:16px;align-content:start"><a class="logo" href="index.html">' + ICON.mark + '<span>' + esc(S.brand.name) + '</span></a>' +
        '<p class="muted">' + esc(fill(S.copy.footer.blurb)) + '</p>' +
        '<form class="inline-form" data-newsletter novalidate><div class="field"><label class="sr-only" for="footer-email">Email</label><input class="input" id="footer-email" name="email" type="email" autocomplete="email" placeholder="Email for drop alerts" required></div><button class="btn btn-ghost" type="submit">Join</button></form>' +
        '<p class="form-status" role="status"></p></div>' +
        col('Shop', S.categories.map(function (c) { return { label: c.label, href: 'shop.html?category=' + c.id }; }).concat([{ label: 'Shop all', href: 'shop.html' }, { label: 'Lookbook', href: 'lookbook.html' }])) +
        col('Help', [{ label: 'Shipping', href: 'shipping.html#shipping' }, { label: 'Returns & exchanges', href: 'shipping.html#returns' }, { label: 'FAQ', href: 'shipping.html#faq' }, { label: 'Size guide', href: 'product.html?id=' + products[0].id + '#size-guide' }, { label: 'Contact', href: 'contact.html' }]) +
        col('Follow', S.social.map(function (s) { return { label: s.label, href: s.url, ext: true }; })) +
        '</div>' +
        '<div class="footer-bottom"><span>© <span data-year></span> ' + esc(S.brand.name) + '. All rights reserved.</span>' +
        '<span><a href="shipping.html#returns">Refund policy</a> · <a href="contact.html">Privacy policy [ADD]</a> · <a href="contact.html">Terms of service [ADD]</a> · <a href="CREDITS.md">Photo credits</a></span></div>' +
        '</div></footer>';
      var y = $('[data-year]'); if (y) y.textContent = new Date().getFullYear();
    }

    document.body.insertAdjacentHTML('beforeend',
      '<div class="drawer-scrim" data-cart-scrim data-open="false" aria-hidden="true"></div>' +
      '<aside id="cart-drawer" class="drawer" role="dialog" aria-modal="true" aria-labelledby="cart-title" data-open="false">' +
      '<div class="drawer-head"><h2 id="cart-title" class="h-md">Your cart</h2><button class="icon-btn" type="button" data-cart-close aria-label="Close cart">' + ICON.close + '</button></div>' +
      '<div class="drawer-body"><div class="ship-meter"><p data-ship-msg></p><div class="ship-track" role="progressbar" aria-label="Progress to free shipping" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" data-ship-bar><div class="ship-fill" data-ship-fill></div></div></div>' +
      '<ul class="lines" data-cart-lines aria-label="Cart items" style="list-style:none"></ul>' +
      '<div class="empty-cart" data-cart-empty><p>Your cart is empty.</p><a class="btn btn-neon" href="shop.html">Shop the drop</a></div></div>' +
      '<div class="drawer-foot"><div class="totals"><div><span class="muted">Subtotal</span><span data-subtotal>' + money(0) + '</span></div><div><span class="muted">Shipping</span><span data-shipping>—</span></div><div class="grand"><span>Total</span><span data-total>' + money(0) + '</span></div></div>' +
      '<button class="btn btn-neon btn-block" type="button" data-checkout disabled>Checkout</button><p class="muted" style="font-size:.85rem" role="status" data-checkout-msg></p></div>' +
      '</aside>' +
      '<div class="toast" role="status" aria-live="polite" data-toast></div>' +
      '<div class="sr-only" aria-live="polite" data-live></div>');

    var toggle = $('.menu-toggle'), mnav = $('#mobile-nav');
    if (toggle && mnav) toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      toggle.setAttribute('aria-label', open ? 'Menu' : 'Close menu');
      toggle.innerHTML = open ? ICON.menu : ICON.close;
      mnav.hidden = open;
    });
  }

  /* ---------- copy binding: data-c="copy.home.heroTitle" ---------- */
  function bindCopy(root) {
    $$('[data-c]', root).forEach(function (el) {
      var v = get(el.getAttribute('data-c'));
      if (v == null) return;
      el.textContent = fill(v);
      if (el.classList.contains('glitch')) el.setAttribute('data-text', el.textContent);
    });
    $$('[data-c-list]', root).forEach(function (el) {
      var v = get(el.getAttribute('data-c-list'));
      if (!Array.isArray(v)) return;
      el.innerHTML = v.map(function (t) { return '<li>' + esc(fill(t)) + '</li>'; }).join('');
    });
    $$('[data-brand]', root).forEach(function (el) { el.textContent = S.brand.name; });
    document.title = fill(document.title);
  }

  /* ---------- live region + toast ---------- */
  function announce(msg) {
    var live = $('[data-live]'); if (!live) return;
    live.textContent = ''; setTimeout(function () { live.textContent = msg; }, 40);
  }
  var toastTimer;
  function toast(msg) {
    var t = $('[data-toast]'); if (!t) return;
    t.textContent = msg; t.dataset.show = 'true';
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { t.dataset.show = 'false'; }, 2600);
  }

  /* ---------- cart store: serialized action queue ---------- */
  var KEY = 'neon.cart.v1', MAXQ = 10;
  var state = { lines: [] }, queue = [], draining = false, listeners = [];
  var lineKey = function (id, colour, size) { return id + '|' + colour + '|' + size; };

  function reduce(s, a) {
    var L = s.lines;
    switch (a.type) {
      case 'ADD': {
        var k = lineKey(a.id, a.colour, a.size), qty = a.qty || 1;
        if (L.some(function (l) { return l.key === k; })) {
          return { lines: L.map(function (l) { return l.key === k ? { key: l.key, id: l.id, colour: l.colour, size: l.size, qty: Math.min(l.qty + qty, MAXQ) } : l; }) };
        }
        return { lines: L.concat([{ key: k, id: a.id, colour: a.colour, size: a.size, qty: Math.min(qty, MAXQ) }]) };
      }
      case 'QTY':
        return { lines: L.map(function (l) { return l.key === a.key ? { key: l.key, id: l.id, colour: l.colour, size: l.size, qty: Math.max(1, Math.min(a.qty, MAXQ)) } : l; }) };
      case 'REMOVE':
        return { lines: L.filter(function (l) { return l.key !== a.key; }) };
      case 'LOAD':
        return { lines: a.lines };
      default:
        return s;
    }
  }
  function dispatch(action) {
    queue.push(action);
    if (draining) return;
    draining = true;
    try {
      while (queue.length) state = Object.freeze(reduce(state, queue.shift()));
    } finally { draining = false; }
    try { localStorage.setItem(KEY, JSON.stringify(state.lines)); } catch (e) { /* private mode: cart stays in memory */ }
    listeners.forEach(function (fn) { fn(state); });
  }
  function load() {
    try {
      var raw = JSON.parse(localStorage.getItem(KEY) || '[]');
      if (!Array.isArray(raw)) return;
      dispatch({ type: 'LOAD', lines: raw.filter(function (l) {
        var p = l && byId[l.id];
        return p && p.colours.indexOf(l.colour) > -1 && p.sizes.indexOf(l.size) > -1 && l.qty > 0;
      }).map(function (l) { return { key: lineKey(l.id, l.colour, l.size), id: l.id, colour: l.colour, size: l.size, qty: Math.min(l.qty | 0, MAXQ) }; }) });
    } catch (e) { /* ignore corrupted storage */ }
  }
  function totals(s) {
    var count = 0, sub = 0;
    s.lines.forEach(function (l) { count += l.qty; sub += byId[l.id].price * l.qty; });
    var ship = count === 0 ? 0 : (sub >= S.shipping.freeShipping ? 0 : S.shipping.flatRate);
    return { count: count, sub: sub, ship: ship, total: sub + ship };
  }

  function renderCart(s) {
    var t = totals(s);
    $$('[data-cart-count]').forEach(function (b) { b.textContent = t.count; b.dataset.show = t.count > 0 ? 'true' : 'false'; });
    $$('[data-cart-open]').forEach(function (b) { b.setAttribute('aria-label', 'Open cart, ' + t.count + ' item' + (t.count === 1 ? '' : 's')); });
    var list = $('[data-cart-lines]'); if (!list) return;
    list.innerHTML = s.lines.map(function (l) {
      var p = byId[l.id], c = S.colours[l.colour], desc = p.name + ', ' + c.label + ', size ' + l.size;
      return '<li class="line" data-key="' + esc(l.key) + '">' +
        '<a class="line-thumb" href="product.html?id=' + encodeURIComponent(p.id) + '" tabindex="-1" aria-hidden="true">' + productMedia(p, l.colour, 0) + '</a>' +
        '<div><h3><a href="product.html?id=' + encodeURIComponent(p.id) + '">' + esc(p.name) + '</a></h3>' +
        '<p class="meta">' + esc(c.label) + ' · ' + esc(l.size) + ' · ' + money(p.price) + '</p>' +
        '<div class="qty" role="group" aria-label="' + esc('Quantity, ' + desc) + '"><button type="button" data-act="dec" aria-label="Decrease quantity"' + (l.qty <= 1 ? ' disabled' : '') + '>−</button><output>' + l.qty + '</output><button type="button" data-act="inc" aria-label="Increase quantity"' + (l.qty >= MAXQ ? ' disabled' : '') + '>+</button></div></div>' +
        '<div class="right"><strong>' + money(p.price * l.qty) + '</strong><button class="icon-btn" type="button" data-act="remove" aria-label="' + esc('Remove ' + desc) + '">' + ICON.trash + '</button></div>' +
        '</li>';
    }).join('');
    $('[data-cart-empty]').hidden = s.lines.length > 0;
    $('[data-subtotal]').textContent = money(t.sub);
    $('[data-shipping]').textContent = t.count === 0 ? '—' : (t.ship === 0 ? 'Free' : money(t.ship));
    $('[data-total]').textContent = money(t.total);
    var left = Math.max(0, S.shipping.freeShipping - t.sub), pct = Math.min(100, Math.round(t.sub / S.shipping.freeShipping * 100));
    $('[data-ship-msg]').textContent = left > 0 ? 'Add ' + money(left) + ' more for free shipping.' : 'You unlocked free shipping.';
    $('[data-ship-fill]').style.width = pct + '%';
    $('[data-ship-bar]').setAttribute('aria-valuenow', String(pct));
    var co = $('[data-checkout]'); co.disabled = t.count === 0;
    $('[data-checkout-msg]').textContent = '';
  }

  /* ---------- drawer ---------- */
  var lastFocus = null;
  function bg() { return $$('body > *:not(#cart-drawer):not([data-cart-scrim]):not([data-toast]):not([data-live]):not(script)'); }
  function openCart() {
    var d = $('#cart-drawer'); if (d.dataset.open === 'true') return;
    lastFocus = document.activeElement;
    d.dataset.open = 'true'; $('[data-cart-scrim]').dataset.open = 'true';
    $$('[data-cart-open]').forEach(function (b) { b.setAttribute('aria-expanded', 'true'); });
    bg().forEach(function (n) { n.setAttribute('inert', ''); });
    document.documentElement.style.overflow = 'hidden';
    setTimeout(function () { $('[data-cart-close]').focus(); }, 30);
  }
  function closeCart() {
    var d = $('#cart-drawer'); if (d.dataset.open !== 'true') return;
    d.dataset.open = 'false'; $('[data-cart-scrim]').dataset.open = 'false';
    $$('[data-cart-open]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    bg().forEach(function (n) { n.removeAttribute('inert'); });
    document.documentElement.style.overflow = '';
    var back = lastFocus && document.contains(lastFocus) ? lastFocus : $('[data-cart-open]');
    if (back) back.focus();
  }
  function wireCart() {
    document.addEventListener('click', function (e) {
      if (e.target.closest('[data-cart-open]')) { openCart(); return; }
      if (e.target.closest('[data-cart-close]') || e.target.closest('[data-cart-scrim]')) { closeCart(); return; }
      var act = e.target.closest('[data-act]');
      if (act && act.closest('[data-cart-lines]') && !act.disabled) {
        var li = act.closest('[data-key]'), key = li.getAttribute('data-key');
        var line = state.lines.filter(function (l) { return l.key === key; })[0]; if (!line) return;
        var a = act.getAttribute('data-act');
        if (a === 'remove') {
          var idx = $$('[data-cart-lines] > li').indexOf(li);
          dispatch({ type: 'REMOVE', key: key });
          announce('Item removed. Cart has ' + totals(state).count + ' items.');
          var rem = $$('[data-cart-lines] [data-act="remove"]');
          (rem[Math.min(idx, rem.length - 1)] || $('[data-cart-close]')).focus();
        } else {
          dispatch({ type: 'QTY', key: key, qty: line.qty + (a === 'inc' ? 1 : -1) });
          var row = $$('[data-cart-lines] > li').filter(function (n) { return n.getAttribute('data-key') === key; })[0];
          if (row) { var same = row.querySelector('[data-act="' + a + '"]'); (same && !same.disabled ? same : row.querySelector('[data-act="' + (a === 'inc' ? 'dec' : 'inc') + '"]')).focus(); }
          announce('Quantity ' + (line.qty + (a === 'inc' ? 1 : -1)) + '.');
        }
      }
      if (e.target.closest('[data-checkout]')) {
        $('[data-checkout-msg]').textContent = 'Checkout is not connected yet. Hook this button to Shopify, Snipcart or Stripe Payment Links (see README).';
      }
    });
    document.addEventListener('keydown', function (e) {
      var d = $('#cart-drawer'); if (!d || d.dataset.open !== 'true') return;
      if (e.key === 'Escape') { e.preventDefault(); closeCart(); return; }
      if (e.key !== 'Tab') return;
      var f = $$('a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])', d).filter(function (n) { return n.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (!d.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
      else if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  /* ---------- newsletter (no backend: validates and confirms) ---------- */
  function wireNewsletters() {
    $$('[data-newsletter]').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var input = form.querySelector('input[type="email"]');
        var status = form.parentElement.querySelector('.form-status');
        var ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim());
        input.setAttribute('aria-invalid', ok ? 'false' : 'true');
        if (status) status.textContent = ok ? fill(S.copy.footer.newsletterSuccess) : 'Enter a valid email address.';
        if (ok) form.reset(); else input.focus();
      });
    });
  }

  /* ---------- public API ---------- */
  window.Store = {
    S: S, esc: esc, fill: fill, money: money, byId: byId, products: products, categoryLabel: categoryLabel,
    productArt: productArt, productMedia: productMedia, priceHTML: priceHTML, cardHTML: cardHTML,
    add: function (id, colour, size, qty, opts) {
      var p = byId[id];
      dispatch({ type: 'ADD', id: id, colour: colour, size: size, qty: qty || 1 });
      var msg = 'Added ' + p.name + ' (' + S.colours[colour].label + ', ' + size + ') to cart.';
      announce(msg); if (!(opts && opts.quiet)) toast(msg);
    },
    openCart: openCart, announce: announce, toast: toast, icon: ICON
  };

  /* ---------- boot ---------- */
  renderChrome();
  bindCopy(document);
  listeners.push(renderCart);
  wireCart();
  wireNewsletters();
  load();
  renderCart(state);
})();
