const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const SITE = process.env.SD + '/site/templates';
const OUT  = process.env.SD + '/raw';
fs.mkdirSync(OUT, { recursive: true });

const SHOTS = [
  { key: 'desktop', w: 1440, h: 900 },
  { key: 'mobile',  w: 390,  h: 844 },
];

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--font-render-hinting=none'],
    proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined,
  });

  const files = fs.readdirSync(SITE).filter(f => f.endsWith('.html')).sort();
  for (const f of files) {
    const name = f.replace('.html', '');
    for (const s of SHOTS) {
      const ctx = await browser.newContext({
        viewport: { width: s.w, height: s.h },
        deviceScaleFactor: 2,
        ignoreHTTPSErrors: true,
        locale: 'ko-KR',
      });
      const page = await ctx.newPage();
      try {
        await page.goto('file://' + path.join(SITE, f), { waitUntil: 'load', timeout: 30000 });
        // 등장 애니메이션 강제 완료 + 모션 정지
        await page.addStyleTag({ content: `
          *,*::before,*::after{animation:none !important;transition:none !important}
          .reveal,.up{opacity:1 !important;transform:none !important}
        `});
        await page.evaluate(() => {
          document.querySelectorAll('.reveal,.up').forEach(e => e.classList.add('in'));
          document.querySelectorAll('[data-count]').forEach(e => {
            const t = +e.dataset.count; if (!isNaN(t)) e.textContent = t.toLocaleString('ko-KR');
          });
          window.scrollTo(0, 0);
        });
        await page.waitForTimeout(1200);
        await page.screenshot({ path: `${OUT}/${name}-${s.key}.png` });
        process.stdout.write(`✓ ${name}-${s.key}\n`);
      } catch (e) {
        process.stdout.write(`✗ ${name}-${s.key}: ${String(e).slice(0, 90)}\n`);
      }
      await ctx.close();
    }
  }
  await browser.close();
})();
