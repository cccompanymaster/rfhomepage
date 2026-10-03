/* ============================================================
   홈 첫 화면 — 기기 목업 쇼케이스
   위 줄: 모니터(데스크톱 화면) · 아래 줄: 휴대폰(모바일 화면). 같은 디자인끼리 세로로 짝.
   흐름: 고르기(‹ › · 스와이프 · 옆 기기 클릭) → 펼쳐 보기(두 화면이 실제처럼 스크롤)
        → [다른 디자인 보기] / [홈페이지로 보기] / [이게 좋겠어요!] → 히어로
   첫 방문(세션당 1회) 자동 표시, 홈 레퍼런스 구간 버튼으로 다시 열 수 있음.
   ============================================================ */
import { DESIGNS } from './showcase-data.js?v=f673054c';

window.__scReady = true;   // <head> 안전장치: 이 스크립트가 안 뜨면 쇼케이스를 걷어냄

const SEEN_KEY = 'noah_intro_seen';
const html = document.documentElement;
const root = document.getElementById('showcase-intro');
const N = DESIGNS.length;
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');

let sel = 0;
let mode = 'shelf';
let built = false;
let leaving = false;
let geo = { mw: 560, pw: 150, mrow: 380, prow: 300, gap: 18, spacing: 380, narrow: false };
let items = [];   // [{ mon, phone }]

const $ = (s) => root.querySelector(s);
const track = (name, params) => { if (typeof gtag === 'function') gtag('event', name, params || {}); };
const circ = (i) => { let d = (i - sel) % N; if (d > N / 2) d -= N; if (d < -N / 2) d += N; return d; };

/* ── 기기 만들기 ── */
function build() {
  if (built) return;
  built = true;
  const mRow = $('[data-row="d"]');
  const pRow = $('[data-row="m"]');
  DESIGNS.forEach((d, i) => {
    const mon = document.createElement('button');
    mon.type = 'button';
    mon.className = 'sc-item sc-monitor';
    mon.dataset.i = i;
    mon.setAttribute('aria-label', `${d.nameKo} — ${d.industryKo}`);
    mon.innerHTML = '<span class="sc-screen"><span class="sc-view"><img class="sc-first" alt="" decoding="async"></span></span><span class="sc-stand" aria-hidden="true"></span>';
    const phone = document.createElement('button');
    phone.type = 'button';
    phone.className = 'sc-item sc-phone';
    phone.dataset.i = i;
    phone.tabIndex = -1;
    phone.setAttribute('aria-hidden', 'true');
    phone.innerHTML = '<span class="sc-screen"><span class="sc-view"><img class="sc-first" alt="" decoding="async"></span></span>';
    mRow.appendChild(mon);
    pRow.appendChild(phone);
    items.push({ mon, phone });
  });
  items.forEach(({ mon, phone }) => {
    for (const img of [mon.querySelector('img'), phone.querySelector('img')]) {
      img.addEventListener('load', () => img.classList.add('is-loaded'));
    }
  });
}

/* 보이는 것(가운데 ±3)부터 이미지 로드, 나머지는 한가할 때 */
function loadNear(radius = 3) {
  items.forEach(({ mon, phone }, i) => {
    if (Math.abs(circ(i)) > radius) return;
    const d = DESIGNS[i];
    const a = mon.querySelector('img.sc-first');
    const b = phone.querySelector('img.sc-first');
    if (!a.src) a.src = d.d;
    if (!b.src) b.src = d.m;
  });
}

/* ── 크기 계산: 화면 높이·폭에 맞춰 두 줄을 배치 ── */
function measure() {
  const stage = $('.sc-stage');
  const H = stage.clientHeight;
  const W = root.clientWidth;
  const narrow = W < 720;
  const gap = Math.round(Math.max(10, H * 0.035));
  const mrow = Math.round((H - gap) * 0.56);
  const prow = H - gap - mrow;
  const mw = Math.floor(Math.min(mrow / 0.725, W * (narrow ? 0.8 : 0.48), 860));
  const pw = Math.floor(Math.min((prow * 0.97) / 2.164, mw * 0.34));
  const spacing = narrow ? mw * 0.96 : mw * 0.7;
  geo = { mw, pw, mrow, prow, gap, spacing, narrow };
  root.style.setProperty('--mw', `${mw}px`);
  root.style.setProperty('--pw', `${pw}px`);
  root.style.setProperty('--mrow', `${mrow}px`);
  root.style.setProperty('--prow', `${prow}px`);
  root.style.setProperty('--row-gap', `${gap}px`);
}

/* ── 배치: 가운데 크게, 양옆은 작게 기울여서 (모니터·휴대폰 같은 x 로 세로 정렬) ── */
const SCALE = [1, 0.78, 0.64, 0.56];
const ALPHA = [1, 0.85, 0.5, 0.22];
function place() {
  const { mw, pw, prow, gap, spacing, narrow } = geo;
  const maxVisible = narrow ? 1 : 3;
  items.forEach(({ mon, phone }, i) => {
    const off = circ(i);
    const a = Math.abs(off);
    const sgn = Math.sign(off);
    const far = a > maxVisible;
    const x = a === 0 ? 0 : sgn * spacing * (1 + (a - 1) * 0.62);
    const s = SCALE[Math.min(a, 3)];
    const rot = -sgn * Math.min(a, 3) * (narrow ? 10 : 15);
    let op = far ? 0 : ALPHA[Math.min(a, 3)];
    let mT = `translateX(-50%) translateX(${x}px) rotateY(${rot}deg) scale(${s})`;
    let pT = mT;

    if (mode === 'detail') {
      if (a !== 0) {
        op = 0;
        mT = `translateX(-50%) translateX(${x * 1.5}px) rotateY(${rot}deg) scale(${s * 0.9})`;
        pT = mT;
      } else {
        // 펼침: 비어 있는 두 줄 공간을 한 쌍이 채우도록 키우고 세로 가운데로.
        // 모니터는 살짝 왼쪽, 휴대폰은 모니터 오른쪽 아래에 겹쳐 세움.
        const H = geo.mrow + gap + prow;
        const W = root.clientWidth;
        const mh = mw * 0.725;                                   // 모니터(받침 포함) 높이
        const k = Math.max(1, Math.min(narrow ? 1.12 : 1.6, (H * 0.86) / mh, (W * (narrow ? 0.84 : 0.62)) / mw));
        const dyMon = H * 0.5 + (k * mh) / 2 - geo.mrow;         // 모니터 세로 가운데
        const shift = narrow ? -mw * k * 0.02 : -mw * k * 0.08;
        mT = `translateX(-50%) translate(${shift}px, ${dyMon}px) scale(${k})`;
        const kp = k * (narrow ? 0.92 : 1.02);
        const monBottom = geo.mrow + dyMon;                       // 모니터 받침 바닥
        const dyPhone = monBottom + mw * k * 0.02 - H;            // 휴대폰 바닥을 받침 높이에
        const px = shift + mw * k * (narrow ? 0.36 : 0.42);
        pT = `translateX(-50%) translate(${px}px, ${dyPhone}px) scale(${kp})`;
      }
    }
    for (const [el, t] of [[mon, mT], [phone, pT]]) {
      el.style.transform = t;
      el.style.opacity = op;
      el.style.zIndex = String(20 - a);
      el.dataset.off = String(off);
      el.classList.toggle('is-far', op === 0);
    }
    mon.tabIndex = a === 0 ? 0 : -1;
  });
}

/* ── 선택·캡션 ── */
function select(i, announce = true) {
  sel = ((i % N) + N) % N;
  const d = DESIGNS[sel];
  root.style.setProperty('--accent', d.accent);
  $('[data-sc-name]').textContent = d.nameKo;
  $('[data-sc-meta]').textContent = `${d.industryKo} · ${d.tagKo}`;
  $('[data-sc-count]').textContent = `${sel + 1} / ${N}`;
  $('[data-sc-d-eyebrow]').textContent = `REFERENCE · ${String(sel + 1).padStart(2, '0')} · ${d.industryKo}`;
  $('[data-sc-d-name]').textContent = d.nameKo;
  $('[data-sc-d-tag]').textContent = d.tagKo;
  $('[data-sc="visit"]').href = d.url;
  loadNear();
  place();
  if (announce) $('.sc-live').textContent = `${sel + 1}번째, ${d.nameKo}. ${d.industryKo}.`;
}

/* ── 펼치기: 두 화면을 긴 캡처로 바꿔 천천히 스크롤 ── */
function startScroll(view, src, ratio) {
  let tall = view.querySelector('img.sc-tall');
  if (!tall) {
    tall = document.createElement('img');
    tall.className = 'sc-tall';
    tall.alt = '';
    tall.decoding = 'async';
    tall.addEventListener('load', () => tall.classList.add('is-loaded'));
    view.appendChild(tall);
  }
  const w = view.clientWidth;
  const h = view.clientHeight;
  const shift = Math.min(0, h - w * ratio);
  view.style.setProperty('--shift', `${Math.round(shift)}px`);
  view.style.setProperty('--dur', `${Math.max(8, Math.min(20, Math.abs(shift) / 45)).toFixed(1)}s`);
  if (!tall.src) tall.src = src;
  if (!reduceMotion.matches) view.classList.add('is-scrolling');
}
function stopScroll() {
  root.querySelectorAll('.sc-view.is-scrolling').forEach((v) => v.classList.remove('is-scrolling'));
}

let scrollTimer = 0;
function scheduleDetailScroll() {
  clearTimeout(scrollTimer);
  // 기기가 자리 잡은 뒤 크기를 재야 스크롤 길이가 맞음
  scrollTimer = setTimeout(() => {
    if (mode !== 'detail') return;
    const d = DESIGNS[sel];
    const { mon, phone } = items[sel];
    startScroll(mon.querySelector('.sc-view'), d.dt, d.dtRatio);
    startScroll(phone.querySelector('.sc-view'), d.mt, d.mtRatio);
  }, reduceMotion.matches ? 0 : 650);
}

function setMode(next) {
  mode = next;
  root.dataset.mode = next;
  $('[data-sc-bar="shelf"]').hidden = next === 'detail';
  $('[data-sc-bar="detail"]').hidden = next !== 'detail';
  place();
  const d = DESIGNS[sel];
  if (next === 'detail') {
    scheduleDetailScroll();
    $('.sc-live').textContent = `${d.nameKo}을 펼쳤습니다. 다른 디자인 보기, 홈페이지로 보기, 이게 좋겠어요 버튼이 있습니다.`;
    track('intro_open', { item: d.slug });
    $('[data-sc="how"]').focus({ preventScroll: true });
  } else {
    stopScroll();
    $('.sc-stage').focus({ preventScroll: true });
  }
}

/* ── 열기 / 나가기 ── */
function start() {
  leaving = false;
  root.classList.remove('is-leaving');
  html.classList.add('intro-on');
  build();
  measure();
  mode = 'shelf';
  root.dataset.mode = 'shelf';
  $('[data-sc-bar="shelf"]').hidden = false;
  $('[data-sc-bar="detail"]').hidden = true;
  select(sel, false);
  track('intro_view');
  requestAnimationFrame(() => $('.sc-stage').focus({ preventScroll: true }));
  const idle = window.requestIdleCallback || ((fn) => setTimeout(fn, 1200));
  idle(() => loadNear(N));
}

function exit(method) {
  if (leaving) return;
  leaving = true;
  try { sessionStorage.setItem(SEEN_KEY, '1'); } catch (_) {}
  track('intro_exit', { method, item: DESIGNS[sel]?.slug });
  window.scrollTo(0, 0);
  const finish = () => {
    stopScroll();
    html.classList.remove('intro-on', 'intro-leaving');
    root.classList.remove('is-leaving');
    const h1 = document.querySelector('#hero h1');
    if (h1) { h1.setAttribute('tabindex', '-1'); h1.focus({ preventScroll: true }); }
  };
  html.classList.add('intro-leaving');
  root.classList.add('is-leaving');
  setTimeout(finish, reduceMotion.matches ? 220 : 980);
}

/* ── 입력 ── */
let swipe = null;
let swallowClick = false;
root?.addEventListener('pointerdown', (e) => {
  if (!e.target.closest('.sc-stage')) return;
  swipe = { x: e.clientX, y: e.clientY };
});
root?.addEventListener('pointerup', (e) => {
  if (!swipe) return;
  const dx = e.clientX - swipe.x;
  const dy = e.clientY - swipe.y;
  swipe = null;
  if (mode === 'shelf' && Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
    swallowClick = true;
    select(sel + (dx < 0 ? 1 : -1));
    setTimeout(() => { swallowClick = false; }, 0);
  }
});

root?.addEventListener('click', (e) => {
  if (swallowClick) return;
  const act = e.target.closest('[data-sc]')?.dataset.sc;
  if (act === 'prev') return select(sel - 1);
  if (act === 'next') return select(sel + 1);
  if (act === 'open') return setMode('detail');
  if (act === 'back') return setMode('shelf');
  if (act === 'how') return exit('how');
  if (act === 'skip') return exit('skip');
  if (act === 'visit') return track('intro_visit', { item: DESIGNS[sel].slug });
  const item = e.target.closest('.sc-item');
  if (!item || mode !== 'shelf') return;
  const i = Number(item.dataset.i);
  if (i === sel) setMode('detail');
  else select(i);
});

root?.addEventListener('keydown', (e) => {
  if (e.target.closest('input, textarea')) return;
  if (e.key === 'Escape') { e.preventDefault(); return mode === 'detail' ? setMode('shelf') : exit('skip'); }
  if (mode !== 'shelf') return;
  if (e.key === 'ArrowRight') { e.preventDefault(); select(sel + 1); }
  else if (e.key === 'ArrowLeft') { e.preventDefault(); select(sel - 1); }
  else if (e.key === 'Enter' && e.target.closest('.sc-stage')) { e.preventDefault(); setMode('detail'); }
});

let resizeRaf = 0;
window.addEventListener('resize', () => {
  if (!html.classList.contains('intro-on')) return;
  cancelAnimationFrame(resizeRaf);
  resizeRaf = requestAnimationFrame(() => {
    measure();
    place();
    if (mode === 'detail') { stopScroll(); scheduleDetailScroll(); }
  });
});

/* 홈 레퍼런스 구간의 "펼쳐 보기" */
document.querySelectorAll('[data-showcase-open]').forEach((el) => {
  el.addEventListener('click', () => { window.scrollTo(0, 0); start(); });
});

if (root && html.classList.contains('intro-on')) start();
