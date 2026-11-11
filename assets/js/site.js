/* 메인 페이지 공통 (홈·레퍼런스·제작 과정·가격·상담) — 모바일 메뉴, 소개서 신청창 */
// 노아폼백엔드 (Apps Script) — 소개서·상담 신청 기록
const GAS_URL = 'https://script.google.com/macros/s/AKfycbz-048UbQ15LMY3j847AqQmZ7Zu4hNDyqAQEVjD60BKsqQmZDvS1YBbmyab8jjscEz-/exec';

// 모바일 메뉴 — 열고 닫을 때 버튼 상태(aria-expanded)와 포커스를 함께 옮김
const navBtn = document.querySelector('[data-nav-open]');
function openNav(){
  const m=document.getElementById('mnav'); if(!m) return;
  m.classList.add('open'); document.body.style.overflow='hidden';
  navBtn?.setAttribute('aria-expanded','true');
  m.querySelector('a, button')?.focus();
}
function closeNav(){
  const m=document.getElementById('mnav'); if(!m || !m.classList.contains('open')) return;
  m.classList.remove('open'); document.body.style.overflow='';
  navBtn?.setAttribute('aria-expanded','false');
  navBtn?.focus();
}
navBtn?.addEventListener('click', openNav);
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeNav();});

// ====================== 떠 있는 요소 정리 ======================
// 하단 상담 바: 첫 화면을 지나면 나타나고, 마지막 상담 블록·푸터([data-dock-stop])가 보이면 들어감.
// 블로그 안내 팝업: 넓은 화면(1200px 이상)에서 페이지를 30% 넘게 읽은 뒤부터.
(() => {
  const root = document.documentElement;
  const dock = document.querySelector('.banner-bottom');
  const pop = document.getElementById('blog-pop');
  if (!dock && !pop) return;
  root.classList.add('dock-ready');
  const stops = new Set();
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((es) => {
      es.forEach((e) => (e.isIntersecting ? stops.add(e.target) : stops.delete(e.target)));
      update();
    });
    document.querySelectorAll('[data-dock-stop]').forEach((el) => io.observe(el));
  }
  let popArmed = false;
  const wide = matchMedia('(min-width: 1200px)');
  function update() {
    const y = window.scrollY;
    const vh = window.innerHeight;
    if (dock && !dock.classList.contains('is-hidden')) {
      dock.classList.toggle('is-shown', y > vh * 0.7 && stops.size === 0);
    }
    if (pop && wide.matches && !pop.classList.contains('is-hidden')) {
      const max = document.documentElement.scrollHeight - vh;
      if (max > 0 && y / max > 0.3) popArmed = true;
      // 한 번 나타난 뒤에도 첫 화면·마지막 상담 블록·푸터에서는 숨김 — 본문을 가리지 않게
      pop.classList.toggle('is-shown', popArmed && y > vh * 0.7 && stops.size === 0);
    }
  }
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return; ticking = true;
    requestAnimationFrame(() => { ticking = false; update(); });
  }, { passive: true });
  window.addEventListener('resize', update, { passive: true });
  update();
})();

// ====================== 소개서 모달 토글 ======================
const brochureModal = document.getElementById('brochure-modal');
const brochureTrigger = document.getElementById('brochure-trigger');
const brochureClose = document.getElementById('brochure-close');
const brochureForm = document.getElementById('brochure-form');
const brochureStatus = document.getElementById('brochure-status');
const brochureSubmit = document.getElementById('brochure-submit');

const openBrochure = () => { brochureModal?.classList.add('is-open'); document.body.style.overflow = 'hidden'; };
const closeBrochure = () => { brochureModal?.classList.remove('is-open'); document.body.style.overflow = ''; brochureStatus.textContent = ''; };
brochureTrigger?.addEventListener('click', openBrochure);
brochureClose?.addEventListener('click', closeBrochure);
brochureModal?.addEventListener('click', (e) => { if (e.target === brochureModal) closeBrochure(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeBrochure(); });

// 소개서 폼 제출 (Apps Script로 전송 + PDF 즉시 다운로드)
const BROCHURE_URL = './assets/brochure/NOAH-brochure.pdf';
const BROCHURE_FILENAME = 'NOAH_소개서.pdf';
const triggerBrochureDownload = (source = 'unknown') => {
  const a = document.createElement('a');
  a.href = BROCHURE_URL;
  a.download = BROCHURE_FILENAME;
  a.rel = 'noopener';
  document.body.appendChild(a);
  a.click();
  a.remove();
  if (typeof gtag === 'function') {
    gtag('event', 'brochure_download', {
      event_category: 'engagement',
      event_label: source,
      file_name: BROCHURE_FILENAME,
    });
  }
};

brochureForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!brochureForm.checkValidity()) { brochureForm.reportValidity(); return; }
  if (brochureForm.elements.website?.value) { brochureForm.reset(); return; }  // 봇 허니팟 (사람 눈엔 안 보이는 칸)

  brochureSubmit.disabled = true;
  brochureSubmit.textContent = '전송 중...';
  brochureStatus.style.color = 'var(--text-dim)';
  brochureStatus.textContent = '';

  const fd = new FormData(brochureForm);
  const payload = { type: 'brochure' };
  fd.forEach((v, k) => { payload[k] = v; });
  payload.timestamp = new Date().toISOString();
  payload.referrer = (window.NOAH_SRC?.text() || document.referrer || '직접 접속');  // 광고·검색·AI 등 들어온 경로 (assets/js/attrib.js)

  // 1) PDF 즉시 다운로드 (Apps Script 응답을 기다리지 않음)
  triggerBrochureDownload('brochure_modal');

  // GA4: 소개서 모달 제출 이벤트
  if (typeof gtag === 'function') {
    gtag('event', 'brochure_submit', {
      event_category: 'lead',
      event_label: 'brochure_modal',
    });
  }

  // 2) 백그라운드로 Apps Script에 신청 기록 (실패해도 다운로드는 이미 시작됨)
  try {
    await fetch(GAS_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(payload),
    });
    brochureStatus.style.color = '#34d399';
    brochureStatus.textContent = '✓ 소개서 다운로드를 시작했어요. 입력하신 메일로도 한 번 더 보내드릴게요.';
    brochureForm.reset();
    setTimeout(closeBrochure, 2600);
  } catch (err) {
    brochureStatus.style.color = '#fbbf24';
    brochureStatus.textContent = '✓ 다운로드는 시작했어요. (이메일 전송은 잠시 후 자동 처리됩니다)';
    brochureForm.reset();
    setTimeout(closeBrochure, 2600);
  } finally {
    brochureSubmit.disabled = false;
    brochureSubmit.textContent = '소개서 받기 →';
  }
});

// ====================== 블로그 팝업 닫기 (세션 기억) ======================
const blogPop = document.getElementById('blog-pop');
try {
  if (sessionStorage.getItem('blog-pop-dismissed') === '1') {
    blogPop?.classList.add('is-hidden');
  }
} catch (_) {}
document.querySelector('[data-blog-close]')?.addEventListener('click', () => {
  blogPop?.classList.add('is-hidden');
  try { sessionStorage.setItem('blog-pop-dismissed', '1'); } catch (_) {}
});

// ====================== 이벤트 선정자 배너 닫기 (세션 기억) ======================
const eventBanner = document.getElementById('event-banner');
try {
  if (sessionStorage.getItem('event-banner-dismissed') === '1') {
    eventBanner?.classList.add('is-hidden');
  }
} catch (_) {}
document.getElementById('event-banner-close')?.addEventListener('click', (e) => {
  e.preventDefault();
  eventBanner?.classList.add('is-hidden');
  try { sessionStorage.setItem('event-banner-dismissed', '1'); } catch (_) {}
});
eventBanner?.querySelector('a')?.addEventListener('click', () => {
  if (typeof gtag === 'function') {
    gtag('event', 'intake_banner_click', { event_category: 'navigation', event_label: 'event_winner_banner' });
  }
});
