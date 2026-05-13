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

  /* -------- 가로 하단 배너 닫기 -------- */
  document.querySelectorAll('.banner-bottom .close').forEach((btn) => {
    btn.addEventListener('click', () => {
      const banner = btn.closest('.banner-bottom');
      if (!banner) return;
      banner.classList.add('is-hidden');
      try {
        sessionStorage.setItem(
          'banner-dismissed-' + (banner.dataset.bannerId || 'default'),
          '1'
        );
      } catch (e) {}
    });
  });
  document.querySelectorAll('.banner-bottom').forEach((banner) => {
    try {
      const id = banner.dataset.bannerId || 'default';
      if (sessionStorage.getItem('banner-dismissed-' + id) === '1') {
        banner.classList.add('is-hidden');
      }
    } catch (e) {}
  });

  /* -------- 숫자 카운트업 -------- */
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);
  const animateCount = (el) => {
    const target = parseFloat(el.dataset.count);
    if (Number.isNaN(target)) return;
    const decimals = parseInt(el.dataset.decimals || '0', 10);
    const duration = parseInt(el.dataset.duration || '1400', 10);
    const isYear = el.dataset.format === 'year';
    const start = performance.now();
    const formatter = isYear
      ? null
      : new Intl.NumberFormat('ko-KR', {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        });
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const v = target * easeOut(t);
      if (isYear) {
        el.textContent = String(Math.round(v));
      } else {
        el.textContent = formatter.format(decimals ? +v.toFixed(decimals) : Math.round(v));
      }
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

  /* -------- 타이핑 효과 (rotating typewriter) -------- */
  // <span class="typer" data-words="A|B|C" data-type-speed="80" data-pause="1800"></span>
  class Typer {
    constructor(el) {
      this.el = el;
      this.words = (el.dataset.words || '').split('|').filter(Boolean);
      if (this.words.length === 0) return;
      this.typeSpeed = parseInt(el.dataset.typeSpeed, 10) || 90;
      this.deleteSpeed = parseInt(el.dataset.deleteSpeed, 10) || 40;
      this.pauseAfterType = parseInt(el.dataset.pause, 10) || 1800;
      this.pauseAfterDelete = 280;
      this.idx = 0;
      this.charIdx = 0;
      this.deleting = false;
      // 가장 긴 단어 기준으로 min-width 잡아 레이아웃 흔들림 최소화
      const longest = this.words.reduce((a, b) => (a.length > b.length ? a : b));
      // 빈 텍스트 시작 + 첫 단어부터 타이핑
      this.el.textContent = '';
      // 시작 약간 지연 (페이지 로드 호흡)
      setTimeout(() => this.tick(), 600);
    }
    tick() {
      const word = this.words[this.idx];
      if (this.deleting) {
        this.charIdx--;
        this.el.textContent = word.substring(0, this.charIdx);
        if (this.charIdx === 0) {
          this.deleting = false;
          this.idx = (this.idx + 1) % this.words.length;
          setTimeout(() => this.tick(), this.pauseAfterDelete);
          return;
        }
        setTimeout(() => this.tick(), this.deleteSpeed);
      } else {
        this.charIdx++;
        this.el.textContent = word.substring(0, this.charIdx);
        if (this.charIdx === word.length) {
          this.deleting = true;
          setTimeout(() => this.tick(), this.pauseAfterType);
          return;
        }
        setTimeout(() => this.tick(), this.typeSpeed);
      }
    }
  }
  // prefers-reduced-motion 사용자에겐 첫 단어만 정적으로 표시
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const typerEls = document.querySelectorAll('.typer');
  if (typerEls.length) {
    if (reduceMotion) {
      typerEls.forEach((el) => {
        const first = (el.dataset.words || '').split('|')[0] || '';
        el.textContent = first;
        el.classList.add('typer-static');
      });
    } else if ('IntersectionObserver' in window) {
      // 뷰포트에 들어왔을 때만 타이핑 시작 (스크롤 위치의 카피도 살아남)
      const tio = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) {
              new Typer(e.target);
              tio.unobserve(e.target);
            }
          });
        },
        { threshold: 0.5 }
      );
      typerEls.forEach((el) => tio.observe(el));
    } else {
      typerEls.forEach((el) => new Typer(el));
    }
  }
})();
