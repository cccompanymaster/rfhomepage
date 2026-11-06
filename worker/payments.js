// 결제 흐름: 주문 생성 → (결제창) → returnUrl 검증·승인 → 완료 페이지 / 웹훅 동기화
import catalog from '../assets/data/catalog.json';
import { ORDER_ID_RE, TID_RE, PENDING_TTL, KEEP_TTL, config, json, text, redirect, won, newOrderId, priceItems, validateBuyer, readJson } from './lib.js';
import { approve, getPayment, netCancel, checkAuthSignature, checkResultSignature, isVerifiedPaid, UnknownOutcome } from './nicepay.js';

const key = (orderId) => `order:${orderId}`;
const log = (ev, data) => console.log(JSON.stringify({ ev, ...data }));   // 개인정보·키는 넣지 않는다

async function getOrder(env, orderId) {
  if (!env.ORDERS || !ORDER_ID_RE.test(orderId)) return null;
  return env.ORDERS.get(key(orderId), 'json');
}
function putOrder(env, order, ttl) {
  return env.ORDERS.put(key(order.orderId), JSON.stringify(order), { expirationTtl: ttl });
}

/* ════════ GET /api/config — 결제 켜짐 여부만 (키 값은 내보내지 않음) ════════ */
export function getConfig(env) {
  return json({ mode: config(env).live ? 'live' : 'demo' });
}

/* ════════ POST /api/order ════════ */
export async function createOrder(request, env) {
  const c = config(env);
  const url = new URL(request.url);
  const origin = request.headers.get('Origin');
  const site = request.headers.get('Sec-Fetch-Site');
  if ((origin && origin !== url.origin) || (site && site !== 'same-origin')) return json({ ok: false, error: 'origin' }, 403);

  const body = await readJson(request);
  if (!body) return json({ ok: false, error: 'bad_request', message: '요청 형식이 올바르지 않습니다.' }, 400);
  if (body.website) return json({ ok: false, error: 'rejected' }, 400);                 // 봇 허니팟

  const priced = priceItems(catalog, body.items);
  if (priced.error) return json({ ok: false, error: 'items', message: '선택한 옵션을 확인해 주세요. 새로고침 후 다시 시도해 주세요.' }, 400);
  const v = validateBuyer(body);
  if (v.error) return json({ ok: false, error: v.error, message: v.message }, 400);

  if (!c.live) return json({ ok: true, mode: 'demo', amount: priced.total });

  const order = {
    v: 1,
    orderId: newOrderId(),
    status: 'pending',
    amount: priced.total,
    supply: priced.supply,
    vat: priced.vat,
    lines: priced.lines,
    itemText: priced.itemText,
    goodsName: priced.goodsName,
    buyer: v.buyer,
    sandbox: c.sandbox,
    createdAt: new Date().toISOString(),
  };
  await putOrder(env, order, PENDING_TTL);
  log('order_created', { orderId: order.orderId, amount: order.amount });
  return json({
    ok: true,
    mode: 'live',
    orderId: order.orderId,
    amount: order.amount,
    goodsName: order.goodsName,
    clientId: c.clientId,
    method: c.method,
  });
}

/* ════════ GET /api/order/{orderId}/status — 개인정보 없이 상태만 ════════ */
export async function orderStatus(env, orderId) {
  const order = await getOrder(env, orderId);
  if (!order) return json({ status: 'not_found' }, 404);
  return json({
    orderId: order.orderId,
    status: order.status,
    amount: order.amount,
    itemText: order.itemText,
    items: order.lines.map(({ key, name, qty, price }) => ({ key, name, qty, price })),
  });
}

/* ════════ POST /api/nicepay/return — 결제창 인증 결과 (브라우저 form POST) ════════ */
export async function handleReturn(request, env, ctx) {
  const c = config(env);
  const fail = (reason, code) => redirect(`/checkout?pay=fail&reason=${reason}${code && /^[A-Z0-9]{4}$/i.test(code) ? '&code=' + code : ''}`);
  const done = (orderId) => redirect(`/checkout/complete?o=${orderId}`);

  let form;
  try {
    form = await request.formData();
  } catch {
    return fail('verify');
  }
  const f = Object.fromEntries(['authResultCode', 'authResultMsg', 'tid', 'clientId', 'orderId', 'amount', 'authToken', 'signature'].map((k) => [k, String(form.get(k) ?? '')]));

  if (!c.live) return fail('config');
  const order = await getOrder(env, f.orderId);
  if (!order) return fail('expired');
  if (order.status !== 'pending') return done(order.orderId);          // 이미 처리됨 — 새로고침·재전송에도 승인 다시 안 함

  if (f.authResultCode !== '0000') {
    log('auth_failed', { orderId: order.orderId, code: f.authResultCode });
    return fail('auth', f.authResultCode);
  }

  // 금액·주문번호·가맹점·서명을 모두 확인한 뒤에만 승인 API 호출
  const verified =
    f.clientId === c.clientId &&
    /^\d+$/.test(f.amount) &&
    Number(f.amount) === order.amount &&
    f.orderId === order.orderId &&
    TID_RE.test(f.tid) &&
    Boolean(f.authToken) &&
    (await checkAuthSignature(c, f));
  if (!verified) {
    log('return_rejected', { orderId: order.orderId });
    return fail('verify');
  }

  let d;
  try {
    d = await approve(c, f.tid, order.amount);
  } catch (err) {
    if (!(err instanceof UnknownOutcome)) throw err;
    // 승인 결과를 모름 → 망취소 (1시간 안에만 가능하므로 즉시)
    const nc = await netCancel(c, order.orderId);
    log('approve_unknown', { orderId: order.orderId, reason: err.message, netcancel: nc });
    order.status = 'check';
    order.tid = f.tid;
    order.note = `승인 응답 없음(${err.message}) → 망취소 요청 결과: ${nc === '0000' ? '성공' : nc}`;
    order.markedAt = new Date().toISOString();
    await putOrder(env, order, KEEP_TTL);
    ctx.waitUntil(recordToSheet(env, c, order, request));
    return fail('timeout');
  }

  if (await isVerifiedPaid(c, d, order, f.tid)) return markPaid(env, c, ctx, order, d, request);

  if (d && d.resultCode === '0000') {
    // 성공 코드인데 금액·서명이 맞지 않음 — 결제됐을 수 있으므로 사장님 확인 필요
    log('approve_mismatch', { orderId: order.orderId });
    order.status = 'check';
    order.tid = f.tid;
    order.note = '승인 응답의 금액 또는 서명이 주문과 다름 — 나이스페이 관리자에서 확인 필요';
    order.markedAt = new Date().toISOString();
    await putOrder(env, order, KEEP_TTL);
    ctx.waitUntil(recordToSheet(env, c, order, request));
    return done(order.orderId);
  }

  // 승인 실패 — 같은 tid가 먼저 승인된 경우(동시 재전송)만 조회로 확인해 완료 처리
  log('approve_failed', { orderId: order.orderId, code: d && d.resultCode });
  try {
    const q = await getPayment(c, f.tid);
    if (await isVerifiedPaid(c, q, order, f.tid)) {
      const again = await getOrder(env, order.orderId);
      if (again && again.status !== 'pending') return done(order.orderId);
      return markPaid(env, c, ctx, order, q, request);
    }
  } catch {
    /* 조회 실패 — 승인 실패로 안내 */
  }
  return fail('approve', d && d.resultCode);
}

// 승인 확인된 주문을 paid로 저장 (이름·연락처는 시트 기록이 끝날 때까지만 보관)
async function savePaid(env, order, d) {
  order.status = 'paid';
  order.tid = d.tid;
  order.paidAt = d.paidAt || new Date().toISOString();
  order.payMethod = d.payMethod || '';
  order.cardName = (d.card && d.card.cardName) || '';
  order.approveNo = d.approveNo || '';
  order.receiptUrl = d.receiptUrl || '';
  order.recorded = false;
  order.markedAt = new Date().toISOString();
  await putOrder(env, order, KEEP_TTL);
  log('paid', { orderId: order.orderId, amount: order.amount });
}
async function markPaid(env, c, ctx, order, d, request) {
  await savePaid(env, order, d);
  ctx.waitUntil(recordToSheet(env, c, order, request));
  return redirect(`/checkout/complete?o=${order.orderId}`);
}

/* ── Apps Script(handleConsult)로 기록 → 성공하면 KV에서 이름·연락처·이메일 삭제 ── */
// handleConsult는 이름·연락처·이메일·업종·관심 디자인·메시지만 시트에 적으므로 상태·tid는 업종·메시지 글자에 넣는다.
function sheetPayload(c, order, request) {
  const b = order.buyer || {};
  const tag = order.sandbox ? '[샌드박스 테스트] ' : '';
  const rc = { none: '필요 없음', cash: '현금영수증', tax: `세금계산서 (${b.bizno})` }[b.receipt] || '필요 없음';
  const head =
    order.status === 'paid'
      ? `${tag}[NOAH 결제 완료] ${order.orderId}`
      : `${tag}[NOAH 결제 확인 필요] ${order.orderId}`;
  const pay =
    order.status === 'paid'
      ? `결제: ${[order.payMethod, order.cardName].filter(Boolean).join(' · ') || '카드·간편결제'}${order.approveNo ? ` · 승인번호 ${order.approveNo}` : ''} · tid ${order.tid}`
      : `확인 필요: ${order.note || ''} · tid ${order.tid || '-'}\n나이스페이 가맹점 관리자에서 주문번호로 결제 여부를 확인해 주세요.`;
  const message = [
    head,
    `주문 내역: ${order.itemText}`,
    `공급가액 ${won(order.supply)} + 부가세 ${won(order.vat)} = 총 ${won(order.amount)}`,
    pay,
    order.receiptUrl ? `매출전표: ${order.receiptUrl}` : null,
    `성함: ${b.name} / 연락처: ${b.phone} / 이메일: ${b.email}`,
    b.biz ? `상호: ${b.biz}` : null,
    `영수증: ${rc}`,
    b.memo ? `메모: ${b.memo}` : null,
  ]
    .filter(Boolean)
    .join('\n');
  return {
    type: 'consult',
    kind: 'order',
    sendBrochure: false,
    orderId: order.orderId,
    status: order.status,
    tid: order.tid || '',
    name: b.name,
    phone: b.phone,
    email: b.email,
    industry: `${tag}${order.status === 'paid' ? '카드결제 완료' : '결제 확인 필요'} · 총 ${won(order.amount)}`,
    reference: b.reference || '',
    message,
    total: order.amount,
    receipt: b.receipt,
    bizno: b.bizno,
    timestamp: new Date().toISOString(),
    referrer: '나이스페이 결제 서버',
    page: new URL('/checkout', request.url).href,
  };
}

async function postSheet(c, payload) {
  if (!c.gasUrl) return false;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 20000);
  try {
    const r = await fetch(c.gasUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(payload),
      redirect: 'follow',
      signal: ctrl.signal,
    });
    const t = await r.text();
    return JSON.parse(t).ok === true;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

async function recordToSheet(env, c, order, request) {
  const payload = sheetPayload(c, order, request);
  let ok = await postSheet(c, payload);
  if (!ok) {
    await new Promise((r) => setTimeout(r, 3000));
    ok = await postSheet(c, payload);
  }
  if (!ok) {
    log('sheet_failed', { orderId: order.orderId, status: order.status });
    return;
  }
  // 최신 상태를 다시 읽어 덮어쓰기 (그 사이 웹훅이 상태를 바꿨을 수 있음)
  const latest = (await getOrder(env, order.orderId)) || order;
  latest.recorded = true;
  delete latest.buyer;
  await putOrder(env, latest, KEEP_TTL);
  log('sheet_recorded', { orderId: order.orderId, status: latest.status });
}

/* ════════ POST /api/nicepay/webhook — 나이스페이 → 서버 ════════ */
const OK = () => text('OK', 200, 'text/html;charset=utf-8');

export async function handleWebhook(request, env, ctx) {
  const c = config(env);
  if (c.webhookIps.length && !c.webhookIps.includes(request.headers.get('CF-Connecting-IP') || '')) {
    log('webhook_ip_rejected', {});
    return text('forbidden', 403);
  }
  const d = await readJson(request, 65536);
  if (!d) return text('bad request', 400);
  if (!c.live) return OK();                                  // 결제 꺼짐 — 처리할 주문 없음
  const order = typeof d.orderId === 'string' ? await getOrder(env, d.orderId) : null;
  if (!order) return OK();                                   // 모르는 주문 — 무시

  const valid = Number(d.amount) === order.amount && (!order.tid || d.tid === order.tid) && (await checkResultSignature(c, d));
  if (!valid) {
    log('webhook_rejected', { orderId: order.orderId });
    return text('invalid signature', 400);
  }
  log('webhook', { orderId: order.orderId, status: d.status, current: order.status });

  if (d.status === 'paid' && d.resultCode === '0000') {
    if (order.status === 'pending') {
      // 보통은 returnUrl 처리가 곧 paid로 바꾼다. 잠시 기다렸다가 그래도 대기면 웹훅 기준으로 완료 처리.
      ctx.waitUntil(
        (async () => {
          await new Promise((r) => setTimeout(r, 8000));
          const again = await getOrder(env, order.orderId);
          if (again && again.status === 'pending' && (await isVerifiedPaid(c, d, again))) {
            await savePaid(env, again, d);
            await recordToSheet(env, c, again, request);
          }
        })(),
      );
    } else if (order.status === 'paid' && !order.recorded && Date.now() - Date.parse(order.markedAt || 0) > 60000) {
      ctx.waitUntil(recordToSheet(env, c, order, request));  // 시트 기록이 실패했던 주문 — 웹훅 재전송 때 다시 시도
    }
  } else if ((d.status === 'cancelled' || d.status === 'partialCancelled') && order.status !== d.status) {
    order.status = d.status;
    order.cancelledAt = d.cancelledAt || new Date().toISOString();
    await putOrder(env, order, KEEP_TTL);
  }
  return OK();
}

