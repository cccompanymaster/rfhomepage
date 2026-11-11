/* viz.js — 사이트 차트 공통 (viz.css 짝)
   1) 화면에 들어오면 막대가 자람 (움직임 줄이기 설정이면 바로 다 보임)
   2) 마우스·터치 툴팁 — 값은 글자로도 이미 보이고, 툴팁은 보조. 내용은 textContent로만 넣음
   3) 일정 차트 칸에 안 들어가는 글자는 숨김 (잘라서 보여 주지 않음 — 툴팁과 아래 표에 있음) */
(() => {
  const charts = document.querySelectorAll('.vz');
  if (!charts.length) return;

  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    charts.forEach((c) => {
      if (!c.hasAttribute('data-vz-grow')) return;
      c.classList.add('is-armed');
      const io = new IntersectionObserver((es) => {
        if (es.some((e) => e.isIntersecting)) { c.classList.add('is-on'); io.disconnect(); }
      }, { threshold: 0.25 });
      io.observe(c);
    });
  }

  const tip = document.createElement('div');
  tip.className = 'vz-tip';
  tip.setAttribute('aria-hidden', 'true');
  const v = document.createElement('strong'), k = document.createElement('span'), n = document.createElement('em');
  tip.append(v, k, n);
  document.body.append(tip);
  let cur = null;

  const place = (x, y) => {
    const w = tip.offsetWidth, h = tip.offsetHeight;
    let left = x + 14, top = y - h - 14;
    if (left + w > innerWidth - 8) left = x - w - 14;
    if (left < 8) left = 8;
    if (top < 8) top = y + 20;
    tip.style.transform = '';
    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
  };
  const show = (el, x, y) => {
    if (cur !== el) {
      cur?.classList.remove('is-hot');
      cur = el;
      el.classList.add('is-hot');
      v.textContent = el.dataset.vzV || '';
      k.textContent = el.dataset.vzK || '';
      n.textContent = el.dataset.vzN || '';
      n.hidden = !el.dataset.vzN;
    }
    place(x, y);
    tip.classList.add('on');
  };
  const hide = () => { tip.classList.remove('on'); cur?.classList.remove('is-hot'); cur = null; };
  const target = (e) => e.target.closest?.('.vz [data-vz-v]');

  document.addEventListener('pointermove', (e) => {
    if (e.pointerType === 'touch') return;
    const el = target(e);
    if (el) show(el, e.clientX, e.clientY); else if (cur) hide();
  }, { passive: true });
  document.addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'mouse') return;
    const el = target(e);
    if (el) show(el, e.clientX, e.clientY); else hide();
  }, { passive: true });
  // 손가락을 떼도 pointerleave가 오므로 마우스가 화면 밖으로 나갈 때만 닫음
  document.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse') hide(); });
  addEventListener('scroll', () => { if (cur) hide(); }, { passive: true });

  const labels = document.querySelectorAll('.vz-g-seg b');
  const fit = () => labels.forEach((b) => {
    b.classList.remove('is-hidden');
    const room = b.parentElement.clientWidth - 10;
    if (b.scrollWidth > room) b.classList.add('is-hidden');
  });
  if (labels.length) {
    fit();
    document.fonts?.ready.then(fit);
    let t;
    addEventListener('resize', () => { clearTimeout(t); t = setTimeout(fit, 120); });
  }
})();
