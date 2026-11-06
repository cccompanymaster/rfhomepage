// 공통 도구 — 설정 읽기, 응답, 해시·서명, 금액 계산, 입력 검증
// 비밀 값(NICEPAY_SECRET_KEY)은 이 파일의 함수 안에서만 쓰고, 응답·로그로 내보내지 않는다.

export const ORDER_ID_RE = /^NO-\d{6}-[A-Z2-9]{10}$/;
export const TID_RE = /^[A-Za-z0-9_-]{1,40}$/;
export const PENDING_TTL = 2 * 60 * 60;      // 결제 대기 주문 2시간
export const KEEP_TTL = 90 * 24 * 60 * 60;   // 결제 결과(paid·check·cancelled) 90일

export function config(env) {
  const clientId = String(env.NICEPAY_CLIENT_ID || '').trim();
  const secretKey = String(env.NICEPAY_SECRET_KEY || '').trim();
  const apiBase = String(env.NICEPAY_API_BASE || 'https://sandbox-api.nicepay.co.kr').trim().replace(/\/+$/, '');
  return {
    live: Boolean(clientId && secretKey && env.ORDERS),
    clientId,
    secretKey,
    apiBase,
    sandbox: apiBase.includes('sandbox'),
    method: String(env.NICEPAY_METHOD || 'cardAndEasyPay').trim(),
    timeoutMs: Number(env.NICEPAY_TIMEOUT_MS) > 0 ? Number(env.NICEPAY_TIMEOUT_MS) : 30000,
    gasUrl: String(env.GAS_URL || '').trim(),
    webhookIps: String(env.NICEPAY_WEBHOOK_IPS || '').split(',').map((s) => s.trim()).filter(Boolean),
    retryAfterMs: Number(env.RECORD_RETRY_AFTER_MS) > 0 ? Number(env.RECORD_RETRY_AFTER_MS) : 120000,
  };
}

// 운영 주소에서 샌드박스 키로 결제창이 열리면 손님이 "결제 완료"를 보고도 실제로는 결제되지 않는다.
// 그래서 샌드박스 키일 때 운영 주소에서는 테스트 표시(?paytest=1)가 있는 요청만 결제를 켠다.
const PROD_HOSTS = ['noahhomepage.co.kr', 'www.noahhomepage.co.kr'];
export function paymentMode(c, url, testFlag) {
  if (!c.live) return 'demo';
  if (c.sandbox && PROD_HOSTS.includes(url.hostname) && !testFlag) return 'demo';
  return 'live';
}

/* ── 응답 ── */
const BASE_HEADERS = {
  'Cache-Control': 'no-store',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'X-Frame-Options': 'DENY',
};
export function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { ...BASE_HEADERS, 'Content-Type': 'application/json; charset=utf-8' } });
}
export function text(body, status = 200, type = 'text/plain; charset=utf-8') {
  return new Response(body, { status, headers: { ...BASE_HEADERS, 'Content-Type': type } });
}
export function redirect(location) {
  return new Response(null, { status: 303, headers: { ...BASE_HEADERS, Location: location } });
}

/* ── 해시·서명 ── */
export async function sha256Hex(s) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
}
// 길이가 같으면 끝까지 비교 (타이밍 차이 최소화)
export function safeEqual(a, b) {
  a = String(a || '').toLowerCase();
  b = String(b || '').toLowerCase();
  if (!a || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

/* ── 표시 ── */
export const won = (n) => '₩' + String(Math.trunc(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ',');

export function newOrderId(now = new Date()) {
  const kst = new Date(now.getTime() + 9 * 3600 * 1000);
  const ymd = kst.toISOString().slice(2, 10).replace(/-/g, '');
  const abc = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';           // 헷갈리는 0·O·1·I 제외 (32자)
  const rnd = crypto.getRandomValues(new Uint8Array(10));
  return `NO-${ymd}-${[...rnd].map((b) => abc[b & 31]).join('')}`;
}

/* ── 금액 계산: 브라우저가 보낸 것은 옵션 키·수량만 믿는다 ── */
export function priceItems(catalog, items) {
  if (!Array.isArray(items) || items.length > 30) return { error: 'items' };
  const opts = new Map(catalog.options.map((o) => [o.key, o]));
  const want = new Map();
  for (const it of items) {
    if (!it || typeof it !== 'object' || typeof it.key !== 'string') return { error: 'items' };
    const qty = it.qty === undefined ? 1 : it.qty;
    if (it.key === catalog.base.key) {                       // 기본 패키지는 항상 1개 포함
      if (qty !== 1) return { error: 'items' };
      continue;
    }
    const o = opts.get(it.key);
    if (!o || want.has(it.key)) return { error: 'items' };
    if (!Number.isInteger(qty) || qty < 1 || qty > (o.maxQty || 1)) return { error: 'items' };
    want.set(it.key, qty);
  }
  const b = catalog.base;
  const lines = [{ key: b.key, name: b.name, qty: 1, price: b.price }];
  for (const o of catalog.options) {                          // 단가표 순서로 정렬
    if (!want.has(o.key)) continue;
    const qty = want.get(o.key);
    lines.push({ key: o.key, name: qty > 1 ? `${o.name} ×${qty}` : o.name, qty, price: o.price * qty });
  }
  const supply = lines.reduce((a, l) => a + l.price, 0);
  const vat = Math.round(supply * catalog.vatRate);
  const extra = lines.length - 1;
  return {
    lines,
    supply,
    vat,
    total: supply + vat,
    itemText: lines.map((l) => l.name).join(' + '),
    goodsName: (b.name + (extra ? ` 외 ${extra}건` : '')).slice(0, 40),
  };
}

/* ── 주문자 입력 검증 ── */
const clean = (v, max) => String(v ?? '').replace(/[\u0000-\u0009\u000B-\u001F\u007F]/g, '').trim().slice(0, max + 1);
export function validateBuyer(body) {
  const name = clean(body.name, 30).replace(/\n/g, ' ');
  const phone = clean(body.phone, 13);
  const email = clean(body.email, 100);
  const biz = clean(body.biz, 60).replace(/\n/g, ' ');
  const memo = clean(body.memo, 500);
  const reference = clean(body.reference, 60).replace(/\n/g, ' ');
  const receipt = ['none', 'cash', 'tax'].includes(body.receipt) ? body.receipt : null;
  const bizno = clean(body.bizno, 12);

  if (!name || name.length > 30) return { error: 'name', message: '성함을 확인해 주세요.' };
  const pd = phone.replace(/-/g, '');
  if (!/^01[016789]\d{7,8}$/.test(pd) || !/^[\d-]+$/.test(phone)) return { error: 'phone', message: '휴대폰 번호를 확인해 주세요.' };
  if (email.length > 100 || !/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(email)) return { error: 'email', message: '이메일 주소를 확인해 주세요.' };
  if (biz.length > 60) return { error: 'biz', message: '상호는 60자 이내로 입력해 주세요.' };
  if (memo.length > 500) return { error: 'memo', message: '요청 메모는 500자 이내로 입력해 주세요.' };
  if (!receipt) return { error: 'receipt', message: '영수증 종류를 확인해 주세요.' };
  if (receipt === 'tax' && !/^\d{3}-\d{2}-\d{5}$/.test(bizno)) return { error: 'bizno', message: '사업자등록번호 10자리를 확인해 주세요.' };

  const phoneFmt = pd.length === 11 ? `${pd.slice(0, 3)}-${pd.slice(3, 7)}-${pd.slice(7)}` : `${pd.slice(0, 3)}-${pd.slice(3, 6)}-${pd.slice(6)}`;
  return { buyer: { name, phone: phoneFmt, email, biz, memo, reference, receipt, bizno: receipt === 'tax' ? bizno : '' } };
}

// UTF-8 바이트 기준 자르기 (나이스페이 필드 길이는 byte 단위)
export function byteCut(s, max) {
  let out = '';
  let n = 0;
  for (const ch of String(s || '')) {
    const b = new TextEncoder().encode(ch).length;
    if (n + b > max) break;
    out += ch;
    n += b;
  }
  return out;
}

export async function readJson(request, maxBytes = 16384) {
  const len = Number(request.headers.get('Content-Length') || 0);
  if (len > maxBytes) return null;
  const t = await request.text();
  if (t.length > maxBytes) return null;
  try {
    const d = JSON.parse(t);
    return d && typeof d === 'object' && !Array.isArray(d) ? d : null;
  } catch {
    return null;
  }
}
