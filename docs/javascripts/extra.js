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