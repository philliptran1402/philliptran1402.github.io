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


  /* ── custom cursor ───────────────────────────────
     A dot that tracks exactly plus a reticle that lags behind. Enabled only
     on fine-pointer devices and only from JS, so the native cursor survives
     a script failure. Disabled entirely under reduced motion.             */
  var fine = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (fine && !reduced) {
    var dot = document.createElement('div'); dot.className = 'cur-dot';
    var ring = document.createElement('div'); ring.className = 'cur-ring';
    document.body.appendChild(dot); document.body.appendChild(ring);
    document.documentElement.classList.add('cur');

    var mx = innerWidth / 2, my = innerHeight / 2, rx = mx, ry = my;
    addEventListener('mousemove', function (e) {
      mx = e.clientX; my = e.clientY;
      dot.style.transform = 'translate(' + mx + 'px,' + my + 'px)';
    }, { passive: true });

    (function loop() {
      rx += (mx - rx) * 0.16;            // lerp: the reticle trails the dot
      ry += (my - ry) * 0.16;
      ring.style.transform = 'translate(' + rx + 'px,' + ry + 'px)';
      requestAnimationFrame(loop);
    })();

    var root = document.documentElement;
    addEventListener('mouseover', function (e) {
      if (e.target.closest && e.target.closest('a,button')) root.classList.add('cur-on');
    }, { passive: true });
    addEventListener('mouseout', function (e) {
      if (e.target.closest && e.target.closest('a,button')) root.classList.remove('cur-on');
    }, { passive: true });
    addEventListener('mousedown', function () { root.classList.add('cur-down'); }, { passive: true });
    addEventListener('mouseup', function () { root.classList.remove('cur-down'); }, { passive: true });
    addEventListener('mouseleave', function () { dot.style.opacity = ring.style.opacity = '0'; });
    addEventListener('mouseenter', function () { dot.style.opacity = ring.style.opacity = ''; });
  }

  /* ── sound ───────────────────────────────────────
     On by default, no visible toggle. Tones are synthesised with the Web
     Audio API — no files, no CDN.

     Browsers will NOT produce sound before the visitor interacts with the
     page; that is an autoplay policy, not something code can bypass. So the
     AudioContext is created on the first real gesture and everything after
     that is audible. Press M to mute — the choice persists.              */
  (function () {
    var on = true, ctx = null, lastTick = 0;
    try { if (localStorage.getItem('snd') === 'off') on = false; } catch (e) {}

    var beep = function (freq, dur, vol, type) {
      if (!on) return;
      try {
        if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
        if (ctx.state === 'suspended') ctx.resume();
        var o = ctx.createOscillator(), g = ctx.createGain(), now = ctx.currentTime;
        o.type = type || 'sine';
        o.frequency.setValueAtTime(freq, now);
        g.gain.setValueAtTime(0, now);
        g.gain.linearRampToValueAtTime(vol, now + 0.008);
        g.gain.exponentialRampToValueAtTime(0.0001, now + dur);
        o.connect(g); g.connect(ctx.destination);
        o.start(now); o.stop(now + dur + 0.02);
      } catch (e) { /* audio unavailable — ignore */ }
    };

    document.addEventListener('mouseover', function (e) {
      if (!on || !e.target.closest || !e.target.closest('a,button')) return;
      var t = Date.now();
      if (t - lastTick < 110) return;          // throttle: no machine-gunning
      lastTick = t;
      beep(1500, 0.028, 0.022, 'square');
    }, { passive: true });

    document.addEventListener('click', function (e) {
      if (!on || !e.target.closest) return;
      if (e.target.closest('a,button')) beep(660, 0.06, 0.04, 'triangle');
    }, { passive: true });

    // escape hatch: M mutes / unmutes
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'm' && e.key !== 'M') return;
      if (/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) return;
      on = !on;
      try { localStorage.setItem('snd', on ? 'on' : 'off'); } catch (err) {}
      if (on) beep(880, 0.07, 0.05);
    });
  })();

  /* ── copy to clipboard ───────────────────────────
     Any [data-copy] button copies its value and confirms in place. Falls back
     to a hidden textarea where the async Clipboard API is unavailable (it
     needs a secure context, which file:// is not).                        */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('.copy');
    if (!btn) return;
    e.preventDefault();
    var text = btn.dataset.copy || '';
    var done = function () {
      var old = btn.textContent;
      btn.textContent = 'Copied';
      btn.classList.add('done');
      setTimeout(function () { btn.textContent = old; btn.classList.remove('done'); }, 1600);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () {});
    } else {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (err) {}
      ta.remove();
    }
  });

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
