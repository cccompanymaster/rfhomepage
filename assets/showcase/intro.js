/* ============================================================
   홈 첫 화면 — 기기 목업 쇼케이스
   위 줄: 모니터(데스크톱 화면) · 아래 줄: 휴대폰(모바일 화면). 같은 디자인끼리 세로로 짝.
   흐름: 고르기(‹ › · 스와이프 · 옆 기기 클릭, 한 디자인에 1초 머물면 두 화면이 스크롤)
        → 펼쳐 보기(크게 띄워 실제처럼 스크롤)
        → [다른 디자인 보기] / [홈페이지로 보기] / [이게 좋겠어요!] → 히어로
   첫 방문(세션당 1회) 자동 표시, 홈 레퍼런스 구간 버튼으로 다시 열 수 있음.
   ============================================================ */
import { DESIGNS } from './showcase-data.js?v=fd0c3710';

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
let geo = { mw: 560, pw: 150, H: 600, W: 1200, narrow: false };
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

/* ── 크기 계산 ──
   넓은 화면: 모니터 + 오른쪽 아래에 겹쳐 선 휴대폰을 한 쌍으로, 가운데 한 쌍을 무대에 꽉 차게.
   좁은 화면: 위 모니터 · 아래 휴대폰 두 줄, 화면 폭을 거의 다 쓰게. 양옆엔 다음 디자인이 살짝 보임 */
function measure() {
  const stage = $('.sc-stage');
  const H = stage.clientHeight;
  const W = root.clientWidth;
  const narrow = W < 720;
  root.dataset.layout = narrow ? 'rows' : 'pair';
  if (!narrow) {
    // 모니터(받침 포함) 높이 = 폭 × 0.725 — 무대 높이의 86%, 화면 폭의 58%까지
    const mw = Math.floor(Math.min((H * 0.86) / 0.725, W * 0.58, 1180));
    geo = { mw, pw: Math.round(mw * 0.26), H, W, narrow };
  } else {
    const gap = Math.round(Math.max(10, H * 0.03));
    const mrow = Math.round((H - gap) * 0.5);
    const prow = H - gap - mrow;
    const mw = Math.floor(Math.min(mrow / 0.725, W * 0.84));
    const pw = Math.floor(Math.min((prow * 0.97) / 2.164, mw * 0.42));
    geo = { mw, pw, mrow, prow, gap, H, W, narrow };
    root.style.setProperty('--mrow', `${mrow}px`);
    root.style.setProperty('--prow', `${prow}px`);
    root.style.setProperty('--row-gap', `${gap}px`);
  }
  root.style.setProperty('--mw', `${geo.mw}px`);
  root.style.setProperty('--pw', `${geo.pw}px`);
}

/* 넓은 화면의 한 쌍: 가운데 x, 배율 k, 기울기 rot → [모니터, 휴대폰] transform.
   두 줄이 무대 전체에 겹쳐 있고(바닥 = 무대 바닥), 쌍을 세로 가운데에 세움 */
function pairT(x, k, rot) {
  const { mw, H } = geo;
  const monBottom = H / 2 + (mw * 0.725 * k) / 2;
  const mx = x - mw * k * 0.08;
  const px = mx + mw * k * 0.42;
  const r = rot ? ` rotateY(${rot}deg)` : '';
  return [
    `translateX(-50%) translate(${mx}px, ${monBottom - H}px)${r} scale(${k})`,
    `translateX(-50%) translate(${px}px, ${monBottom + mw * k * 0.02 - H}px)${r} scale(${k})`,
  ];
}

const SCALE = [1, 0.78, 0.64, 0.56];
function place() {
  const { mw, H, W, narrow } = geo;
  items.forEach(({ mon, phone }, i) => {
    const off = circ(i);
    const a = Math.abs(off);
    const sgn = Math.sign(off);
    let op, mT, pT;

    if (!narrow) {
      if (mode === 'detail') {
        // 펼침: 옆 디자인은 치우고 가운데 한 쌍만 조금 더 크게
        const k = Math.max(1, Math.min(1.12, (H * 0.92) / (mw * 0.725), (W * 0.66) / mw));
        op = a === 0 ? 1 : 0;
        [mT, pT] = a === 0 ? pairT(0, k, 0) : pairT(sgn * W * 0.75, 0.7, -sgn * 14);
      } else {
        // 고르기: 가운데 크게, 바로 옆 디자인은 화면 가장자리에 반쯤 걸쳐 보이게
        op = a === 0 ? 1 : a === 1 ? 0.55 : 0;
        [mT, pT] = a === 0 ? pairT(0, 1, 0) : pairT(sgn * W * (a === 1 ? 0.52 : 0.9), a === 1 ? 0.72 : 0.6, -sgn * 14);
      }
    } else {
      const { pw, prow, gap } = geo;
      const x = a === 0 ? 0 : sgn * W * (0.7 + (a - 1) * 0.5);   // 바로 옆 디자인이 가장자리에 걸쳐 보이게
      const s = SCALE[Math.min(a, 3)];
      const rot = -sgn * Math.min(a, 3) * 10;
      op = a === 0 ? 1 : a === 1 ? 0.5 : 0;
      mT = `translateX(-50%) translateX(${x}px) rotateY(${rot}deg) scale(${s})`;
      pT = mT;
      if (mode === 'detail') {
        if (a !== 0) {
          op = 0;
          mT = `translateX(-50%) translateX(${x * 1.5}px) rotateY(${rot}deg) scale(${s * 0.9})`;
          pT = mT;
        } else {
          // 펼침: 비어 있는 두 줄 공간을 한 쌍이 채우도록 키우고 세로 가운데로 (휴대폰은 모니터 오른쪽 아래에 겹침)
          const HH = geo.mrow + gap + prow;
          const mh = mw * 0.725;
          const k = Math.max(1, Math.min(1.12, (HH * 0.86) / mh, (W * 0.84) / mw));
          const dyMon = HH * 0.5 + (k * mh) / 2 - geo.mrow;
          const shift = -mw * k * 0.02;
          mT = `translateX(-50%) translate(${shift}px, ${dyMon}px) scale(${k})`;
          const dyPhone = geo.mrow + dyMon + mw * k * 0.02 - HH;
          const kp = Math.min(k * 0.92, (mw * k * 0.36) / pw);
          pT = `translateX(-50%) translate(${shift + mw * k * 0.36}px, ${dyPhone}px) scale(${kp})`;
        }
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
  scheduleScroll();
  if (announce) $('.sc-live').textContent = `${sel + 1}번째, ${d.nameKo}. ${d.industryKo}.`;
}

/* ── 두 화면을 긴 캡처로 바꿔 천천히 스크롤 ── */
function startScroll(view, src, ratio, delay) {
  if (view.classList.contains('is-scrolling')) return;   // 고르다 펼치면 하던 스크롤을 이어감
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
  view.style.setProperty('--delay', `${delay}s`);
  if (!tall.src) tall.src = src;
  // 다 받아진 뒤 바꿔 끼움 (빈 화면 깜빡임 없게). 그새 다른 디자인으로 넘어갔으면 켜지 않음
  const go = () => { if (!leaving && view.closest('.sc-item').dataset.off === '0') view.classList.add('is-scrolling'); };
  if (tall.complete && tall.naturalWidth) go(); else tall.addEventListener('load', go, { once: true });
}
function stopScroll() {
  root.querySelectorAll('.sc-view.is-scrolling').forEach((v) => v.classList.remove('is-scrolling'));
}

/* 고르는 중 1초 머물면, 펼친 뒤엔 기기가 자리 잡으면(0.65초) 가운데 모니터·휴대폰이 스크롤 */
let scrollTimer = 0;
function scheduleScroll() {
  clearTimeout(scrollTimer);
  if (mode === 'shelf') stopScroll();
  if (reduceMotion.matches || splashOn()) return;
  const detail = mode === 'detail';
  scrollTimer = setTimeout(() => {
    const d = DESIGNS[sel];
    const { mon, phone } = items[sel];
    startScroll(mon.querySelector('.sc-view'), d.dt, d.dtRatio, detail ? 1.4 : 0);
    startScroll(phone.querySelector('.sc-view'), d.mt, d.mtRatio, detail ? 1.4 : 0);
  }, detail ? 650 : 1000);
}

function setMode(next) {
  mode = next;
  root.dataset.mode = next;
  $('[data-sc-bar="shelf"]').hidden = next === 'detail';
  $('[data-sc-bar="detail"]').hidden = next !== 'detail';
  place();
  scheduleScroll();
  const d = DESIGNS[sel];
  if (next === 'detail') {
    $('.sc-live').textContent = `${d.nameKo}을 펼쳤습니다. 다른 디자인 보기, 홈페이지로 보기, 이게 좋겠어요 버튼이 있습니다.`;
    track('intro_open', { item: d.slug });
    $('[data-sc="how"]').focus({ preventScroll: true });
  } else {
    $('.sc-stage').focus({ preventScroll: true });
  }
}

/* ── 쇼케이스 앞 브랜드 인트로 (index.html .sc-splash) ──
   애니메이션은 첫 화면부터 CSS로 재생되고, 여기서는 끝나는 시점만 잡아 위로 걷어냄.
   화면을 누르거나 아무 키나 누르면 바로 쇼케이스로. 홈 중간의 '펼쳐 보기'로 다시 열 때는 건너뜀 */
const splash = root?.querySelector('[data-sc-splash]');
const splashOn = () => !!splash && html.classList.contains('intro-on') && !html.classList.contains('splash-off');
let splashTimer = 0;
function endSplash(method) {
  if (!splashOn() || splash.classList.contains('is-out')) return;
  clearTimeout(splashTimer);
  if (method) track('intro_splash_skip', { method });
  splash.classList.add('is-out');
  setTimeout(() => {
    html.classList.add('splash-off');
    splash.classList.remove('is-out');
    scheduleScroll();
    $('.sc-stage').focus({ preventScroll: true });
  }, reduceMotion.matches ? 200 : 900);
}
splash?.addEventListener('click', (e) => { e.stopPropagation(); endSplash('click'); });
root?.addEventListener('keydown', (e) => {
  if (!splashOn() || e.key === 'Tab') return;
  e.preventDefault();
  e.stopImmediatePropagation();
  endSplash('key');
}, true);
if (splashOn()) {
  // 글꼴이 준비돼 재생이 시작된 시점(index.html 게이트의 __splashT0)부터 약 5.2초(움직임 줄이기면 2.4초) 뒤에 걷음
  const arm = () => {
    const played = performance.now() - (window.__splashT0 ?? performance.now());
    splashTimer = setTimeout(endSplash, Math.max(300, (reduceMotion.matches ? 2400 : 5200) - played));
  };
  if (window.__splashT0 != null) arm(); else window.addEventListener('splash:start', arm, { once: true });
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
  requestAnimationFrame(() => (splashOn() ? splash : $('.sc-stage')).focus({ preventScroll: true }));
  const idle = window.requestIdleCallback || ((fn) => setTimeout(fn, 1200));
  idle(() => loadNear(N));
}

/* "이게 좋겠어요!" — 고른 디자인을 기억해 상담 신청서·결제·사전정보 시트에 미리 채움 (assets/js/pick.js) */
const PICK_KEY = 'noah_pick';
function rememberPick(d) {
  try { localStorage.setItem(PICK_KEY, JSON.stringify({ slug: d.slug, nameKo: d.nameKo, ts: Date.now() })); } catch (_) { return false; }
  track('select_item', { item_list_name: 'showcase', items: [{ item_id: d.slug, item_name: d.nameKo }] });
  return true;
}

/* 히어로로 넘어간 뒤 잠깐 보여주는 안내 — 무엇을 기억했는지 알리고 바로 취소할 수 있게 */
function pickToast(d) {
  document.querySelector('.sc-toast')?.remove();
  const t = document.createElement('div');
  t.className = 'sc-toast';
  t.setAttribute('role', 'status');
  t.innerHTML = '<span class="sc-toast-text"><strong></strong> 디자인을 기억해 둘게요. 상담 신청서에 미리 넣어 드립니다.</span>' +
    '<a class="sc-toast-go" href="/contact">상담 신청 →</a><button type="button" class="sc-toast-undo">취소</button>';
  t.querySelector('strong').textContent = d.nameKo;
  t.querySelector('.sc-toast-undo').addEventListener('click', () => {
    try { localStorage.removeItem(PICK_KEY); } catch (_) {}
    t.querySelector('.sc-toast-text').textContent = '기억한 디자인을 지웠어요.';
    t.querySelector('.sc-toast-go').remove();
    t.querySelector('.sc-toast-undo').remove();
    setTimeout(() => t.remove(), 1800);
  });
  document.body.appendChild(t);
  requestAnimationFrame(() => t.classList.add('is-on'));
  setTimeout(() => { t.classList.remove('is-on'); setTimeout(() => t.remove(), 400); }, 7000);
}

function exit(method) {
  if (leaving) return;
  leaving = true;
  clearTimeout(scrollTimer);
  try { sessionStorage.setItem(SEEN_KEY, '1'); } catch (_) {}
  const d = DESIGNS[sel];
  track('intro_exit', { method, item: d?.slug });
  const picked = method === 'how' && d && rememberPick(d);
  window.scrollTo(0, 0);
  const finish = () => {
    stopScroll();
    html.classList.remove('intro-on', 'intro-leaving');
    root.classList.remove('is-leaving');
    const h1 = document.querySelector('#hero h1');
    if (h1) { h1.setAttribute('tabindex', '-1'); h1.focus({ preventScroll: true }); }
    if (picked) pickToast(d);
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
    stopScroll();
    scheduleScroll();
  });
});

/* 홈 레퍼런스 구간의 "펼쳐 보기" */
document.querySelectorAll('[data-showcase-open]').forEach((el) => {
  el.addEventListener('click', () => { html.classList.add('splash-off'); window.scrollTo(0, 0); start(); });
});

if (root && html.classList.contains('intro-on')) start();
