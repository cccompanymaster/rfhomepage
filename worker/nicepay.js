// 나이스페이 Start API (Server 승인 모델) 호출
// 매뉴얼: https://github.com/nicepayments/nicepay-manual (api/payment-window-server.md, api/cancel.md, api/hook.md)
import { sha256Hex, safeEqual } from './lib.js';

// 결과를 알 수 없는 실패(타임아웃·네트워크 오류·JSON 아닌 응답) — 승인 호출이면 망취소 대상
export class UnknownOutcome extends Error {
  constructor(reason) {
    super(reason);
    this.name = 'UnknownOutcome';
  }
}

async function call(c, path, { method = 'POST', body, timeoutMs = c.timeoutMs } = {}) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(c.apiBase + path, {
      method,
      headers: {
        'Content-Type': 'application/json;charset=utf-8',
        Authorization: 'Basic ' + btoa(`${c.clientId}:${c.secretKey}`),
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: ctrl.signal,
    });
    const raw = await res.text();
    try {
      return JSON.parse(raw);
    } catch {
      throw new UnknownOutcome('bad_response_' + res.status);
    }
  } catch (err) {
    if (err instanceof UnknownOutcome) throw err;
    throw new UnknownOutcome(err && err.name === 'AbortError' ? 'timeout' : 'network');
  } finally {
    clearTimeout(timer);
  }
}

// 승인: POST /v1/payments/{tid}  { amount }
export function approve(c, tid, amount) {
  return call(c, `/v1/payments/${encodeURIComponent(tid)}`, { body: { amount } });
}

// 거래 조회: GET /v1/payments/{tid}
export function getPayment(c, tid) {
  return call(c, `/v1/payments/${encodeURIComponent(tid)}`, { method: 'GET', timeoutMs: 10000 });
}

// 망취소: POST /v1/payments/netcancel  { orderId, ediDate, signData = hex(sha256(orderId + ediDate + secretKey)) }
export async function netCancel(c, orderId) {
  const ediDate = new Date().toISOString();
  const signData = await sha256Hex(orderId + ediDate + c.secretKey);
  try {
    const d = await call(c, '/v1/payments/netcancel', { body: { orderId, ediDate, signData }, timeoutMs: 15000 });
    return String(d.resultCode || 'none');
  } catch (err) {
    return 'error:' + err.message;
  }
}

// 인증 결과(returnUrl POST) 서명: hex(sha256(authToken + clientId + amount + secretKey))
export async function checkAuthSignature(c, f) {
  const expected = await sha256Hex(f.authToken + f.clientId + f.amount + c.secretKey);
  return safeEqual(f.signature, expected);
}

// 승인·조회 응답과 웹훅 서명: hex(sha256(tid + amount + ediDate + secretKey))
export async function checkResultSignature(c, d) {
  if (!d || !d.signature || d.tid == null || d.amount == null || d.ediDate == null) return false;
  const expected = await sha256Hex(String(d.tid) + String(d.amount) + String(d.ediDate) + c.secretKey);
  return safeEqual(d.signature, expected);
}

// 승인 완료로 믿어도 되는 응답인지 — 결과코드·상태·서명·금액·주문번호·tid 모두 확인
export async function isVerifiedPaid(c, d, order, tid) {
  return Boolean(
    d &&
      d.resultCode === '0000' &&
      d.status === 'paid' &&
      Number(d.amount) === order.amount &&
      d.orderId === order.orderId &&
      (!tid || d.tid === tid) &&
      (await checkResultSignature(c, d)),
  );
}
