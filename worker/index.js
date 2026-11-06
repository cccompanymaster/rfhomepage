// NOAH 결제 서버 (Cloudflare Worker)
// wrangler.toml 의 run_worker_first = ["/api/*"] 때문에 /api/* 만 여기로 온다.
// 그 밖의 요청은 정적 파일이 바로 응답(_headers·_redirects 그대로 적용). 혹시 여기로 오면 정적 파일로 넘긴다.
import { json } from './lib.js';
import { getConfig, createOrder, orderStatus, handleReturn, handleWebhook } from './payments.js';

const STATUS_RE = /^\/api\/order\/([^/]+)\/status$/;

async function route(request, env, ctx, url) {
  const p = url.pathname;
  const m = request.method;
  if (p === '/api/config' && m === 'GET') return getConfig(env);
  if (p === '/api/order' && m === 'POST') return createOrder(request, env);
  if (p === '/api/nicepay/return' && m === 'POST') return handleReturn(request, env, ctx);
  if (p === '/api/nicepay/webhook' && m === 'POST') return handleWebhook(request, env, ctx);
  const s = p.match(STATUS_RE);
  if (s && m === 'GET') return orderStatus(env, decodeURIComponent(s[1]));
  // 결제창에서 GET으로 돌아오는 경우(뒤로가기 등) — 결제 페이지로
  if (p === '/api/nicepay/return' && m === 'GET') return Response.redirect(new URL('/checkout', url).href, 303);
  return json({ ok: false, error: 'not_found' }, 404);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith('/api/')) return env.ASSETS.fetch(request);
    try {
      return await route(request, env, ctx, url);
    } catch (err) {
      console.log(JSON.stringify({ ev: 'api_error', path: url.pathname, name: err && err.name }));
      if (url.pathname === '/api/nicepay/return') return Response.redirect(new URL('/checkout?pay=fail&reason=error', url).href, 303);
      return json({ ok: false, error: 'server', message: '일시적인 오류입니다. 잠시 후 다시 시도해 주세요.' }, 500);
    }
  },
};
