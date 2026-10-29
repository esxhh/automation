/* Interactions: scroll reveal, pointer glow, tilt, ripple, sparkles, forms, calculator. */
(function () {
  'use strict';
  var root = document.documentElement;
  root.classList.add('js');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var COLORS = ['#19D3C5', '#37E08F', '#F6C945', '#FF8A1F', '#E5391F', '#7A3FD1'];

  /* ---------- scroll progress ---------- */
  var bar = $('#progress');
  function onScroll() {
    var max = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, window.scrollY / max) : 0) + ')';
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- responsive navigation + active section ---------- */
  var nav = $('.nav'), navToggle = $('.nav-toggle'), navLinks = $$('.links a[href^="#"]');
  function closeNav() {
    if (!nav || !navToggle) return;
    nav.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
  }
  if (nav && navToggle) {
    navLinks.forEach(function (link) { link.addEventListener('click', closeNav); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeNav(); });
    document.addEventListener('pointerdown', function (e) {
      if (!nav.contains(e.target)) closeNav();
    });
  }
  if ('IntersectionObserver' in window && navLinks.length) {
    var sections = navLinks.map(function (link) { return $(link.getAttribute('href')); }).filter(Boolean);
    var activeSection = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (link) {
          if (link.getAttribute('href') === '#' + entry.target.id) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-24% 0px -64% 0px' });
    sections.forEach(function (section) { activeSection.observe(section); });
  }

  /* ---------- scroll reveal ---------- */
  var reveals = $$('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.15 });
    reveals.forEach(function (el, i) {
      var sibs = $$('.reveal', el.parentElement);
      el.style.transitionDelay = (Math.max(0, sibs.indexOf(el)) * 90) + 'ms';
      io.observe(el);
    });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }
  var chat = $('#chat');
  if (chat) {
    if ('IntersectionObserver' in window && !reduce) {
      var cio = new IntersectionObserver(function (es) {
        if (es[0].isIntersecting) { chat.classList.add('in'); cio.disconnect(); }
      }, { threshold: 0.4 });
      cio.observe(chat);
    } else { chat.classList.add('in'); }
  }

  /* ---------- pointer glow + hero parallax ---------- */
  var hero = $('#hero'), heroArt = $('#heroArt'), raf = 0, px = 0, py = 0;
  function frame() {
    raf = 0;
    root.style.setProperty('--mx', px + 'px');
    root.style.setProperty('--my', py + 'px');
    if (heroArt && !reduce) {
      var r = hero.getBoundingClientRect();
      if (r.bottom > 0 && r.top < window.innerHeight) {
        var nx = (px / window.innerWidth - 0.5) * 2, ny = ((py - r.top) / r.height - 0.5) * 2;
        heroArt.style.setProperty('--rx', (nx * 18).toFixed(1));
        heroArt.style.setProperty('--ry', (ny * 14).toFixed(1));
      }
    }
  }
  window.addEventListener('pointermove', function (e) {
    px = e.clientX; py = e.clientY;
    if (!raf) raf = requestAnimationFrame(frame);
  }, { passive: true });
  window.addEventListener('pointerdown', function (e) {
    px = e.clientX; py = e.clientY;
    if (!raf) raf = requestAnimationFrame(frame);
  }, { passive: true });

  /* ---------- rotating words ---------- */
  var rot = $('#rot');
  if (rot && !reduce) {
    var words = [];
    try { words = JSON.parse(rot.getAttribute('data-words')); } catch (err) { /* ignore */ }
    var wi = 0;
    if (words.length > 1) {
      setInterval(function () {
        rot.classList.add('out');
        setTimeout(function () {
          wi = (wi + 1) % words.length;
          rot.textContent = words[wi];
          rot.classList.remove('out');
        }, 320);
      }, 2600);
    }
  }

  /* ---------- 3D tilt cards (mouse and touch) ---------- */
  if (!reduce) {
    $$('.tilt').forEach(function (card) {
      function move(e) {
        var r = card.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        card.style.transform = 'perspective(800px) rotateX(' + ((0.5 - y) * 9).toFixed(2) + 'deg) rotateY(' + ((x - 0.5) * 11).toFixed(2) + 'deg)';
        card.style.setProperty('--px', (x * 100) + '%');
        card.style.setProperty('--py', (y * 100) + '%');
      }
      function leave() { card.style.transform = ''; }
      card.addEventListener('pointermove', move);
      card.addEventListener('pointerdown', move);
      card.addEventListener('pointerleave', leave);
      card.addEventListener('pointerup', leave);
      card.addEventListener('pointercancel', leave);
    });

    /* ---------- magnetic buttons ---------- */
    $$('.magnetic').forEach(function (btn) {
      btn.addEventListener('pointermove', function (e) {
        if (e.pointerType === 'touch') return;
        var r = btn.getBoundingClientRect();
        var dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
        btn.style.transform = 'translate(' + (dx * 0.18).toFixed(1) + 'px,' + (dy * 0.28).toFixed(1) + 'px)';
      });
      btn.addEventListener('pointerleave', function () { btn.style.transform = ''; });
    });
  }

  /* ---------- button ripple ---------- */
  document.addEventListener('pointerdown', function (e) {
    var btn = e.target.closest && e.target.closest('.btn');
    if (!btn || reduce) return;
    var r = btn.getBoundingClientRect(), size = Math.max(r.width, r.height) * 2;
    var s = document.createElement('span');
    s.className = 'ripple';
    s.style.width = s.style.height = size + 'px';
    s.style.left = (e.clientX - r.left - size / 2) + 'px';
    s.style.top = (e.clientY - r.top - size / 2) + 'px';
    btn.appendChild(s);
    setTimeout(function () { s.remove(); }, 650);
  });

  /* ---------- sparkle particles (tap, click and drag) ---------- */
  var cv = $('#sparkles'), ctx = cv && cv.getContext('2d'), parts = [], running = false, lastTrail = 0;
  var effectsEnabled = !!(cv && ctx && !reduce && getComputedStyle(cv).display !== 'none');
  function sizeCanvas() {
    var d = window.devicePixelRatio || 1;
    cv.width = window.innerWidth * d; cv.height = window.innerHeight * d;
    ctx.setTransform(d, 0, 0, d, 0, 0);
  }
  function burst(x, y, n, speed) {
    if (!effectsEnabled) return;
    for (var i = 0; i < n; i++) {
      var a = Math.random() * Math.PI * 2, v = (0.6 + Math.random()) * speed;
      parts.push({
        x: x, y: y, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 0.4,
        life: 0, max: 40 + Math.random() * 30, size: 1.5 + Math.random() * 2.5,
        color: COLORS[(Math.random() * COLORS.length) | 0]
      });
    }
    if (!running) { running = true; requestAnimationFrame(tick); }
  }
  function tick() {
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    ctx.globalCompositeOperation = 'lighter';
    parts = parts.filter(function (p) { return p.life < p.max; });
    parts.forEach(function (p) {
      p.life++; p.x += p.vx; p.y += p.vy; p.vy += 0.045; p.vx *= 0.985;
      ctx.globalAlpha = Math.max(0, 1 - p.life / p.max);
      ctx.fillStyle = p.color;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, 6.283); ctx.fill();
    });
    ctx.globalAlpha = 1;
    if (parts.length) requestAnimationFrame(tick); else { running = false; ctx.clearRect(0, 0, window.innerWidth, window.innerHeight); }
  }
  if (effectsEnabled) {
    sizeCanvas();
    window.addEventListener('resize', sizeCanvas);
    window.addEventListener('pointerdown', function (e) { burst(e.clientX, e.clientY, 16, 2.6); }, { passive: true });
    window.addEventListener('pointermove', function (e) {
      var now = performance.now();
      if ((e.pointerType === 'mouse' && e.buttons === 0 && now - lastTrail > 60) || (e.pointerType !== 'mouse' && now - lastTrail > 45)) {
        lastTrail = now; burst(e.clientX, e.clientY, 1, 0.7);
      }
    }, { passive: true });
  }

  /* ---------- tap the moth ---------- */
  var moth = $('#moth');
  if (moth) {
    moth.addEventListener('pointerdown', function () {
      moth.classList.add('startled');
      var r = moth.getBoundingClientRect();
      burst(r.left + r.width / 2, r.top + r.height / 2, 40, 4);
      clearTimeout(moth._t);
      moth._t = setTimeout(function () { moth.classList.remove('startled'); }, 1400);
    });
  }

  /* ---------- toast ---------- */
  var toastEl = $('#toast'), toastTimer;
  function toast(msg, kind) {
    toastEl.textContent = msg;
    toastEl.className = 'toast show' + (kind === 'err' ? ' err' : '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 5000);
  }

  /* ---------- AJAX forms (contact and audit) ---------- */
  function clearErrors(form) {
    $$('.err', form).forEach(function (el) { el.textContent = ''; });
    $$('[aria-invalid]', form).forEach(function (el) { el.removeAttribute('aria-invalid'); });
  }
  function showErrors(form, errors) {
    var first = null;
    Object.keys(errors).forEach(function (name) {
      var holder = $('.err[data-for="' + name + '"]', form), input = form.elements[name];
      if (holder) holder.textContent = errors[name].join(' ');
      if (input) { input.setAttribute('aria-invalid', 'true'); if (!first) first = input; }
    });
    if (first) first.focus();
  }
  $$('form[data-ajax]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = $('button[type=submit]', form);
      clearErrors(form);
      btn.disabled = true; btn.classList.add('loading');
      var token = form.elements.csrfmiddlewaretoken ? form.elements.csrfmiddlewaretoken.value : '';
      fetch(form.action, {
        method: 'POST', body: new FormData(form), credentials: 'same-origin',
        headers: { 'X-Requested-With': 'fetch', 'Accept': 'application/json', 'X-CSRFToken': token }
      }).then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (data) { return { res: res, data: data }; });
      }).then(function (o) {
        if (o.res.ok && o.data.ok) {
          form.reset();
          toast(o.data.message, 'ok');
          var r = btn.getBoundingClientRect();
          burst(r.left + r.width / 2, r.top + r.height / 2, 36, 3.6);
        } else {
          if (o.data.errors) showErrors(form, o.data.errors);
          toast(o.data.message || 'Something went wrong. Please try again.', 'err');
        }
      }).catch(function () {
        toast('Network error. Please check your connection and try again.', 'err');
      }).then(function () {
        btn.disabled = false; btn.classList.remove('loading');
      });
    });
  });

  /* ---------- savings calculator ---------- */
  var hours = $('#hours'), share = $('#share'), cost = $('#cost'), cur = $('#currency');
  if (hours) {
    var out = $('#saving'), hOut = $('#hoursOut'), sOut = $('#shareOut'), hs = $('#hoursSaved');
    var shown = 0, target = 0, anim = 0;
    function money(v) {
      try {
        return new Intl.NumberFormat(undefined, { style: 'currency', currency: cur.value, maximumFractionDigits: 0 }).format(v);
      } catch (err) { return Math.round(v).toLocaleString(); }
    }
    function step() {
      shown += (target - shown) * 0.2;
      if (Math.abs(target - shown) < 1) shown = target;
      out.textContent = money(shown);
      anim = shown === target ? 0 : requestAnimationFrame(step);
    }
    function calc() {
      var h = +hours.value, s = +share.value, c = Math.max(0, +cost.value || 0);
      var saved = h * 4.33 * (s / 100);
      hOut.textContent = h; sOut.textContent = s + '%';
      hs.textContent = Math.round(saved);
      target = saved * c;
      if (reduce) { shown = target; out.textContent = money(target); }
      else if (!anim) anim = requestAnimationFrame(step);
    }
    [hours, share, cost, cur].forEach(function (el) { el.addEventListener('input', calc); });
    calc();
  }
})();
