/* ═══ Phi Tran — shared behaviour ════════════════════
   Clock · menu · scroll reveal · text scramble ·
   page-transition wipe · work-page filters.
   No framework, no dependencies. Everything degrades:
   with JS off the page is fully readable, and every
   animation is disabled under prefers-reduced-motion.
   ════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var reduced = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── live clock, Da Nang ─────────────────────────── */
  var clock = document.getElementById('clock');
  if (clock) {
    var tick = function () {
      clock.textContent = new Date().toLocaleTimeString('en-US', {
        timeZone: 'Asia/Ho_Chi_Minh', hour: '2-digit', minute: '2-digit', hour12: true
      });
    };
    tick();
    setInterval(tick, 10000);
  }

  /* ── menu overlay ────────────────────────────────── */
  var panel = document.getElementById('panel'),
      scrim = document.getElementById('scrim'),
      openBtn = document.getElementById('open'),
      closeBtn = document.getElementById('close');

  if (panel && scrim) {
    var shut = function () { panel.classList.remove('on'); scrim.classList.remove('on'); };
    if (openBtn) openBtn.addEventListener('click', function () {
      panel.classList.add('on'); scrim.classList.add('on');
    });
    if (closeBtn) closeBtn.addEventListener('click', shut);
    scrim.addEventListener('click', shut);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') shut(); });
  }

  /* ── scroll reveal ───────────────────────────────── */
  var rv = document.querySelectorAll('.rv');
  if (!rv.length) { /* nothing */ }
  else if (reduced || !('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(rv, function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -60px 0px', threshold: 0.08 });
    Array.prototype.forEach.call(rv, function (el) { io.observe(el); });
  }

  /* ── text scramble ───────────────────────────────── */
  var GLYPHS = '#$%&/\\<>[]{}*+=_?0123456789ABCDEFXYZ';
  function scramble(el, done) {
    var final = el.dataset.text || el.textContent;
    if (reduced) { el.textContent = final; if (done) done(); return; }
    var frame = 0, total = 22;
    var timer = setInterval(function () {
      var out = '', settled = Math.floor((frame / total) * final.length);
      for (var i = 0; i < final.length; i++) {
        if (final[i] === ' ') { out += ' '; continue; }
        out += i < settled ? final[i] : GLYPHS[(Math.random() * GLYPHS.length) | 0];
      }
      el.textContent = out;
      if (++frame > total) { clearInterval(timer); el.textContent = final; if (done) done(); }
    }, 38);
  }
  var scr = document.querySelectorAll('[data-scramble]');
  Array.prototype.forEach.call(scr, function (el, i) {
    el.dataset.text = el.textContent;
    if (reduced) return;
    el.textContent = '';
    setTimeout(function () { scramble(el); }, 380 + i * 170);
  });
  // re-scramble on hover
  Array.prototype.forEach.call(scr, function (el) {
    el.addEventListener('mouseenter', function () {
      if (!el.dataset.busy) { el.dataset.busy = '1'; scramble(el, function () { delete el.dataset.busy; }); }
    });
  });

  /* ── page-transition wipe ────────────────────────── */
  if (!reduced) {
    var wipe = document.createElement('div');
    wipe.className = 'wipe';
    document.body.appendChild(wipe);
    setTimeout(function () { wipe.remove(); }, 700);

    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a');
      if (!a) return;
      var href = a.getAttribute('href') || '';
      var internal = href && !href.startsWith('#') && !href.startsWith('mailto:') &&
                     !/^https?:/i.test(href) && a.target !== '_blank';
      if (!internal) return;
      e.preventDefault();
      // opening the site from disk: a directory URL lists files instead of
      // serving index.html, so point at the file directly in that case only.
      if (location.protocol === 'file:' && href.endsWith('/')) href += 'index.html';
      var w = document.createElement('div');
      w.className = 'wipe out';
      document.body.appendChild(w);
      setTimeout(function () { window.location.href = href; }, 380);
    });
  }

  /* ── work page: category filter ──────────────────── */
  var filters = document.querySelectorAll('.filters button');
  var cards = document.querySelectorAll('.card');
  if (filters.length && cards.length) {
    var empty = document.querySelector('.empty');
    Array.prototype.forEach.call(filters, function (btn) {
      btn.addEventListener('click', function () {
        var want = btn.dataset.filter;
        Array.prototype.forEach.call(filters, function (b) {
          b.setAttribute('aria-pressed', String(b === btn));
        });
        var shown = 0;
        Array.prototype.forEach.call(cards, function (c) {
          var match = want === 'all' || c.dataset.cat === want;
          c.classList.toggle('hide', !match);
          if (match) shown++;
        });
        if (empty) empty.style.display = shown ? 'none' : 'block';
      });
    });
  }
})();
