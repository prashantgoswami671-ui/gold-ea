/* ============================================================
   core.js — helpers, atmosphere, music
   ============================================================ */
(function () {
  "use strict";

  var CFG = window.GIFT || {};
  var Gift = (window.Gift = window.Gift || {});

  /* ---------- helpers ---------- */
  var $ = (Gift.$ = function (sel, root) {
    return (root || document).querySelector(sel);
  });
  var $$ = (Gift.$$ = function (sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  });

  Gift.clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };
  Gift.rand = function (a, b) { return a + Math.random() * (b - a); };
  Gift.pick = function (arr) { return arr[Math.floor(Math.random() * arr.length)]; };
  Gift.reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  Gift.touch = window.matchMedia("(hover: none)").matches;
  Gift.CFG = CFG;

  Gift.palette = ["#ff9dc0", "#f2cd95", "#c9b8ff", "#fff4e9", "#e2618f", "#ffd7a8"];

  Gift.fillTokens = function (str) {
    if (!str) return "";
    return String(str)
      .replace(/\{nickname\}/g, CFG.nickname || CFG.herName || "")
      .replace(/\{name\}/g, CFG.herName || "");
  };

  Gift.sizeCanvas = function (canvas) {
    var rect = canvas.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = Math.max(1, Math.round(rect.width));
    var h = Math.max(1, Math.round(rect.height));
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx: ctx, w: w, h: h, dpr: dpr };
  };

  /* ---------- heart shape ---------- */
  Gift.heartPath = function (ctx, x, y, s) {
    ctx.beginPath();
    ctx.moveTo(x, y + s * 0.75);
    ctx.bezierCurveTo(x + s * 1.35, y - s * 0.05, x + s * 0.62, y - s * 1.05, x, y - s * 0.4);
    ctx.bezierCurveTo(x - s * 0.62, y - s * 1.05, x - s * 1.35, y - s * 0.05, x, y + s * 0.75);
    ctx.closePath();
  };

  /* ============================================================
     STARFIELD
     ============================================================ */
  Gift.Stars = (function () {
    var canvas = $("#stars");
    if (!canvas) return { start: function () {} };
    var ctx = canvas.getContext("2d");
    var w = 0, h = 0, stars = [], shooters = [], last = 0, raf = 0;
    var reduced = Gift.reduce;

    function resize() {
      var s = Gift.sizeCanvas(canvas);
      ctx = s.ctx; w = s.w; h = s.h;
      var count = reduced ? 60 : Math.round((w * h) / 8500);
      count = Math.min(count, 220);
      stars = [];
      for (var i = 0; i < count; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          r: Gift.rand(0.35, 1.5),
          a: Gift.rand(0.18, 0.9),
          sp: Gift.rand(0.4, 1.8),
          ph: Math.random() * Math.PI * 2,
          gold: Math.random() > 0.78
        });
      }
    }

    function spawnShooter() {
      if (reduced) return;
      shooters.push({
        x: Gift.rand(w * 0.1, w * 0.75),
        y: Gift.rand(0, h * 0.4),
        vx: Gift.rand(5, 8),
        vy: Gift.rand(2.2, 3.6),
        life: 1,
        len: Gift.rand(60, 130)
      });
    }

    function frame(t) {
      raf = requestAnimationFrame(frame);
      if (!last) last = t;
      var dt = Math.min((t - last) / 1000, 0.05);
      last = t;

      ctx.clearRect(0, 0, w, h);
      var scrollOff = (window.scrollY || 0) * 0.035;

      for (var i = 0; i < stars.length; i++) {
        var s = stars[i];
        var tw = 0.55 + 0.45 * Math.sin(t * 0.001 * s.sp + s.ph);
        var y = ((s.y - scrollOff) % h + h) % h;
        ctx.beginPath();
        ctx.arc(s.x, y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = s.gold
          ? "rgba(242,205,149," + (s.a * tw) + ")"
          : "rgba(255,244,233," + (s.a * tw) + ")";
        ctx.fill();
      }

      if (!reduced) {
        if (Math.random() < 0.0035 && shooters.length < 2) spawnShooter();
        for (var k = shooters.length - 1; k >= 0; k--) {
          var sh = shooters[k];
          sh.x += sh.vx * dt * 60;
          sh.y += sh.vy * dt * 60;
          sh.life -= dt * 0.55;
          if (sh.life <= 0 || sh.x > w + 140 || sh.y > h + 140) {
            shooters.splice(k, 1);
            continue;
          }
          var grad = ctx.createLinearGradient(
            sh.x, sh.y, sh.x - sh.vx * sh.len * 0.14, sh.y - sh.vy * sh.len * 0.14
          );
          grad.addColorStop(0, "rgba(255,248,235," + (0.9 * sh.life) + ")");
          grad.addColorStop(1, "rgba(255,248,235,0)");
          ctx.strokeStyle = grad;
          ctx.lineWidth = 1.4;
          ctx.beginPath();
          ctx.moveTo(sh.x, sh.y);
          ctx.lineTo(sh.x - sh.vx * sh.len * 0.14, sh.y - sh.vy * sh.len * 0.14);
          ctx.stroke();
        }
      }
    }

    function start() {
      resize();
      window.addEventListener("resize", resize);
      raf = requestAnimationFrame(frame);
    }

    return { start: start, resize: resize };
  })();

  /* ============================================================
     FX — petals + bursts
     ============================================================ */
  Gift.FX = (function () {
    var canvas = $("#fx");
    if (!canvas) return { burst: function () {}, spark: function () {}, start: function () {} };
    var ctx = canvas.getContext("2d");
    var w = 0, h = 0, petals = [], parts = [], last = 0;
    var reduced = Gift.reduce;

    var petalColors = [
      "rgba(255,196,218,",
      "rgba(214,202,255,",
      "rgba(255,226,186,",
      "rgba(255,208,192,"
    ];

    function resize() {
      var s = Gift.sizeCanvas(canvas);
      ctx = s.ctx; w = s.w; h = s.h;
    }

    function makePetals() {
      petals = [];
      var n = reduced ? 0 : (w < 640 ? 9 : 17);
      for (var i = 0; i < n; i++) {
        petals.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vy: Gift.rand(14, 34),
          vx: Gift.rand(-8, 8),
          r: Gift.rand(2.5, 6),
          rot: Math.random() * Math.PI * 2,
          vr: Gift.rand(-0.6, 0.6),
          sway: Gift.rand(0.6, 1.6),
          phase: Math.random() * Math.PI * 2,
          color: Gift.pick(petalColors),
          alpha: Gift.rand(0.3, 0.62)
        });
      }
    }

    function spawnPetals() {
      if (reduced) return;
      for (var i = 0; i < 26; i++) {
        petals.push({
          x: Math.random() * w,
          y: -20 - Math.random() * h * 0.5,
          vy: Gift.rand(20, 55),
          vx: Gift.rand(-14, 14),
          r: Gift.rand(3, 7.5),
          rot: Math.random() * Math.PI * 2,
          vr: Gift.rand(-1.4, 1.4),
          sway: Gift.rand(0.8, 2),
          phase: Math.random() * Math.PI * 2,
          color: Gift.pick(petalColors),
          alpha: Gift.rand(0.35, 0.7)
        });
      }
    }

    function burst(x, y, opts) {
      opts = opts || {};
      var n = opts.count || 26;
      var colors = opts.colors || Gift.palette;
      var type = opts.type || "heart";
      var speed = opts.speed || 7;
      var gravity = opts.gravity == null ? 0.14 : opts.gravity;
      var size = opts.size || 1;

      for (var i = 0; i < n; i++) {
        var ang = Math.random() * Math.PI * 2;
        var sp = Gift.rand(speed * 0.25, speed);
        parts.push({
          x: x, y: y,
          px: x, py: y,
          vx: Math.cos(ang) * sp,
          vy: Math.sin(ang) * sp - (opts.lift || 0),
          g: gravity,
          life: 1,
          decay: opts.decay || Gift.rand(0.006, 0.016),
          size: Gift.rand(3, 7) * size,
          color: Gift.pick(colors),
          type: type,
          rot: Math.random() * Math.PI * 2,
          vr: Gift.rand(-0.16, 0.16)
        });
      }
    }

    function spark(x, y) {
      parts.push({
        x: x, y: y, px: x, py: y,
        vx: Gift.rand(-0.5, 0.5),
        vy: Gift.rand(-0.6, 0.3),
        g: 0.01,
        life: 1,
        decay: 0.028,
        size: Gift.rand(1, 2.4),
        color: Gift.pick(Gift.palette),
        type: "circle",
        rot: 0, vr: 0
      });
    }

    function drawHeart(x, y, s, rot) {
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(rot);
      Gift.heartPath(ctx, 0, 0, s);
      ctx.restore();
    }

    function frame(t) {
      requestAnimationFrame(frame);
      if (!last) last = t;
      var dt = Math.min((t - last) / 1000, 0.05);
      last = t;

      ctx.clearRect(0, 0, w, h);

      /* petals */
      for (var i = 0; i < petals.length; i++) {
        var p = petals[i];
        p.phase += dt * p.sway;
        p.x += (p.vx + Math.sin(p.phase) * 16) * dt;
        p.y += p.vy * dt;
        p.rot += p.vr * dt;

        if (p.y > h + 30) {
          p.y = -20;
          p.x = Math.random() * w;
        }
        if (p.x < -40) p.x = w + 20;
        if (p.x > w + 40) p.x = -20;

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rot);
        ctx.fillStyle = p.color + p.alpha + ")";
        ctx.beginPath();
        ctx.ellipse(0, 0, p.r, p.r * 0.52, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }

      /* bursts */
      for (var k = parts.length - 1; k >= 0; k--) {
        var q = parts[k];
        q.px = q.x; q.py = q.y;
        q.vx *= 0.985;
        q.vy = q.vy * 0.985 + q.g;
        q.x += q.vx;
        q.y += q.vy;
        q.rot += q.vr;
        q.life -= q.decay;
        if (q.life <= 0) { parts.splice(k, 1); continue; }

        ctx.globalAlpha = Math.max(0, q.life);
        ctx.fillStyle = q.color;

        if (q.type === "heart") {
          drawHeart(q.x, q.y, q.size * 1.5, q.rot);
          ctx.fill();
        } else if (q.type === "petal") {
          ctx.save();
          ctx.translate(q.x, q.y);
          ctx.rotate(q.rot);
          ctx.beginPath();
          ctx.ellipse(0, 0, q.size * 1.5, q.size * 0.7, 0, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        } else if (q.type === "star") {
          ctx.save();
          ctx.translate(q.x, q.y);
          ctx.rotate(q.rot);
          ctx.beginPath();
          for (var a = 0; a < 5; a++) {
            var r1 = q.size * 1.7, r2 = q.size * 0.7;
            var aa = (a * 4 * Math.PI) / 5 - Math.PI / 2;
            if (a === 0) ctx.moveTo(Math.cos(aa) * r1, Math.sin(aa) * r1);
            else ctx.lineTo(Math.cos(aa) * r1, Math.sin(aa) * r1);
            var ab = aa + (2 * Math.PI) / 5;
            ctx.lineTo(Math.cos(ab) * r2, Math.sin(ab) * r2);
          }
          ctx.closePath();
          ctx.fill();
          ctx.restore();
        } else if (q.type === "confetti") {
          ctx.save();
          ctx.translate(q.x, q.y);
          ctx.rotate(q.rot);
          ctx.fillRect(-q.size * 0.7, -q.size * 0.35, q.size * 1.4, q.size * 0.7);
          ctx.restore();
        } else {
          ctx.beginPath();
          ctx.arc(q.x, q.y, q.size, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.globalAlpha = 1;
      }
    }

    function start() {
      resize();
      makePetals();
      window.addEventListener("resize", function () { resize(); makePetals(); });
      requestAnimationFrame(frame);
    }

    return { start: start, burst: burst, spark: spark, petals: spawnPetals };
  })();

  /* ============================================================
     MUSIC — real file, or a soft generated piano
     ============================================================ */
  Gift.Music = (function () {
    var btn = $("#music-btn");
    var audio = null;
    var synth = null;
    var playing = false;
    var failed = false;

    function paint() {
      if (!btn) return;
      btn.classList.toggle("playing", playing);
      btn.setAttribute("aria-pressed", playing ? "true" : "false");
    }

    /* ---- generated fallback ---- */
    function makeSynth() {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      var ctx = new AC();
      var master = ctx.createGain();
      master.gain.value = 0;

      var filter = ctx.createBiquadFilter();
      filter.type = "lowpass";
      filter.frequency.value = 2400;

      var delay = ctx.createDelay(1);
      delay.delayTime.value = 0.38;
      var fb = ctx.createGain(); fb.gain.value = 0.26;
      var wet = ctx.createGain(); wet.gain.value = 0.3;

      filter.connect(master);
      filter.connect(delay);
      delay.connect(fb); fb.connect(delay);
      delay.connect(wet); wet.connect(master);
      master.connect(ctx.destination);

      var CHORDS = [
        [220.0, 261.63, 329.63],   // Am
        [174.61, 220.0, 261.63],   // F
        [261.63, 329.63, 392.0],   // C
        [196.0, 246.94, 392.0]     // G
      ];
      var ARP = [0, 1, 2, 1, 0, 2, 1, 2];
      var STEP = 0.38;
      var step = 0;
      var nextTime = 0;
      var timer = null;

      function pluck(freq, time, dur, vol) {
        var o = ctx.createOscillator();
        var g = ctx.createGain();
        o.type = "triangle";
        o.frequency.value = freq;
        g.gain.setValueAtTime(0.0001, time);
        g.gain.linearRampToValueAtTime(vol, time + 0.015);
        g.gain.exponentialRampToValueAtTime(0.0001, time + dur);
        o.connect(g); g.connect(filter);
        o.start(time); o.stop(time + dur + 0.05);
      }

      function pad(freqs, time) {
        freqs.forEach(function (f) {
          var o = ctx.createOscillator();
          var g = ctx.createGain();
          o.type = "sine";
          o.frequency.value = f / 2;
          g.gain.setValueAtTime(0.0001, time);
          g.gain.linearRampToValueAtTime(0.02, time + 1.4);
          g.gain.linearRampToValueAtTime(0.0001, time + 3.2);
          o.connect(g); g.connect(filter);
          o.start(time); o.stop(time + 3.4);
        });
      }

      function schedule() {
        while (nextTime < ctx.currentTime + 0.8) {
          var bar = Math.floor(step / 8) % 4;
          var chord = CHORDS[bar];
          var idx = ARP[step % 8];
          var octave = step % 16 >= 8 ? 2 : 1;
          pluck(chord[idx] * octave, nextTime, 1.1, 0.07);
          if (step % 8 === 0) pad(chord, nextTime);
          if (step % 8 === 4) pluck(chord[2] * 2, nextTime, 1.6, 0.025);
          step++;
          nextTime += STEP;
        }
      }

      return {
        start: function () {
          if (ctx.state === "suspended") ctx.resume();
          nextTime = ctx.currentTime + 0.12;
          step = 0;
          master.gain.cancelScheduledValues(ctx.currentTime);
          master.gain.setValueAtTime(0.0001, ctx.currentTime);
          master.gain.linearRampToValueAtTime(0.9, ctx.currentTime + 1.6);
          schedule();
          timer = setInterval(schedule, 120);
        },
        stop: function () {
          clearInterval(timer);
          timer = null;
          master.gain.cancelScheduledValues(ctx.currentTime);
          master.gain.setValueAtTime(master.gain.value, ctx.currentTime);
          master.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + 0.5);
        }
      };
    }

    function fallback() {
      if (failed) return;
      failed = true;
      if (audio) { audio.pause(); audio = null; }
      synth = synth || makeSynth();
      if (synth && playing) synth.start();
    }

    function start() {
      if (playing) return;
      playing = true;
      paint();

      if (failed) {
        synth = synth || makeSynth();
        if (synth) synth.start();
        return;
      }

      if (!audio) {
        try {
          audio = new Audio(CFG.song || "music/song.mp3");
          audio.loop = true;
          audio.volume = 0.72;
          audio.preload = "auto";
          audio.addEventListener("error", fallback, { once: true });
        } catch (e) { fallback(); return; }
      }

      var p = audio.play();
      if (p && p.catch) {
        p.catch(function () {
          /* file missing or blocked — try the generated melody */
          setTimeout(function () { if (playing) fallback(); }, 60);
        });
      }
    }

    function stop() {
      if (!playing) return;
      playing = false;
      paint();
      if (audio) audio.pause();
      if (synth) synth.stop();
    }

    if (btn) {
      btn.addEventListener("click", function () {
        if (playing) stop(); else start();
      });
    }

    return { start: start, stop: stop, toggle: function () { playing ? stop() : start(); } };
  })();

  /* ============================================================
     CURSOR GLOW + SPARKLE TRAIL
     ============================================================ */
  Gift.Cursor = (function () {
    var glow = $("#cursor-glow");
    var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    if (!glow || !fine || Gift.reduce) return { start: function () {} };

    var tx = window.innerWidth / 2, ty = window.innerHeight / 2;
    var cx = tx, cy = ty;
    var lastSpark = 0;

    window.addEventListener("pointermove", function (e) {
      tx = e.clientX; ty = e.clientY;
      var now = performance.now();
      if (now - lastSpark > 55) {
        lastSpark = now;
        Gift.FX.spark(tx + Gift.rand(-4, 4), ty + Gift.rand(-4, 4));
      }
    }, { passive: true });

    function frame() {
      cx += (tx - cx) * 0.12;
      cy += (ty - cy) * 0.12;
      glow.style.transform = "translate3d(" + cx + "px," + cy + "px,0)";
      requestAnimationFrame(frame);
    }
    return { start: function () { requestAnimationFrame(frame); } };
  })();

  /* ============================================================
     SCROLL PROGRESS
     ============================================================ */
  Gift.ScrollBar = (function () {
    var bar = $("#scroll-bar");
    if (!bar) return { start: function () {} };
    function update() {
      var doc = document.documentElement;
      var max = doc.scrollHeight - window.innerHeight;
      var pct = max > 0 ? (window.scrollY / max) * 100 : 0;
      bar.style.width = pct + "%";
    }
    return {
      start: function () {
        window.addEventListener("scroll", update, { passive: true });
        window.addEventListener("resize", update);
        update();
      }
    };
  })();

  /* ============================================================
     REVEAL OBSERVER
     ============================================================ */
  Gift.Reveal = (function () {
    var io = null;

    function init() {
      if (!("IntersectionObserver" in window)) {
        $$(".reveal").forEach(function (el) { el.classList.add("in"); });
        return;
      }
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          var el = en.target;
          var d = parseInt(el.getAttribute("data-delay") || "0", 10);
          el.style.transitionDelay = (d * 0.13) + "s";
          el.classList.add("in");
          io.unobserve(el);
        });
      }, { threshold: 0.14, rootMargin: "0px 0px -8% 0px" });

      $$(".reveal").forEach(function (el) { io.observe(el); });
    }

    return {
      init: init,
      observe: function (el) { if (io) io.observe(el); else el.classList.add("in"); }
    };
  })();

  /* ---------- boot atmosphere ---------- */
  Gift.boot = function () {
    Gift.Stars.start();
    Gift.FX.start();
    Gift.Cursor.start();
    Gift.ScrollBar.start();
    Gift.Reveal.init();
  };
})();
