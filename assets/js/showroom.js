/* ============================================================
   showroom.js — 쇼룸·템플릿 공통 인터랙션
   - 카드 호버 글로우 (마우스 위치 기반)
   - iframe 프리뷰 lazy-load + 스케일 자동 맞춤
   - 카테고리 필터 (chip 클릭으로 카드 토글)
   - 스크롤 진행 바
   - 숫자 카운트업 애니메이션 (data-count 속성 사용)
   ============================================================ */
(() => {
  /* -------- 카드 호버 글로우 -------- */
  document.querySelectorAll('.ref-card').forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', ((e.clientX - r.left) / r.width) * 100 + '%');
      card.style.setProperty('--my', ((e.clientY - r.top) / r.height) * 100 + '%');
    });
  });

  /* -------- iframe lazy-load -------- */
  const lazy = document.querySelectorAll('iframe[data-src]');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.src = e.target.dataset.src;
            io.unobserve(e.target);
          }
        });
      },
      { rootMargin: '200px 0px' }
    );
    lazy.forEach((f) => io.observe(f));
  } else {
    lazy.forEach((f) => (f.src = f.dataset.src));
  }

  /* -------- iframe 자동 스케일 -------- */
  const fit = (frame, designW) => {
    const wrap = frame.parentElement;
    if (!wrap) return;
    const w = wrap.clientWidth;
    if (!w) return;
    const scale = w / designW;
    frame.style.transform = `scale(${scale})`;
    const designH = parseFloat(frame.style.height) || frame.offsetHeight;
    wrap.style.height = designH * scale + 'px';
  };
  const refit = () => {
    document.querySelectorAll('.preview-desktop').forEach((f) => fit(f, 1440));
    document.querySelectorAll('.preview-mobile').forEach((f) => fit(f, 390));
  };
  window.addEventListener('load', refit);
  window.addEventListener('resize', refit);
  setTimeout(refit, 100);
  setTimeout(refit, 600);

  /* -------- 카테고리 필터 -------- */
  const chips = document.querySelectorAll('.cat-chip[data-cat]');
  const refCards = document.querySelectorAll('.ref-card[data-cat]');
  if (chips.length && refCards.length) {
    chips.forEach((chip) => {
      chip.addEventListener('click', () => {
        chips.forEach((c) => (c.dataset.active = 'false'));
        chip.dataset.active = 'true';
        const cat = chip.dataset.cat;
        refCards.forEach((card) => {
          const match = cat === 'all' || card.dataset.cat === cat;
          card.classList.toggle('is-hidden', !match);
        });
        const visible = document.querySelectorAll('.ref-card[data-cat]:not(.is-hidden)').length;
        const total = refCards.length;
        const counter = document.querySelector('[data-card-counter]');
        if (counter) counter.textContent = `${visible} / ${total} references`;
        // resize iframes after layout shift
        setTimeout(refit, 50);
      });
    });
  }

  /* -------- 스크롤 진행 바 -------- */
  const bar = document.querySelector('.scroll-progress');
  if (bar) {
    const updateBar = () => {
      const h = document.documentElement;
      const pct = h.scrollTop / (h.scrollHeight - h.clientHeight || 1);
      bar.style.transform = `scaleX(${Math.min(1, Math.max(0, pct))})`;
    };
    window.addEventListener('scroll', updateBar, { passive: true });
    updateBar();
  }

  /* -------- 숫자 카운트업 -------- */
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);
  const animateCount = (el) => {
    const target = parseFloat(el.dataset.count);
    if (Number.isNaN(target)) return;
    const decimals = parseInt(el.dataset.decimals || '0', 10);
    const duration = parseInt(el.dataset.duration || '1400', 10);
    const start = performance.now();
    const formatter = new Intl.NumberFormat('ko-KR', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const v = target * easeOut(t);
      el.textContent = formatter.format(decimals ? +v.toFixed(decimals) : Math.round(v));
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    const cio = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            animateCount(e.target);
            cio.unobserve(e.target);
          }
        });
      },
      { threshold: 0.4 }
    );
    counters.forEach((c) => cio.observe(c));
  }
})();
