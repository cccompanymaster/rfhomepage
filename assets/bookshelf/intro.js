/* ============================================================
   홈 첫 화면 — 레퍼런스 책장 호스트 (ThreeUI BookshelfScene.tsx 를 바닐라로 옮김)
   - 렌더러는 화면에 보일 때만 불러오고(약 1.3MB), 닫으면 dispose 로 GPU 자원을 모두 반납
   - 흐름: 책장 → 책 선택(펼침) → [다른 디자인 보기] 책장으로 / [어떻게 만들죠?] 히어로로
   - 첫 방문(세션당 1회) 자동 표시, 홈 레퍼런스 구간의 버튼으로 다시 열 수 있음
   ============================================================ */
import { SITE_BOOKS } from './books-site.js?v=4e9a0ba9';

const SEEN_KEY = 'noah_intro_seen';
const html = document.documentElement;
const root = document.getElementById('shelf-intro');

let renderer = null;
let resizeObserver = null;
let modeObserver = null;
let selected = 0;
let leaving = false;
let readyTimer = 0;

const $ = (sel) => root.querySelector(sel);
const track = (name, params) => { if (typeof gtag === 'function') gtag('event', name, params || {}); };

function setSelection(index) {
  selected = index;
  const b = SITE_BOOKS[index];
  if (!b) return;
  root.style.setProperty('--si-ink', b.ink);
  root.style.setProperty('--si-ink-soft', hexA(b.ink, 0.74));
  root.style.setProperty('--si-wall', b.wall);
  $('[data-si-name]').textContent = b.nameKo;
  $('[data-si-meta]').textContent = `${b.industryKo} · ${b.tagKo}`;
  $('[data-si-count]').textContent = `${index + 1} / ${SITE_BOOKS.length}`;
  $('[data-si="visit"]').href = b.url;
  $('[data-si-d-eyebrow]').textContent = `REFERENCE · ${String(index + 1).padStart(2, '0')} · ${b.industryKo}`;
  $('[data-si-d-name]').textContent = b.nameKo;
  $('[data-si-d-tag]').textContent = b.tagKo;
}

function setMode(mode) {
  root.dataset.mode = mode;
  $('[data-si-bar="shelf"]').hidden = mode === 'detail';
  $('[data-si-bar="detail"]').hidden = mode !== 'detail';
  const live = $('.si-live');
  const b = SITE_BOOKS[selected];
  live.textContent = mode === 'detail'
    ? `${b.nameKo}을 펼쳤습니다. 이 디자인 열어보기, 다른 디자인 보기, 어떻게 만들죠 버튼이 있습니다.`
    : '책장으로 돌아왔습니다.';
  if (mode === 'detail') track('intro_open_book', { item: b.slug });
}

/* 펼치기·닫기 애니메이션 중에는 렌더러가 명령을 받지 않으므로 버튼도 잠깐 쉼 */
let busyTimer = 0;
function setBusy(on) {
  clearTimeout(busyTimer);
  root.toggleAttribute('data-busy', on);
  root.querySelectorAll('.si-bar .si-btn:not([data-si="how"]):not([data-si="visit"])').forEach((b) => b.setAttribute('aria-disabled', on ? 'true' : 'false'));
  if (on) busyTimer = setTimeout(() => setBusy(false), 12000);   // 완료 신호가 안 올 때만 쓰는 안전장치
}

function hexA(hex, a) {
  const h = hex.replace('#', '');
  const n = parseInt(h.length === 3 ? h.replace(/./g, '$&$&') : h, 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
}

async function start() {
  if (renderer || !root) return;
  leaving = false;
  root.classList.remove('is-leaving');
  root.dataset.state = 'loading';
  html.classList.add('intro-on');
  setSelection(0);
  setMode('shelf');
  track('intro_view');

  const host = $('.bookshelf');
  const canvas = $('.bookshelf__canvas');
  try {
    const { createBookshelfRenderer } = await import(root.dataset.renderer);
    renderer = createBookshelfRenderer(host, canvas, {
      onReady: () => {
        root.dataset.state = 'ready';
        canvas.classList.add('is-ready');
        clearTimeout(readyTimer);
        host.focus({ preventScroll: true });
      },
      onError: () => exit('error', true),
      onSelectionChange: ({ index }) => setSelection(index),
      onModeChange: (mode) => { const m = mode === 'detail' ? 'detail' : 'shelf'; if (root.dataset.mode !== m) setMode(m); setBusy(false); },
    });
    renderer.ready.catch(() => exit('error', true));
    resizeObserver = new ResizeObserver(() => renderer && renderer.resize());
    resizeObserver.observe(host);
    // 펼침/닫힘을 '애니메이션이 끝난 뒤'가 아니라 '시작하는 순간' 반영 —
    // 렌더러가 펼치기 시작할 때 host 에 mode-detail 을 붙이고, 닫기 시작할 때 뗍니다.
    // (책을 버튼이 아니라 직접 눌러 펼친 경우도 여기서 잡힘)
    modeObserver = new MutationObserver(() => {
      const next = host.classList.contains('mode-detail') ? 'detail' : 'shelf';
      if (root.dataset.mode !== next) { setMode(next); setBusy(true); }
    });
    modeObserver.observe(host, { attributes: true, attributeFilter: ['class'] });
    // 느린 기기에서 오래 걸리면 건너뛰기를 눈에 띄게
    readyTimer = setTimeout(() => { if (root.dataset.state !== 'ready') $('.si-skip').classList.add('is-primary'); }, 9000);
  } catch (err) {
    exit('error', true);
  }
}

function teardown() {
  clearTimeout(readyTimer);
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null; }
  if (modeObserver) { modeObserver.disconnect(); modeObserver = null; }
  if (renderer) { try { renderer.dispose(); } catch (_) {} renderer = null; }
  $('.bookshelf__canvas').classList.remove('is-ready');
}

/* 책장을 위로 걷어 올리고 히어로를 보여줌 */
function exit(method, instant = false) {
  if (leaving) return;
  leaving = true;
  try { sessionStorage.setItem(SEEN_KEY, '1'); } catch (_) {}
  if (method !== 'error') track('intro_exit', { method, item: SITE_BOOKS[selected]?.slug });
  window.scrollTo(0, 0);

  const finish = () => {
    teardown();
    html.classList.remove('intro-on', 'intro-leaving');
    root.classList.remove('is-leaving');
    const h1 = document.querySelector('#hero h1');
    if (h1) { h1.setAttribute('tabindex', '-1'); h1.focus({ preventScroll: true }); }
  };
  if (instant) { finish(); return; }
  html.classList.add('intro-leaving');
  root.classList.add('is-leaving');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  setTimeout(finish, reduce ? 220 : 980);
}

/* ── 버튼 ── */
root?.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-si]');
  if (!btn || btn.getAttribute('aria-disabled') === 'true') return;
  const act = btn.dataset.si;
  if (act === 'prev') renderer?.previousVolume();
  else if (act === 'next') renderer?.nextVolume();
  else if (act === 'open') renderer?.open();
  else if (act === 'back') renderer?.close();
  else if (act === 'how') exit('how');
  else if (act === 'skip') exit('skip');
  else if (act === 'visit') track('intro_visit', { item: SITE_BOOKS[selected]?.slug });
});

/* 책장이 열린 상태에서 Esc: 펼친 책이면 renderer 가 닫고, 책장이면 히어로로 */
root?.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && root.dataset.mode !== 'detail') exit('skip');
});

/* 홈 레퍼런스 구간의 "책장 열어보기" */
document.querySelectorAll('[data-shelf-open]').forEach((el) => {
  el.addEventListener('click', () => { window.scrollTo(0, 0); start(); });
});

/* 첫 진입: <head> 게이트가 intro-on 을 붙였으면 바로 시작 */
if (html.classList.contains('intro-on')) start();
