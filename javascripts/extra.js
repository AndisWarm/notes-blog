// 主页大标题逐字淡入 + 头像陀螺旋转联动
document$.subscribe(function () {
  var title = document.querySelector('.ml3');
  if (!title || title.dataset.animated) return;
  title.dataset.animated = '1';

  var text = title.textContent;
  var html = '';
  for (var i = 0; i < text.length; i++) {
    var ch = text[i];
    if (ch === ' ' || ch === '\n') {
      html += ' ';
    } else {
      html +=
        '<span style="display:inline-block;opacity:0;animation:heroLetter .6s ease forwards;animation-delay:' +
        (0.08 * i) +
        's">' +
        ch +
        '</span>';
    }
  }
  title.innerHTML = html;

  // 头像陀螺旋转：时长与文字完整展示同步，结束后停在正面
  var avatar = document.querySelector('.avatar-gyro');
  if (avatar) {
    var total = (0.08 * (text.length - 1) + 0.6).toFixed(2);
    avatar.style.animationDuration = total + 's';
    avatar.classList.add('is-spinning');
  }
});

// 修复代码块「Toggle line selection」切换关闭后，选中的行未取消高亮的 bug
document.addEventListener('click', function (e) {
  var target = e.target;
  if (!target || typeof target.closest !== 'function') return;
  var btn = target.closest('button[data-md-type="select"]');
  if (!btn) return;
  setTimeout(function () {
    // 按钮已切换到关闭态（未激活）时，清空所有选中的行
    if (!btn.classList.contains('md-code__button--active')) {
      document.querySelectorAll('.hll.select').forEach(function (el) {
        el.replaceWith.apply(el, Array.from(el.childNodes));
      });
    }
  }, 0);
});

// ===== 主页背景网格：Canvas 起伏凹陷效果（参考 wcowin.work）=====
(function () {
  var canvas = null;
  var ctx = null;
  var mouseX = -1000;
  var mouseY = -1000;
  var gridSize = 50;
  var influenceRadius = 150;
  var maxDisplacement = 8;
  var rafId = null;
  var visible = true;

  function resize() {
    if (!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight * 2;
  }

  function draw() {
    if (!canvas || !visible) {
      rafId = null;
      return;
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    var isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';
    ctx.strokeStyle = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.08)';
    ctx.lineWidth = 1;

    var x, y, dx, dy, dist, force, offsetX, offsetY;

    // 垂直线
    for (x = 0; x <= canvas.width; x += gridSize) {
      ctx.beginPath();
      for (y = 0; y <= canvas.height; y += 5) {
        dx = x - mouseX;
        dy = y - mouseY;
        dist = Math.sqrt(dx * dx + dy * dy);
        offsetX = 0;
        if (dist < influenceRadius) {
          force = (1 - dist / influenceRadius) * maxDisplacement;
          offsetX = (dx / dist) * force || 0;
        }
        if (y === 0) ctx.moveTo(x + offsetX, y);
        else ctx.lineTo(x + offsetX, y);
      }
      ctx.stroke();
    }

    // 水平线
    for (y = 0; y <= canvas.height; y += gridSize) {
      ctx.beginPath();
      for (x = 0; x <= canvas.width; x += 5) {
        dx = x - mouseX;
        dy = y - mouseY;
        dist = Math.sqrt(dx * dx + dy * dy);
        offsetY = 0;
        if (dist < influenceRadius) {
          force = (1 - dist / influenceRadius) * maxDisplacement;
          offsetY = (dy / dist) * force || 0;
        }
        if (x === 0) ctx.moveTo(x, y + offsetY);
        else ctx.lineTo(x, y + offsetY);
      }
      ctx.stroke();
    }

    rafId = requestAnimationFrame(draw);
  }

  document.addEventListener('mousemove', function (e) {
    if (!canvas) return;
    var rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;
  });
  document.addEventListener('mouseleave', function () {
    mouseX = -1000;
    mouseY = -1000;
  });
  window.addEventListener('resize', resize);

  document$.subscribe(function () {
    canvas = document.getElementById('gridCanvas');
    if (!canvas || canvas.dataset.gridInit) return;
    canvas.dataset.gridInit = '1';
    ctx = canvas.getContext('2d');
    resize();

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible && !rafId) draw();
      }, { threshold: 0 }).observe(canvas);
    }

    draw();
  });
})();