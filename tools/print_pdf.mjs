// HTML → PDF (Chromium 인쇄). tools/build_brochure.py 가 부릅니다.
//   node tools/print_pdf.mjs <입력.html> <출력.pdf>
// 페이지 크기는 HTML의 @page(1280×720)를 따릅니다. 글꼴이 다 내려온 뒤 인쇄합니다.
import { chromium } from 'playwright';
import path from 'node:path';

const [, , src, out] = process.argv;
if (!src || !out) { console.error('사용법: node tools/print_pdf.mjs <입력.html> <출력.pdf>'); process.exit(2); }
import { existsSync } from 'node:fs';
// Playwright가 기대하는 브라우저 버전이 없으면, 이미 깔린 Chromium을 찾아 씀 (PW_CHROMIUM 으로 직접 지정 가능)
const KNOWN = [process.env.PW_CHROMIUM, '/opt/pw-browsers/chromium/chrome-linux64/chrome', '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'].filter(Boolean);
let browser;
try { browser = await chromium.launch(process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {}); }
catch (e) {
  const exe = KNOWN.find((p) => existsSync(p));
  if (!exe) throw e;
  browser = await chromium.launch({ executablePath: exe });
}
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
await page.goto('file://' + path.resolve(src), { waitUntil: 'networkidle' });
await page.evaluate(async () => { await document.fonts.ready; });
await page.pdf({ path: out, printBackground: true, preferCSSPageSize: true });
await browser.close();
console.log('✓ PDF', out);
