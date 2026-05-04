/* ============================================================
   showroom.js — 쇼룸 카드 인터랙션
   - 카드 호버 시 마우스 위치 기반 글로우
   - iframe 프리뷰는 IntersectionObserver로 lazy-load
   - 데스크톱/모바일 목업의 iframe은 컨테이너에 맞춰 자동 스케일
   ============================================================ */
(() => {
  const cards = document.querySelectorAll('.ref-card');

  /* 마우스 위치 글로우 */
  cards.forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const mx = ((e.clientX - rect.left) / rect.width) * 100;
      const my = ((e.clientY - rect.top) / rect.height) * 100;
      card.style.setProperty('--mx', mx + '%');
      card.style.setProperty('--my', my + '%');
    });
  });

  /* iframe 프리뷰 lazy-load */
  const lazyFrames = document.querySelectorAll('iframe[data-src]');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const frame = entry.target;
            frame.src = frame.dataset.src;
            io.unobserve(frame);
          }
        });
      },
      { rootMargin: '200px 0px' }
    );
    lazyFrames.forEach((f) => io.observe(f));
  } else {
    lazyFrames.forEach((f) => (f.src = f.dataset.src));
  }

  /* iframe 자동 스케일 — 컨테이너 폭 / 디자인 폭 */
  const fitFrame = (frame, designW) => {
    const wrap = frame.parentElement;
    if (!wrap) return;
    const w = wrap.clientWidth;
    const scale = w / designW;
    frame.style.transform = `scale(${scale})`;
    // 부모 높이를 맞춰 잘림 방지
    const designH = parseFloat(frame.style.height) || frame.offsetHeight;
    wrap.style.height = designH * scale + 'px';
  };

  const refit = () => {
    document
      .querySelectorAll('.preview-desktop')
      .forEach((f) => fitFrame(f, 1440));
    document
      .querySelectorAll('.preview-mobile')
      .forEach((f) => fitFrame(f, 390));
  };

  window.addEventListener('load', refit);
  window.addEventListener('resize', refit);
  // 폰트 로드/초기 레이아웃 변경 대응
  setTimeout(refit, 100);
  setTimeout(refit, 600);
})();
