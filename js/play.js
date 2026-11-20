/* ============================================================
   play.js — the game, the fireworks, the question
   ============================================================ */
(function () {
  "use strict";

  var CFG = window.GIFT || {};
  var G = window.Gift;
  var $ = G.$, $$ = G.$$;

  /* ============================================================
     SING IT BACK — a melody memory game
     ============================================================ */
  function initMelody() {
    var stage = $("#melody-stage");
    if (!stage) return;

    var stars = $$(".star", stage);
    var startOverlay = $("#melody-start");
    var winOverlay = $("#melody-win");
    var roundEl = $("#round-num");
    var totalEl = $("#round-total");
    var dotsEl = $("#melody-dots");
    var statusEl = $("#melody-status");
    var replayBtn = $("#melody-replay");
    var secretEl = $("#melody-secret");

    var target = Math.max(2, CFG.melodyRounds || 5);
    var round = 1;
    var seq = [];
    var step = 0;
    var state = "idle";
    var timers = [];
    var token = 0;

    if (totalEl) totalEl.textContent = target;
    if (secretEl) secretEl.textContent = G.fillTokens(CFG.gameSecret || "");

    if (dotsEl) {
      for (var d = 0; d < target; d++) dotsEl.appendChild(document.createElement("i"));
    }

    /* ---- a small synth, separate from the background music ---- */
    var Sound = (function () {
      var ctx = null, input = null, master = null;
      var NOTES = [523.25, 587.33, 659.25, 783.99, 880.0];

      function init() {
        if (ctx) {
          if (ctx.state === "suspended") ctx.resume();
          return;
        }
        var AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return;

        ctx = new AC();
        master = ctx.createGain();
        master.gain.value = 0.9;

        input = ctx.createBiquadFilter();
        input.type = "lowpass";
        input.frequency.value = 3400;

        var delay = ctx.createDelay(1);
        delay.delayTime.value = 0.3;
        var fb = ctx.createGain(); fb.gain.value = 0.26;
        var wet = ctx.createGain(); wet.gain.value = 0.32;

        input.connect(master);
        input.connect(delay);
        delay.connect(fb); fb.connect(delay);
        delay.connect(wet); wet.connect(master);
        master.connect(ctx.destination);

        if (ctx.state === "suspended") ctx.resume();
      }

      function note(i, when, dur, vol) {
        if (!ctx) return;
        var t = when || ctx.currentTime;
        var f = NOTES[i % NOTES.length];
        dur = dur || 0.9;
        vol = vol == null ? 0.42 : vol;

        [[1, "triangle", 1], [2, "sine", 0.16]].forEach(function (layer) {
          var o = ctx.createOscillator();
          var g = ctx.createGain();
          o.type = layer[1];
          o.frequency.value = f * layer[0];
          var v = vol * layer[2];
          g.gain.setValueAtTime(0.0001, t);
          g.gain.linearRampToValueAtTime(v, t + 0.012);
          g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
          o.connect(g); g.connect(input);
          o.start(t); o.stop(t + dur + 0.05);
        });
      }

      function error() {
        if (!ctx) return;
        var t = ctx.currentTime;
        [196.0, 185.0].forEach(function (f, ix) {
          var o = ctx.createOscillator();
          var g = ctx.createGain();
          var at = t + ix * 0.13;
          o.type = "sine";
          o.frequency.value = f;
          g.gain.setValueAtTime(0.0001, at);
          g.gain.linearRampToValueAtTime(0.16, at + 0.02);
          g.gain.exponentialRampToValueAtTime(0.0001, at + 0.4);
          o.connect(g); g.connect(master);
          o.start(at); o.stop(at + 0.45);
        });
      }

      function chime() {
        if (!ctx) return;
        var t = ctx.currentTime;
        [659.25, 783.99, 1046.5].forEach(function (f, ix) {
          var o = ctx.createOscillator();
          var g = ctx.createGain();
          var at = t + ix * 0.09;
          o.type = "sine";
          o.frequency.value = f;
          g.gain.setValueAtTime(0.0001, at);
          g.gain.linearRampToValueAtTime(0.22, at + 0.02);
          g.gain.exponentialRampToValueAtTime(0.0001, at + 0.7);
          o.connect(g); g.connect(input);
          o.start(at); o.stop(at + 0.75);
        });
      }

      return { init: init, note: note, error: error, chime: chime };
    })();

    function clearTimers() {
      timers.forEach(function (t) { window.clearTimeout(t); });
      timers = [];
    }

    function later(fn, ms) {
      var t = window.setTimeout(fn, ms);
      timers.push(t);
      return t;
    }

    function setStatus(text, good) {
      if (!statusEl) return;
      statusEl.textContent = text;
      statusEl.classList.toggle("good", !!good);
    }

    function paintRound(r) {
      round = r;
      if (roundEl) roundEl.textContent = Math.min(r, target);
      if (dotsEl) {
        for (var i = 0; i < dotsEl.children.length; i++) {
          dotsEl.children[i].classList.toggle("on", i < r - 1);
        }
      }
    }

    function setEnabled(on) {
      stars.forEach(function (s) { s.disabled = !on; });
      if (replayBtn) replayBtn.disabled = !on;
    }

    function flash(i, dur) {
      var el = stars[i];
      if (!el) return;

      el.classList.remove("lit");
      void el.offsetWidth;
      el.classList.add("lit");

      Sound.note(i);

      window.setTimeout(function () { el.classList.remove("lit"); }, dur || 320);

      var r = el.getBoundingClientRect();
      if (r.width && !G.reduce) {
        var col = (el.style.getPropertyValue("--c") || "#f2cd95").trim();
        G.FX.burst(r.left + r.width / 2, r.top + r.height / 2, {
          count: 4, type: "star", speed: 2.6, gravity: 0.02, size: 0.45, colors: [col]
        });
      }
    }

    function buildRound() {
      var need = round + 2;
      while (seq.length < need) {
        var n = Math.floor(Math.random() * stars.length);
        if (seq.length >= 2 && seq[seq.length - 1] === n && seq[seq.length - 2] === n) {
          n = (n + 1) % stars.length;
        }
        seq.push(n);
      }
    }

    function playSequence() {
      clearTimers();
      var my = ++token;
      state = "showing";
      step = 0;
      setEnabled(false);
      setStatus("listen…");

      stars.forEach(function (s) { s.classList.remove("lit"); });

      seq.forEach(function (note, i) {
        later(function () {
          if (my !== token) return;
          flash(note, 340);
        }, 520 + i * 540);
      });

      later(function () {
        if (my !== token) return;
        state = "input";
        step = 0;
        setEnabled(true);
        setStatus("your turn", true);
      }, 520 + seq.length * 540 + 100);
    }

    function tap(i) {
      if (state !== "input") return;
      flash(i, 260);

      if (i === seq[step]) {
        step++;
        if (step >= seq.length) {
          state = "showing";
          setEnabled(false);

          if (round >= target) {
            paintRound(target);
            setStatus("you remembered it all", true);
            later(win, 850);
          } else {
            paintRound(round + 1);
            setStatus("beautiful — one more note", true);
            later(function () {
              buildRound();
              playSequence();
            }, 1150);
          }
        }
        return;
      }

      /* wrong note — no losing, just listen again */
      state = "showing";
      setEnabled(false);
      Sound.error();
      setStatus("almost — listen again");
      stage.classList.add("shake");
      window.setTimeout(function () { stage.classList.remove("shake"); }, 480);
      later(function () {
        step = 0;
        playSequence();
      }, 1000);
    }

    function win() {
      state = "won";
      Sound.chime();
      clearTimers();
      setEnabled(false);

      if (dotsEl) {
        for (var i = 0; i < dotsEl.children.length; i++) dotsEl.children[i].classList.add("on");
      }

      var r = stage.getBoundingClientRect();
      var cx = r.left + r.width / 2;
      var cy = r.top + r.height / 2;

      for (var k = 0; k < 4; k++) {
        (function (n) {
          window.setTimeout(function () {
            G.FX.burst(cx + G.rand(-120, 120), cy + G.rand(-90, 90), {
              count: 16, type: "star", speed: 8, gravity: 0.03, size: 0.9
            });
          }, n * 170);
        })(k);
      }

      G.FX.burst(cx, cy, { count: 26, type: "confetti", speed: 11, gravity: 0.18, size: 1, decay: 0.016 });

      window.setTimeout(function () {
        if (winOverlay) winOverlay.classList.remove("hidden");
      }, 650);
    }

    function start() {
      Sound.init();
      clearTimers();
      token++;
      seq = [];
      round = 1;
      step = 0;
      paintRound(1);
      setEnabled(false);
      if (startOverlay) startOverlay.classList.add("hidden");
      if (winOverlay) winOverlay.classList.add("hidden");
      buildRound();
      later(playSequence, 420);
    }

    /* ---- wiring ---- */
    stars.forEach(function (s, i) {
      s.addEventListener("click", function () { tap(i); });
    });

    var playBtn = $("#melody-play");
    if (playBtn) playBtn.addEventListener("click", start);

    if (replayBtn) {
      replayBtn.addEventListener("click", function () {
        if (state === "input") playSequence();
      });
    }

    document.addEventListener("keydown", function (e) {
      if (state !== "input") return;
      var n = parseInt(e.key, 10);
      if (!(n >= 1 && n <= stars.length)) return;
      var r = stage.getBoundingClientRect();
      if (r.bottom < 0 || r.top > window.innerHeight) return;
      tap(n - 1);
    });

    setEnabled(false);
    setStatus("ready when you are");
  }

  /* ============================================================
     FIREWORKS
     ============================================================ */
  var Fireworks = (function () {
    var canvas = $("#fireworks");
    if (!canvas) return { celebrate: function () {} };

    var ctx = canvas.getContext("2d");
    var W = 0, H = 0;
    var rockets = [], sparks = [];
    var raf = 0, last = 0, nextLaunch = 0;
    var visible = false;
    var reduce = G.reduce;
    var HUES = [340, 45, 280, 200, 15, 315];

    function resize() {
      var s = G.sizeCanvas(canvas);
      ctx = s.ctx; W = s.w; H = s.h;
    }

    function launch(x, hue) {
      var side = Math.random() > 0.5;
      rockets.push({
        x: x == null ? (side ? G.rand(W * 0.04, W * 0.22) : G.rand(W * 0.78, W * 0.96)) : x,
        y: H + 10,
        vy: -G.rand(330, 470),
        targetY: G.rand(H * 0.06, H * 0.3),
        hue: hue == null ? G.pick(HUES) : hue,
        life: 1
      });
    }

    function explode(x, y, hue) {
      var n = reduce ? 26 : Math.round(G.rand(90, 130));
      var white = Math.random() > 0.65;
      for (var i = 0; i < n; i++) {
        var ang = Math.random() * Math.PI * 2;
        var sp = G.rand(45, 280);
        sparks.push({
          x: x, y: y, px: x, py: y,
          vx: Math.cos(ang) * sp,
          vy: Math.sin(ang) * sp,
          life: 1,
          decay: G.rand(0.45, 0.8),
          hue: white ? 45 : hue + G.rand(-14, 14),
          light: white ? 92 : G.rand(58, 78)
        });
      }
      /* a soft flash */
      sparks.push({
        x: x, y: y, px: x, py: y, vx: 0, vy: 0,
        life: 1, decay: 2.2, hue: hue, light: 80, flash: true
      });
    }

    function frame(t) {
      raf = requestAnimationFrame(frame);
      if (!last) last = t;
      var dt = Math.min((t - last) / 1000, 0.05);
      last = t;

      if (visible && t > nextLaunch) {
        launch();
        launch();
        nextLaunch = t + G.rand(620, 1050);
      }

      ctx.clearRect(0, 0, W, H);
      ctx.globalCompositeOperation = "lighter";

      for (var i = rockets.length - 1; i >= 0; i--) {
        var r = rockets[i];
        r.y += r.vy * dt;
        r.vy += 90 * dt;

        var g = ctx.createLinearGradient(r.x, r.y, r.x, r.y + 34);
        g.addColorStop(0, "hsla(" + r.hue + ",90%,85%,.95)");
        g.addColorStop(1, "hsla(" + r.hue + ",90%,70%,0)");
        ctx.strokeStyle = g;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(r.x, r.y);
        ctx.lineTo(r.x, r.y + 34);
        ctx.stroke();

        if (r.y <= r.targetY || r.vy >= 0) {
          explode(r.x, r.y, r.hue);
          rockets.splice(i, 1);
        }
      }

      for (var k = sparks.length - 1; k >= 0; k--) {
        var s = sparks[k];
        s.px = s.x; s.py = s.y;
        s.vx *= 1 - 1.15 * dt;
        s.vy = s.vy * (1 - 1.15 * dt) + 78 * dt;
        s.x += s.vx * dt;
        s.y += s.vy * dt;
        s.life -= s.decay * dt;

        if (s.life <= 0) { sparks.splice(k, 1); continue; }

        if (s.flash) {
          var fg = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, 64 * s.life);
          fg.addColorStop(0, "hsla(" + s.hue + ",90%,82%," + (0.34 * s.life) + ")");
          fg.addColorStop(1, "hsla(" + s.hue + ",90%,70%,0)");
          ctx.fillStyle = fg;
          ctx.beginPath();
          ctx.arc(s.x, s.y, 64 * s.life, 0, Math.PI * 2);
          ctx.fill();
          continue;
        }

        ctx.strokeStyle = "hsla(" + s.hue + ",92%," + s.light + "%," + (Math.max(0, s.life) * 0.22) + ")";
        ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.moveTo(s.px, s.py);
        ctx.lineTo(s.x, s.y);
        ctx.stroke();

        ctx.strokeStyle = "hsla(" + s.hue + ",92%," + s.light + "%," + Math.max(0, s.life) + ")";
        ctx.lineWidth = 1.9;
        ctx.beginPath();
        ctx.moveTo(s.px, s.py);
        ctx.lineTo(s.x, s.y);
        ctx.stroke();
      }

      ctx.globalCompositeOperation = "source-over";
    }

    function start() {
      resize();
      if (!raf) raf = requestAnimationFrame(frame);
    }

    window.addEventListener("resize", resize);

    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          visible = en.isIntersecting;
          if (visible) {
            start();
            nextLaunch = performance.now() + 300;
          }
        });
      }, { threshold: 0.05 });
      io.observe(canvas.parentNode);
    } else {
      visible = true;
      start();
    }

    return {
      start: start,
      celebrate: function () {
        visible = true;
        start();
        for (var i = 0; i < 8; i++) {
          (function (n) {
            window.setTimeout(function () {
              var side = n % 2 === 0;
              var x = side ? G.rand(W * 0.08, W * 0.3) : G.rand(W * 0.7, W * 0.92);
              var y = G.rand(H * 0.08, H * 0.3);
              explode(x, y, G.pick(HUES));
            }, n * 200);
          })(i);
        }
      }
    };
  })();

  /* ============================================================
     FINALE
     ============================================================ */
  function initFinale() {
    var card = $("#finale-card");
    var yes = $("#yes");
    var no = $("#no");
    var btns = $("#final-btns");
    var answer = $("#final-answer");
    var msg = $("#final-msg");
    var replay = $("#replay");
    if (!card) return;

    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { card.classList.add("in"); io.disconnect(); }
        });
      }, { threshold: 0.2 });
      io.observe(card);
    } else {
      card.classList.add("in");
    }

    var noLabels = (CFG.finalNoLabels || ["no", "really?", "it's rigged"]).slice();
    var ni = 0;

    function dodge() {
      if (!no) return;
      ni = Math.min(ni + 1, noLabels.length - 1);
      no.textContent = noLabels[ni];
      var cr = card.getBoundingClientRect();
      var maxX = Math.min(120, cr.width * 0.24);
      var x = G.rand(-maxX, maxX);
      var y = G.rand(-46, 46);
      var scale = Math.max(0.55, 1 - ni * 0.06);
      no.style.transform = "translate(" + x + "px," + y + "px) scale(" + scale + ")";
      no.style.opacity = String(Math.max(0.35, 1 - ni * 0.07));
    }

    if (no) {
      no.addEventListener("pointerenter", dodge);
      no.addEventListener("click", function (e) { e.preventDefault(); dodge(); });
      no.addEventListener("focus", dodge);
    }

    if (yes) {
      yes.addEventListener("click", function () {
        if (btns) {
          btns.style.opacity = "0";
          window.setTimeout(function () { btns.style.display = "none"; }, 420);
        }
        if (answer) answer.classList.remove("hidden");
        if (msg) msg.textContent = G.fillTokens(CFG.finalYes || "");

        var cr = card.getBoundingClientRect();
        var cx = cr.left + cr.width / 2;
        var cy = cr.top + cr.height / 2;

        for (var i = 0; i < 3; i++) {
          (function (n) {
            window.setTimeout(function () {
              G.FX.burst(cx + G.rand(-90, 90), cy + G.rand(-60, 40), {
                count: 14, type: "heart", speed: 8, gravity: 0.1,
                size: 1, lift: 1.2, decay: 0.021
              });
            }, n * 150);
          })(i);
        }

        G.FX.burst(cx, cy, { count: 26, type: "confetti", speed: 12, gravity: 0.22, size: 1, decay: 0.019 });
        Fireworks.celebrate();
      });
    }

    if (replay) {
      replay.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "auto" });
        window.location.reload();
      });
    }
  }

  function boot() {
    initMelody();
    initFinale();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
