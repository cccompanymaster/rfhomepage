/* 메인 페이지 공통 (홈·레퍼런스·제작 과정·가격·상담) — 모바일 메뉴, 소개서 신청창 */
// 노아폼백엔드 (Apps Script) — 소개서·상담 신청 기록
const GAS_URL = 'https://script.google.com/macros/s/AKfycbz-048UbQ15LMY3j847AqQmZ7Zu4hNDyqAQEVjD60BKsqQmZDvS1YBbmyab8jjscEz-/exec';

function closeNav(){document.getElementById('mnav').classList.remove('open');document.body.style.overflow='';}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeNav();});

// 가격 비교 카드 — 화면에 들어오면 막대가 자람 (움직임 줄이기면 바로 다 보임)
document.querySelectorAll('.cmp-card').forEach((card) => {
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  card.classList.add('is-armed');
  const io = new IntersectionObserver((es) => {
    if (es.some((e) => e.isIntersecting)) { card.classList.add('is-on'); io.disconnect(); }
  }, { threshold: 0.25 });
  io.observe(card);
});

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

  brochureSubmit.disabled = true;
  brochureSubmit.textContent = '전송 중...';
  brochureStatus.style.color = 'var(--text-dim)';
  brochureStatus.textContent = '';

  const fd = new FormData(brochureForm);
  const payload = { type: 'brochure' };
  fd.forEach((v, k) => { payload[k] = v; });
  payload.timestamp = new Date().toISOString();
  payload.referrer = document.referrer || '직접 접속';

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
