/* ============================================================
   gift.js — the intro, the museum, the jar, the letter
   ============================================================ */
(function () {
  "use strict";

  var CFG = window.GIFT || {};
  var G = window.Gift;
  var $ = G.$, $$ = G.$$;

  var name = CFG.herName || "You";
  var nick = CFG.nickname || name;

  /* ============================================================
     PHOTOS
     A memory written as "photos/01.svg" is really a placeholder.
     If a real photo called 01.jpg / 01.jpeg / 01.png / 01.webp
     exists next to it, that one is used instead — so you can drop
     your photos in without touching config.js at all.
     ============================================================ */
  var Photo = (function () {
    var EXT = ["jpg", "jpeg", "png", "webp"];

    function candidates(src) {
      var m = /^(.*)\.svg$/i.exec(src || "");
      if (!m) return src ? [src] : [];
      var out = [];
      EXT.forEach(function (e) { out.push(m[1] + "." + e); });
      out.push(src);
      return out;
    }

    function load(img, src, fallback) {
      if (!img) return;
      var list = candidates(src);
      var i = 0;

      function next() {
        if (i >= list.length) {
          img.onerror = null;
          if (fallback) img.src = fallback;
          return;
        }
        img.onerror = next;
        img.src = list[i++];
      }

      next();
    }

    return { load: load, candidates: candidates };
  })();

  /* ============================================================
     FILL THE PAGE
     ============================================================ */
  function fillText() {
    document.title = "For " + name + " — Happy Birthday";

    var envName = $("#env-front-name"); if (envName) envName.textContent = name;
    var heroName = $("#hero-name"); if (heroName) heroName.textContent = name;

    var foot = $("#final-footer-text");
    if (foot) foot.textContent = CFG.finalFooter || "made by hand, with a ridiculous amount of love";

    var q = $("#final-q");
    if (q) q.textContent = CFG.finalQuestion || "One last thing…";

    var date = $("#letter-date");
    if (date) date.textContent = CFG.birthdayDate || "";

    var greet = $("#letter-greeting");
    if (greet) greet.textContent = "Dear " + nick + ",";

    var sign = $("#letter-sign");
    if (sign) sign.textContent = CFG.fromName || "Yours, always";

    var body = $("#letter-body");
    if (body) {
      (CFG.letter || []).forEach(function (para) {
        var p = document.createElement("p");
        p.textContent = G.fillTokens(para);
        body.appendChild(p);
      });
    }
  }

  /* ============================================================
     INTRO
     ============================================================ */
  function initIntro() {
    var intro = $("#intro");
    var envelope = $("#envelope");
    var hint = $("#intro-hint");
    var experience = $("#experience");
    if (!envelope || !intro || !experience) return;

    var opened = false;

    function openGift() {
      if (opened) return;
      opened = true;

      envelope.classList.add("open");
      intro.classList.add("open");
      if (hint) hint.style.opacity = "0";

      G.Music.start();

      var r = envelope.getBoundingClientRect();
      var cx = r.left + r.width / 2;
      var cy = r.top + r.height / 2;
      G.FX.burst(cx, cy, { count: 34, type: "petal", speed: 9, gravity: 0.06, size: 1.15 });
      G.FX.burst(cx, cy, { count: 14, type: "heart", speed: 6, gravity: 0.04, lift: 1.5 });
      G.FX.petals();

      window.setTimeout(function () {
        experience.hidden = false;
        window.scrollTo(0, 0);
        intro.classList.add("gone");
        document.body.classList.add("entered");
        G.Reveal.init();
        startHeroLines();
        window.setTimeout(function () {
          if (intro.parentNode) intro.parentNode.removeChild(intro);
        }, 1100);
      }, 1250);
    }

    envelope.addEventListener("click", openGift);
    envelope.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openGift(); }
    });
  }

  /* ============================================================
     HERO LINES
     ============================================================ */
  var heroTimer = null;
  function startHeroLines() {
    var el = $("#hero-line");
    var lines = (CFG.heroLines || []).filter(Boolean);
    if (!el || !lines.length) return;

    var i = 0;
    el.textContent = lines[0];
    el.style.opacity = "1";

    if (lines.length < 2) return;

    heroTimer = window.setInterval(function () {
      i = (i + 1) % lines.length;
      el.classList.add("swap");
      window.setTimeout(function () {
        el.textContent = lines[i];
        el.classList.remove("swap");
      }, 700);
    }, 5400);
  }

  /* ============================================================
     LIGHTBOX
     ============================================================ */
  var Lightbox = (function () {
    var el = $("#lightbox");
    var img = $("#lb-img");
    var cap = $("#lb-cap");
    var date = $("#lb-date");
    var list = [];
    var index = 0;
    var lastFocus = null;

    function paletteFallback(i) {
      var sets = [
        ["#ffb7d1", "#7b4bb5"], ["#ffd9a8", "#b5486f"],
        ["#b9a6ff", "#3a2b6b"], ["#ffc2a8", "#6b3a52"],
        ["#a8d8ff", "#2f3a6b"], ["#ffb7e6", "#5a2b5f"]
      ];
      var s = sets[i % sets.length];
      var svg =
        '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="1000" viewBox="0 0 800 1000">' +
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0" stop-color="' + s[0] + '"/><stop offset="1" stop-color="' + s[1] + '"/>' +
        '</linearGradient><filter id="b"><feGaussianBlur stdDeviation="70"/></filter></defs>' +
        '<rect width="800" height="1000" fill="url(#g)"/>' +
        '<circle cx="230" cy="300" r="180" fill="#fff" opacity=".28" filter="url(#b)"/>' +
        '<circle cx="600" cy="720" r="220" fill="#fff" opacity=".18" filter="url(#b)"/>' +
        '<text x="400" y="520" text-anchor="middle" font-family="Georgia, serif" font-size="44" fill="rgba(255,255,255,.55)">a memory</text>' +
        "</svg>";
      return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
    }

    function show(i) {
      if (!list.length) return;
      index = (i + list.length) % list.length;
      var m = list[index];
      img.alt = m.caption || "A memory";
      Photo.load(img, m.photo, paletteFallback(index));
      cap.textContent = m.caption || "";
      date.textContent = m.date || "";
      /* retrigger the image animation */
      img.style.animation = "none";
      void img.offsetWidth;
      img.style.animation = "";
    }

    function open(i) {
      lastFocus = document.activeElement;
      show(i);
      el.classList.add("open");
      el.setAttribute("aria-hidden", "false");
      document.body.classList.add("locked");
      $("#lb-close").focus({ preventScroll: true });
    }

    function close() {
      el.classList.remove("open");
      el.setAttribute("aria-hidden", "true");
      document.body.classList.remove("locked");
      if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
    }

    function init(memories) {
      list = memories;
      if (!el) return;
      $("#lb-close").addEventListener("click", close);
      $("#lb-prev").addEventListener("click", function () { show(index - 1); });
      $("#lb-next").addEventListener("click", function () { show(index + 1); });
      el.addEventListener("click", function (e) { if (e.target === el) close(); });
      document.addEventListener("keydown", function (e) {
        if (!el.classList.contains("open")) return;
        if (e.key === "Escape") close();
        if (e.key === "ArrowLeft") show(index - 1);
        if (e.key === "ArrowRight") show(index + 1);
      });
    }

    return { init: init, open: open, close: close, fallback: paletteFallback };
  })();

  /* ============================================================
     SCRAPBOOK
     ============================================================ */
  function initScrapbook() {
    var track = $("#scrapbook");
    if (!track) return;

    var memories = CFG.memories || [];
    var frag = document.createDocumentFragment();

    memories.forEach(function (m, i) {
      var card = document.createElement("button");
      card.className = "polaroid";
      card.type = "button";
      card.setAttribute("aria-label", "Open memory " + (i + 1));

      var img = document.createElement("img");
      img.className = "polaroid-img";
      img.alt = m.caption ? m.caption.slice(0, 70) : "A memory";
      img.loading = "lazy";
      img.decoding = "async";
      Photo.load(img, m.photo, Lightbox.fallback ? Lightbox.fallback(i) : "");

      var cap = document.createElement("div");
      cap.className = "polaroid-cap";
      cap.textContent = m.caption || "";

      if (m.date) {
        var d = document.createElement("span");
        d.className = "polaroid-date";
        d.textContent = m.date;
        cap.appendChild(d);
      }

      card.appendChild(img);
      card.appendChild(cap);
      card.addEventListener("click", function () {
        if (track.dataset.dragged === "1") return;
        Lightbox.open(i);
      });
      frag.appendChild(card);
    });

    track.appendChild(frag);
    Lightbox.init(memories);

    /* ---- drag to scroll ---- */
    var down = false, startX = 0, startLeft = 0, moved = 0;

    track.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "touch") return; /* native touch scrolling is better */
      down = true; moved = 0;
      startX = e.clientX;
      startLeft = track.scrollLeft;
      track.dataset.dragged = "0";
      track.classList.add("dragging");
      track.setPointerCapture(e.pointerId);
    });

    track.addEventListener("pointermove", function (e) {
      if (!down) return;
      var dx = e.clientX - startX;
      moved = Math.max(moved, Math.abs(dx));
      track.scrollLeft = startLeft - dx;
    });

    function endDrag() {
      if (!down) return;
      down = false;
      track.classList.remove("dragging");
      if (moved > 8) track.dataset.dragged = "1";
      window.setTimeout(function () { track.dataset.dragged = "0"; }, 60);
    }
    track.addEventListener("pointerup", endDrag);
    track.addEventListener("pointercancel", endDrag);
    track.addEventListener("pointerleave", endDrag);
  }

  /* ============================================================
     WISH JAR
     ============================================================ */
  function initJar() {
    var orbs = $("#orbs");
    var modal = $("#wish-modal");
    if (!orbs || !modal) return;

    var notes = CFG.wishNotes || [];
    var opened = 0;
    var total = notes.length;

    var colors = [
      ["#ffd9e6", "#ff7fae", "rgba(255,127,174,.55)"],
      ["#fff0c9", "#e8b06f", "rgba(232,176,111,.55)"],
      ["#e6dcff", "#9d86ff", "rgba(157,134,255,.55)"],
      ["#d8f5ff", "#6fc6e8", "rgba(111,198,232,.5)"],
      ["#ffe1d1", "#ff8f6f", "rgba(255,143,111,.5)"],
      ["#ffe3f6", "#e07fd0", "rgba(224,127,208,.5)"]
    ];

    var countEl = $("#jar-count");
    var totalEl = $("#jar-total");
    var noteEl = $("#jar-note");
    var dotsEl = $("#jar-dots");
    var jarBody = $("#jar-body");

    if (totalEl) totalEl.textContent = "of " + total;

    var frag = document.createDocumentFragment();
    var dotsFrag = document.createDocumentFragment();

    notes.forEach(function (n, i) {
      var c = colors[i % colors.length];
      var b = document.createElement("button");
      b.className = "orb";
      b.type = "button";
      b.setAttribute("aria-label", "Open note " + (i + 1));
      b.style.left = (n.x || 50) + "%";
      b.style.top = (n.y || 50) + "%";
      b.style.setProperty("--c1", c[0]);
      b.style.setProperty("--c2", c[1]);
      b.style.setProperty("--glow", c[2]);
      b.style.setProperty("--dur", (5 + (i % 4)) + "s");
      b.style.setProperty("--delay", (i * 0.37).toFixed(2) + "s");

      b.addEventListener("click", function (ev) {
        openNote(i, b, ev);
      });

      frag.appendChild(b);

      var dot = document.createElement("i");
      dotsFrag.appendChild(dot);
    });

    orbs.appendChild(frag);
    if (dotsEl) dotsEl.appendChild(dotsFrag);

    var titleEl = $("#wish-title");
    var textEl = $("#wish-text");
    var cardEl = $("#wish-card");

    function openNote(i, btn, ev) {
      var n = notes[i];
      if (!n) return;

      titleEl.textContent = n.title || "";
      textEl.textContent = n.text || "";
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
      document.body.classList.add("locked");

      var r = btn.getBoundingClientRect();
      G.FX.burst(r.left + r.width / 2, r.top + r.height / 2, {
        count: 16, type: "heart", speed: 5, gravity: 0.05, size: 0.85
      });

      if (!btn.classList.contains("opened")) {
        btn.classList.add("opened");
        opened++;
        if (countEl) countEl.textContent = opened;

        var dots = dotsEl ? dotsEl.children : [];
        if (dots[i]) dots[i].classList.add("on");

        if (opened === total) {
          if (jarBody) jarBody.classList.add("lit");
          if (noteEl) noteEl.textContent = "That's all of them. Every single one was true.";
          var jr = jarBody.getBoundingClientRect();
          G.FX.burst(jr.left + jr.width / 2, jr.top + jr.height / 2, {
            count: 42, type: "star", speed: 10, gravity: 0.05, size: 1
          });
        }
      }

      window.setTimeout(function () {
        var closeBtn = $("#wish-close");
        if (closeBtn) closeBtn.focus({ preventScroll: true });
      }, 420);
    }

    function closeNote() {
      modal.classList.remove("open");
      modal.setAttribute("aria-hidden", "true");
      document.body.classList.remove("locked");
    }

    $("#wish-close").addEventListener("click", closeNote);
    modal.addEventListener("click", function (e) { if (e.target === modal) closeNote(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && modal.classList.contains("open")) closeNote();
    });

    /* little wobble when you tap the glass */
    jarBody.addEventListener("click", function (e) {
      if (e.target.closest(".orb")) return;
      jarBody.style.transform = "translateX(-3px) rotate(-.6deg)";
      window.setTimeout(function () { jarBody.style.transform = ""; }, 160);
    });
  }

  /* ============================================================
     LETTER
     ============================================================ */
  function initLetter() {
    var sec = $("#letter");
    var body = $("#letter-body");
    var sign = $("#letter-sign");
    if (!sec || !body) return;

    var paras = $$("p", body);
    var done = false;

    function reveal() {
      if (done) return;
      done = true;
      paras.forEach(function (p, i) {
        window.setTimeout(function () { p.classList.add("in"); }, 140 + i * 220);
      });
      window.setTimeout(function () {
        if (sign) sign.classList.add("in");
      }, 260 + paras.length * 220);
    }

    if (!("IntersectionObserver" in window)) { reveal(); return; }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { reveal(); io.disconnect(); }
      });
    }, { threshold: 0.22 });
    io.observe(sec);
  }

  /* ============================================================
     NAVIGATION
     ============================================================ */
  function initNav() {
    function go(sel) {
      var target = $(sel);
      if (target) target.scrollIntoView({ behavior: G.reduce ? "auto" : "smooth", block: "start" });
    }
    var begin = $("#begin");
    if (begin) begin.addEventListener("click", function () { go("#memories"); });
    var toLetter = $("#to-letter");
    if (toLetter) toLetter.addEventListener("click", function () { go("#letter"); });
    var toFinale = $("#to-finale");
    if (toFinale) toFinale.addEventListener("click", function () { go("#finale"); });
  }

  /* ============================================================
     BOOT
     ============================================================ */
  function boot() {
    fillText();
    G.boot();
    initIntro();
    initScrapbook();
    initJar();
    initLetter();
    initNav();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
