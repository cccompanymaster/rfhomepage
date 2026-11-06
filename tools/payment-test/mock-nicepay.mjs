// 가짜 나이스페이 API + 가짜 Apps Script — 로컬 결제 흐름 테스트용 (실제 결제·네트워크 없음)
//   node tools/payment-test/mock-nicepay.mjs   →  http://127.0.0.1:8788
// tid 접두어로 동작을 고른다: OK…(정상) SLOW…(응답 지연) BADSIG…(응답 서명 틀림) DECLINE…(승인 거절) DUPE…(두 번째 승인부터 '이미 승인')
import http from 'node:http';
import { createHash } from 'node:crypto';

export const CLIENT = 'S2_testclient';
export const SECRET = 'test-secret-key';
const sha = (s) => createHash('sha256').update(s).digest('hex');

const S = { approvals: {}, approved: {}, netcancels: [], gas: [], gasFail: false, registered: {} };

function send(res, code, body, headers = {}) {
  res.writeHead(code, { 'Content-Type': 'application/json;charset=utf-8', ...headers });
  res.end(typeof body === 'string' ? body : JSON.stringify(body));
}
function paidBody(tid, reg, amount) {
  const ediDate = new Date().toISOString();
  return {
    resultCode: '0000', resultMsg: '정상 처리되었습니다.', tid, orderId: reg.orderId, ediDate,
    signature: sha(tid + amount + ediDate + SECRET), status: 'paid', paidAt: ediDate, failedAt: '0', cancelledAt: '0',
    payMethod: 'card', amount, balanceAmt: amount, goodsName: 'NOAH 홈페이지 패키지', useEscrow: false, currency: 'KRW',
    channel: 'pc', approveNo: '30001234', card: { cardCode: '04', cardName: '삼성', cardQuota: '0' },
    receiptUrl: `https://npg.nicepay.co.kr/issue/IssueLoader.do?tid=${tid}`,
  };
}

const server = http.createServer(async (req, res) => {
  let raw = '';
  for await (const ch of req) raw += ch;
  const url = new URL(req.url, 'http://x');
  const p = url.pathname;

  // ── 테스트 제어 ──
  if (p === '/__register') { const d = JSON.parse(raw); S.registered[d.tid] = d; return send(res, 200, { ok: true }); }
  if (p === '/__approve_silently') { const d = JSON.parse(raw); S.approved[d.tid] = paidBody(d.tid, S.registered[d.tid], d.amount); return send(res, 200, S.approved[d.tid]); }
  if (p === '/__gasfail') { S.gasFail = url.searchParams.get('on') === '1'; return send(res, 200, { ok: true }); }
  if (p === '/__state') return send(res, 200, S);
  if (p === '/__sign') { const d = JSON.parse(raw); return send(res, 200, { sig: sha(d.s) }); }

  // ── 가짜 Apps Script: POST → 302 → GET (실제 Apps Script 웹앱과 같은 흐름) ──
  if (p === '/gas' && req.method === 'POST') { S.gas.push(JSON.parse(raw)); return send(res, 302, '', { Location: '/gas-out' + (S.gasFail ? '?fail=1' : '') }); }
  if (p === '/gas-out') return send(res, 200, url.searchParams.get('fail') ? { ok: false, error: 'mock fail' } : { ok: true });

  // ── 가짜 나이스페이 ──
  if (!p.startsWith('/sandbox/v1/')) return send(res, 404, { resultCode: '9999' });
  const want = 'Basic ' + Buffer.from(`${CLIENT}:${SECRET}`).toString('base64');
  if (req.headers.authorization !== want) return send(res, 401, { resultCode: 'U104', resultMsg: '인증 실패' });

  if (p === '/sandbox/v1/payments/netcancel') {
    const d = JSON.parse(raw);
    const okSig = d.signData === sha(d.orderId + d.ediDate + SECRET);
    S.netcancels.push({ ...d, okSig });
    return send(res, 200, { resultCode: okSig ? '0000' : 'A123', resultMsg: okSig ? '망취소 성공' : '서명 오류', orderId: d.orderId });
  }
  const m = p.match(/^\/sandbox\/v1\/payments\/([^/]+)$/);
  if (!m) return send(res, 404, { resultCode: '9999' });
  const tid = decodeURIComponent(m[1]);

  if (req.method === 'GET') return send(res, 200, S.approved[tid] || { resultCode: '4001', resultMsg: '거래 없음', tid, status: 'ready' });

  const { amount } = JSON.parse(raw);
  S.approvals[tid] = (S.approvals[tid] || 0) + 1;
  const reg = S.registered[tid];
  if (!reg) return send(res, 200, { resultCode: '4001', resultMsg: '거래 없음' });
  if (amount !== reg.amount) return send(res, 200, { resultCode: 'A245', resultMsg: '금액 불일치' });
  if (tid.startsWith('SLOW')) await new Promise((r) => setTimeout(r, 5000));
  if (tid.startsWith('DECLINE')) return send(res, 200, { resultCode: '3011', resultMsg: '카드번호 오류', tid, orderId: reg.orderId, status: 'failed', amount });
  if (tid.startsWith('DUPE') && S.approved[tid]) return send(res, 200, { resultCode: 'A118', resultMsg: '이미 승인된 거래', tid, orderId: reg.orderId, status: 'paid', amount });
  const body = paidBody(tid, reg, amount);
  if (tid.startsWith('BADSIG')) body.signature = 'f'.repeat(64);
  S.approved[tid] = body;
  return send(res, 200, body);
});
server.listen(8788, '127.0.0.1', () => console.log('mock nicepay on http://127.0.0.1:8788'));
