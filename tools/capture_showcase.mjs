// 홈 첫 화면 쇼케이스용 템플릿 화면 캡처
//
//   python3 -m http.server 8799 &          # 저장소 루트에서
//   node tools/capture_showcase.mjs        # → content/showcase/screens/*.png
//   python3 tools/build_showcase.py        # → assets/showcase/*.webp
//
// 찍는 것 (템플릿마다 4장)
//   <slug>-desktop.png       1440×900  — 모니터 목업 첫 화면
//   <slug>-desktop-tall.png  1440×2700 — 펼쳤을 때 모니터 안에서 스크롤되는 화면
//   <slug>-mobile.png        390×844 @2x — 휴대폰 목업 첫 화면
//   <slug>-mobile-tall.png   390×2532 @2x — 펼쳤을 때 휴대폰 안에서 스크롤되는 화면
//
// 쇼룸 복귀 버튼·하단 예약 바·측면 플로팅 버튼처럼 화면에 떠 있는 요소는 숨기고,
// 맨 위 사이트 헤더만 남깁니다. 스크롤 등장 애니메이션은 모두 보이는 상태로 고정합니다.
//
// Playwright 필요: npm i -D playwright  (Chromium 경로는 PW_CHROMIUM 으로 지정 가능)
import { chromium } from 'playwright';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BASE = process.env.BASE_URL || 'http://localhost:8799';
const OUT = path.join(ROOT, 'content/showcase/screens');
const only = process.argv.slice(2);
const { designs } = JSON.parse(readFileSync(path.join(ROOT, 'content/showcase/designs.json'), 'utf8'));

const browser = await chromium.launch(process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {});

async function prepare(page) {
  // 지연 로딩 이미지·등장 애니메이션이 모두 켜지도록 끝까지 한 번 훑고 맨 위로
  await page.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += innerHeight * 0.8) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 90)); }
    scrollTo(0, 0);
  });
  await page.evaluate(() => {
    document.querySelectorAll('.reveal,[data-reveal],.rv,.fade-up,.fade-in').forEach((e) => e.classList.add('is-visible', 'on', 'revealed', 'in', 'visible', 'show', 'active'));
    document.querySelectorAll('.fab-back').forEach((e) => e.remove());
    for (const el of document.querySelectorAll('body *')) {
      const cs = getComputedStyle(el);
      if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
      const r = el.getBoundingClientRect();
      const isTopBar = r.top < 90 && r.bottom < 170 && r.width > 300;
      if (!isTopBar) el.style.setProperty('display', 'none', 'important');
    }
  });
  await page.waitForTimeout(1500);
}

for (const d of designs) {
  if (only.length && !only.includes(d.slug)) continue;
  for (const v of [
    { name: 'desktop', vw: 1440, vh: 900, dpr: 1, tall: 2700, mobile: false },
    { name: 'mobile', vw: 390, vh: 844, dpr: 2, tall: 2532, mobile: true },
  ]) {
    const ctx = await browser.newContext({ viewport: { width: v.vw, height: v.vh }, deviceScaleFactor: v.dpr, isMobile: v.mobile, hasTouch: v.mobile });
    await ctx.route(/googletagmanager|google-analytics|ipify/, (r) => r.fulfill({ body: '{}' }));
    const page = await ctx.newPage();
    await page.goto(`${BASE}/templates/${d.slug}.html`, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
    await prepare(page);
    await page.screenshot({ path: path.join(OUT, `${d.slug}-${v.name}.png`) });
    const h = await page.evaluate(() => document.documentElement.scrollHeight);
    await page.screenshot({ path: path.join(OUT, `${d.slug}-${v.name}-tall.png`), fullPage: true, clip: { x: 0, y: 0, width: v.vw, height: Math.min(v.tall, h) } });
    console.log('✓', d.slug, v.name);
    await ctx.close();
  }
}
await browser.close();
