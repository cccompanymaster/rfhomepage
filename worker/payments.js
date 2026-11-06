// 결제 흐름: 주문 생성 → (결제창) → returnUrl 검증·승인 → 완료 페이지 / 웹훅 동기화 / 기록 재시도(크론)
import catalog from '../assets/data/catalog.json';
import { ORDER_ID_RE, TID_RE, PENDING_TTL, KEEP_TTL, config, paymentMode, json, text, redirect, won, newOrderId, priceItems, validateBuyer, readJson } from './lib.js';
import { approve, getPayment, netCancel, checkAuthSignature, checkResultSignature, isVerifiedPaid, UnknownOutcome } from './nicepay.js';

const key = (orderId) => `order:${orderId}`;
const log = (ev, data) => console.log(JSON.stringify({ ev, ...data }));   // 개인정보·키는 넣지 않는다
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getOrder(env, orderId) {
  if (!env.ORDERS || !ORDER_ID_RE.test(orderId)) return null;
  return env.ORDERS.get(key(orderId), 'json');
}
// metadata는 크론이 목록만 보고 "기록 안 된 주문"을 찾는 데 쓴다 (값을 읽지 않아도 됨)
function putOrder(env, order, ttl) {
  return env.ORDERS.put(key(order.orderId), JSON.stringify(order), {
    expirationTtl: ttl,
    metadata: { s: order.status, r: order.recorded ? 1 : 0, m: Date.parse(order.markedAt || order.createdAt) || 0 },
  });
}

/* ════════ GET /api/config — 결제 켜짐 여부만 (키 값은 내보내지 않음) ════════ */
export function getConfig(request, env) {
  const c = config(env);
  const url = new URL(request.url);
  const mode = paymentMode(c, url, url.searchParams.get('test') === '1');
  return json({ mode, sandbox: mode === 'live' && c.sandbox });
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

  if (paymentMode(c, url, body.test === true) !== 'live') return json({ ok: true, mode: 'demo', amount: priced.total });

  // 같은 IP의 연속 주문 제한 (KV 쓰기 한도 보호). 바인딩이 없으면 건너뜀.
  if (env.ORDER_LIMIT && env.ORDER_LIMIT_OFF !== '1') {
    const { success } = await env.ORDER_LIMIT.limit({ key: request.headers.get('CF-Connecting-IP') || 'unknown' });
    if (!success) return json({ ok: false, error: 'rate', message: '주문 요청이 너무 잦습니다. 1분 뒤 다시 시도해 주세요.' }, 429);
  }

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
    origin: url.origin,
    createdAt: new Date().toISOString(),
  };
  await putOrder(env, order, PENDING_TTL);
  log('order_created', { orderId: order.orderId, amount: order.amount });
  return json({
    ok: true,
    mode: 'live',
    sandbox: c.sandbox,
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
    sandbox: Boolean(order.sandbox),
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
    return approveUnknown(env, c, ctx, order, f.tid, err.message);
  }

  // ── 여기부터는 승인 API가 응답한 뒤. 어떤 오류가 나도 "다시 결제" 화면으로 보내지 않는다. ──
  try {
    if (await isVerifiedPaid(c, d, order, f.tid)) return await markPaid(env, c, ctx, order, d);

    if (d && d.resultCode === '0000') {
      // 성공 코드인데 금액·서명이 맞지 않음 — 결제됐을 수 있으므로 사장님 확인 필요
      log('approve_mismatch', { orderId: order.orderId });
      return await markCheck(env, c, ctx, order, f.tid, '승인 응답의 금액 또는 서명이 주문과 다름 — 나이스페이 관리자에서 확인 필요');
    }

    // 승인 실패 — 같은 tid가 먼저 승인된 경우(동시 재전송)만 조회로 확인해 완료 처리
    log('approve_failed', { orderId: order.orderId, code: d && d.resultCode });
    let q = null;
    try {
      q = await getPayment(c, f.tid);
    } catch {
      /* 조회 실패 — 승인 실패로 안내 */
    }
    if (q && (await isVerifiedPaid(c, q, order, f.tid))) {
      const again = await getOrder(env, order.orderId);
      if (again && again.status !== 'pending') return done(order.orderId);
      return await markPaid(env, c, ctx, order, q);
    }
    return fail('approve', d && d.resultCode);
  } catch (err) {
    // 승인 뒤 저장 등에서 오류 — 결제는 됐을 수 있다. 사장님께 바로 알리고 완료 페이지(확인 중 안내)로.
    log('after_approve_error', { orderId: order.orderId, name: err && err.name });
    order.status = 'check';
    order.tid = f.tid;
    order.note = `승인 응답 뒤 서버 오류(${(err && err.name) || 'error'}) — 승인 여부를 나이스페이 관리자에서 확인 필요`;
    order.markedAt = new Date().toISOString();
    await postSheet(c, sheetPayload(order)).catch(() => false);
    return done(order.orderId);
  }
}

// 승인 결과를 모름(타임아웃·네트워크) → 망취소. 망취소가 확인되지 않으면 손님을 "다시 결제" 화면으로 보내지 않는다.
async function approveUnknown(env, c, ctx, order, tid, reason) {
  const nc = await netCancel(c, order.orderId);
  log('approve_unknown', { orderId: order.orderId, reason, netcancel: nc });
  order.status = 'check';
  order.tid = tid;
  order.note = `승인 응답 없음(${reason}) → 망취소 요청 결과: ${nc === '0000' ? '성공 (청구되지 않음)' : '확인 안 됨 ' + nc}`;
  order.markedAt = new Date().toISOString();
  await putOrder(env, order, KEEP_TTL).catch(() => {});
  ctx.waitUntil(
    (async () => {
      if (nc !== '0000') {
        await sleep(5000);
        const nc2 = await netCancel(c, order.orderId);              // 망취소는 1시간 안에만 가능 — 한 번 더
        order.note += ` / 재시도: ${nc2 === '0000' ? '성공 (청구되지 않음)' : '실패 ' + nc2}`;
        log('netcancel_retry', { orderId: order.orderId, netcancel: nc2 });
      }
      await recordToSheet(env, c, order);
    })(),
  );
  return nc === '0000'
    ? redirect('/checkout?pay=fail&reason=timeout')
    : redirect(`/checkout/complete?o=${order.orderId}`);           // 완료 페이지가 "확인 필요" 안내
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
async function markPaid(env, c, ctx, order, d) {
  await savePaid(env, order, d);
  ctx.waitUntil(recordToSheet(env, c, order));
  return redirect(`/checkout/complete?o=${order.orderId}`);
}
async function markCheck(env, c, ctx, order, tid, note) {
  order.status = 'check';
  order.tid = tid;
  order.note = note;
  order.markedAt = new Date().toISOString();
  await putOrder(env, order, KEEP_TTL);
  ctx.waitUntil(recordToSheet(env, c, order));
  return redirect(`/checkout/complete?o=${order.orderId}`);
}

/* ── Apps Script(handleConsult)로 기록 → 성공하면 KV에서 이름·연락처·이메일 삭제 ── */
// handleConsult는 이름·연락처·이메일·업종·관심 디자인·메시지만 시트에 적으므로 상태·tid는 업종·메시지 글자에 넣는다.
// Apps Script 주소는 공개돼 있어 누구나 비슷한 메일을 보낼 수 있다 → 메시지에 진위 확인 링크를 넣는다.
function sheetPayload(order) {
  const b = order.buyer || {};
  const tag = order.sandbox ? '[샌드박스 테스트] ' : '';
  const paid = order.status === 'paid';
  const rc = { none: '필요 없음', cash: '현금영수증', tax: `세금계산서 (${b.bizno})` }[b.receipt] || '필요 없음';
  const site = order.origin || 'https://noahhomepage.co.kr';
  const pay = paid
    ? `결제: ${[order.payMethod, order.cardName].filter(Boolean).join(' · ') || '카드·간편결제'}${order.approveNo ? ` · 승인번호 ${order.approveNo}` : ''} · tid ${order.tid}`
    : `확인 필요: ${order.note || ''} · tid ${order.tid || '-'}\n나이스페이 가맹점 관리자에서 주문번호로 결제 여부를 확인해 주세요.`;
  const message = [
    `${tag}[NOAH ${paid ? '결제 완료' : '결제 확인 필요'}] ${order.orderId}`,
    `주문 내역: ${order.itemText}`,
    `공급가액 ${won(order.supply)} + 부가세 ${won(order.vat)} = 총 ${won(order.amount)}`,
    pay,
    order.receiptUrl ? `매출전표: ${order.receiptUrl}` : null,
    `성함: ${b.name} / 연락처: ${b.phone} / 이메일: ${b.email}`,
    b.biz ? `상호: ${b.biz}` : null,
    `영수증: ${rc}`,
    b.memo ? `메모: ${b.memo}` : null,
    `진위 확인: ${site}/checkout/complete?o=${order.orderId} (착수 전 이 링크나 나이스페이 관리자에서 결제 상태를 확인하세요)`,
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
    industry: `${tag}${paid ? '카드결제 완료' : '결제 확인 필요'} · 총 ${won(order.amount)}`,
    reference: b.reference || '',
    message,
    total: order.amount,
    receipt: b.receipt,
    bizno: b.bizno,
    timestamp: new Date().toISOString(),
    referrer: '나이스페이 결제 서버',
    page: `${site}/checkout`,
  };
}

// 한 번만 시도(최대 12초). Apps Script는 같은 내용을 두 번 받으면 두 번 기록하므로 바로 재시도하지 않고, 실패분은 크론이 다시 보낸다.
async function postSheet(c, payload) {
  if (!c.gasUrl) return false;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 12000);
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

async function recordToSheet(env, c, order) {
  if (!order.buyer || order.recorded) return;
  const ok = await postSheet(c, sheetPayload(order));
  if (!ok) {
    log('sheet_failed', { orderId: order.orderId, status: order.status });
    return;
  }
  // 손에 든 최신 상태로 저장 (KV를 다시 읽으면 오래된 값으로 되돌릴 수 있어 읽지 않음)
  order.recorded = true;
  delete order.buyer;
  await putOrder(env, order, KEEP_TTL);
  log('sheet_recorded', { orderId: order.orderId, status: order.status });
}

/* ════════ 크론: 시트 기록에 실패한 결제(paid·check)를 다시 보낸다 ════════ */
export async function retryUnrecorded(env) {
  const c = config(env);
  if (!env.ORDERS || !c.gasUrl) return;
  let cursor;
  let tried = 0;
  do {
    const page = await env.ORDERS.list({ prefix: 'order:', cursor });
    for (const k of page.keys) {
      const m = k.metadata || {};
      if (m.r !== 0 || (m.s !== 'paid' && m.s !== 'check') || Date.now() - (m.m || 0) < c.retryAfterMs) continue;
      const order = await env.ORDERS.get(k.name, 'json');
      if (order && order.buyer && !order.recorded) {
        await recordToSheet(env, c, order);
        if (++tried >= 20) return;                                  // 한 번에 너무 많이 보내지 않음
      }
    }
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);
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
          await sleep(8000);
          const again = await getOrder(env, order.orderId);
          if (again && again.status === 'pending' && (await isVerifiedPaid(c, d, again))) {
            await savePaid(env, again, d);
            await recordToSheet(env, c, again);
          }
        })(),
      );
    } else if (order.status === 'paid' && order.buyer && !order.recorded && Date.now() - Date.parse(order.markedAt || 0) > 60000) {
      ctx.waitUntil(recordToSheet(env, c, order));           // 시트 기록이 실패했던 주문 — 웹훅 재전송 때 다시 시도
    }
  } else if ((d.status === 'cancelled' || d.status === 'partialCancelled') && order.status !== d.status) {
    order.status = d.status;
    order.cancelledAt = d.cancelledAt || new Date().toISOString();
    order.markedAt = new Date().toISOString();
    await putOrder(env, order, KEEP_TTL);
  }
  return OK();
}
