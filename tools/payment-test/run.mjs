// 결제 흐름 자동 테스트 — wrangler dev(8787) + mock-nicepay(8788) 가 떠 있어야 한다. README.md 참고.
//   node tools/payment-test/run.mjs
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import http from 'node:http';

const W = process.env.WORKER || 'http://127.0.0.1:8787';
const M = 'http://127.0.0.1:8788';
const CLIENT = 'S2_testclient';
const SECRET = 'test-secret-key';
const sha = (s) => createHash('sha256').update(s).digest('hex');
const cat = JSON.parse(readFileSync(new URL('../../assets/data/catalog.json', import.meta.url)));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let pass = 0, failN = 0;
const results = [];
function check(name, cond, extra = '') {
  results.push(`${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '  — ' + extra : ''}`);
  cond ? pass++ : failN++;
}
const state = async () => (await fetch(M + '/__state')).json();
const buyer = { name: '테스트', phone: '010-1234-5678', email: 'test@example.com', biz: '테스트상회', memo: '', receipt: 'none', bizno: '' };
function expected(items) {
  let s = cat.base.price;
  for (const it of items) s += cat.options.find((o) => o.key === it.key).price * (it.qty || 1);
  return s + Math.round(s * cat.vatRate);
}
async function order(items, extra = {}, headers = {}) {
  const r = await fetch(W + '/api/order', { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify({ items, ...buyer, ...extra }) });
  return { status: r.status, body: await r.json() };
}
async function ret(fields) {
  const r = await fetch(W + '/api/nicepay/return', { method: 'POST', body: new URLSearchParams(fields), redirect: 'manual' });
  return { status: r.status, loc: r.headers.get('location') || '' };
}
function authFields(o, tid, { amount = String(o.amount), clientId = CLIENT, code = '0000', sig } = {}) {
  const authToken = 'NICEUNTT' + tid.slice(-8);
  return { authResultCode: code, authResultMsg: code === '0000' ? '인증 성공' : '인증 실패', tid, clientId, orderId: o.orderId, amount, mallReserved: '', authToken,
    signature: sig ?? sha(authToken + clientId + amount + SECRET) };
}
const register = (tid, o) => fetch(M + '/__register', { method: 'POST', body: JSON.stringify({ tid, orderId: o.orderId, amount: o.amount }) });
const status = async (id) => (await fetch(`${W}/api/order/${id}/status`)).json();
function kv(orderId) {
  try {
    const out = execFileSync('npx', ['wrangler@4', 'kv', 'key', 'get', '--local', '--binding', 'ORDERS', `order:${orderId}`], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
    return JSON.parse(out);
  } catch { return null; }
}
async function waitFor(fn, ms = 12000) {
  const t = Date.now();
  while (Date.now() - t < ms) { const v = await fn(); if (v) return v; await sleep(400); }
  return null;
}
let n = 0;
const tidOf = (p) => `${p}${Date.now().toString(36)}${(n++).toString(36)}`.padEnd(20, '0').slice(0, 30);

/* ── 1. 정적 파일·비공개 파일 ── */
for (const [p, code] of [['/', 200], ['/checkout', 200], ['/checkout/complete', 200], ['/pricing', 200], ['/assets/data/catalog.json', 200],
  ['/worker/index.js', 404], ['/worker/payments.js', 404], ['/.dev.vars', 404], ['/.wrangler/state/v3', 404], ['/wrangler.toml', 404], ['/tools/payment-test/run.mjs', 404]]) {
  const r = await fetch(W + p, { redirect: 'manual' });
  check(`GET ${p} → ${code}`, r.status === code, `실제 ${r.status}`);
}
const cfg = await (await fetch(W + '/api/config')).json();
check('결제 키 설정됨 → /api/config live', cfg.mode === 'live', JSON.stringify(cfg));

// 운영 주소 + 샌드박스 키 → 테스트 표시 없으면 결제 꺼짐 (Host 헤더로 운영 주소 흉내)
function hostGet(path, host) {
  return new Promise((ok) => http.get({ host: '127.0.0.1', port: 8787, path, headers: { Host: host } }, (r) => { let b = ''; r.on('data', (c) => (b += c)); r.on('end', () => ok(JSON.parse(b))); }));
}
function hostPost(path, host, body) {
  return new Promise((ok) => { const q = http.request({ host: '127.0.0.1', port: 8787, path, method: 'POST', headers: { Host: host, 'Content-Type': 'application/json' } }, (r) => { let b = ''; r.on('data', (c) => (b += c)); r.on('end', () => ok(JSON.parse(b))); }); q.end(JSON.stringify(body)); });
}
check('운영 주소 + 샌드박스 키 → demo (손님에게 테스트 결제창 안 열림)', (await hostGet('/api/config', 'noahhomepage.co.kr')).mode === 'demo');
check('운영 주소 + 샌드박스 + ?test=1 → live(sandbox 표시)', JSON.stringify(await hostGet('/api/config?test=1', 'noahhomepage.co.kr')) === '{"mode":"live","sandbox":true}');
check('운영 주소 + 샌드박스 주문 → demo 응답(KV 저장 안 함)', (await hostPost('/api/order', 'www.noahhomepage.co.kr', { items: [], ...buyer })).mode === 'demo');
check('운영 주소 + 샌드박스 주문 + test → live', (await hostPost('/api/order', 'noahhomepage.co.kr', { items: [], ...buyer, test: true })).mode === 'live');

/* ── 2. 금액은 서버가 단가표로 계산 ── */
for (const [label, items] of [
  ['기본 패키지만', []],
  ['옵션 여러 개', [{ key: 'seo' }, { key: 'form' }, { key: 'maint_y' }, { key: 'card' }]],
  ['서브페이지 수량 3', [{ key: 'subpage', qty: 3 }]],
  ['무료 옵션만(로고·검색 등록)', [{ key: 'logo' }, { key: 'register' }]],
  ['전부 + 서브페이지 10', [...cat.options.map((o) => ({ key: o.key, qty: o.maxQty ? 10 : 1 }))]],
]) {
  const r = await order(items);
  check(`금액: ${label} = ${expected(items)}`, r.status === 200 && r.body.amount === expected(items), `${r.status} ${r.body.amount}`);
}
check('무료 옵션만 더해도 218,900', (await order([{ key: 'logo' }, { key: 'register' }])).body.amount === 218900);
const tamper = await order([{ key: 'subpage', qty: 1 }], { amount: 100, total: 100, price: 1, items_price: 1 });
check('브라우저가 보낸 amount 무시', tamper.body.amount === expected([{ key: 'subpage' }]), String(tamper.body.amount));
for (const [label, items] of [
  ['모르는 옵션 키', [{ key: 'free_money' }]],
  ['수량 범위 밖(11)', [{ key: 'subpage', qty: 11 }]],
  ['수량 0', [{ key: 'subpage', qty: 0 }]],
  ['음수 수량', [{ key: 'subpage', qty: -2 }]],
  ['수량 문자열', [{ key: 'subpage', qty: '3' }]],
  ['수량 소수', [{ key: 'subpage', qty: 1.5 }]],
  ['수량 없는 옵션에 수량 2', [{ key: 'seo', qty: 2 }]],
  ['같은 옵션 두 번', [{ key: 'seo' }, { key: 'seo' }]],
  ['기본 패키지 2개', [{ key: 'base', qty: 2 }]],
  ['items가 배열 아님', { key: 'seo' }],
]) {
  const r = await order(items);
  check(`거절: ${label}`, r.status === 400 && r.body.error === 'items', `${r.status} ${JSON.stringify(r.body)}`);
}
check('거절: 휴대폰 형식', (await order([], { phone: '02-123-4567' })).status === 400);
check('거절: 세금계산서인데 사업자번호 없음', (await order([], { receipt: 'tax', bizno: '' })).status === 400);
check('거절: 다른 사이트에서 보낸 요청(Origin)', (await order([], {}, { Origin: 'https://evil.example' })).status === 403);
check('거절: 허니팟 입력', (await order([], { website: 'http://spam' })).status === 400);

/* ── 3. 승인 성공 → 완료, 시트 기록, 개인정보 삭제 ── */
const items3 = [{ key: 'subpage', qty: 3 }, { key: 'seo' }];
const o = (await order(items3)).body;
check('주문 생성: orderId·clientId·goodsName', /^NO-\d{6}-[A-Z2-9]{10}$/.test(o.orderId) && o.clientId === CLIENT && o.goodsName.length <= 40 && o.method === 'cardAndEasyPay', JSON.stringify(o));
check('주문 응답에 비밀 키 없음', !JSON.stringify(o).includes(SECRET));
const tid = tidOf('OK');
await register(tid, o);
const g0 = (await state()).gas.length;
const r1 = await ret(authFields(o, tid));
check('승인 성공 → 303 /checkout/complete', r1.status === 303 && r1.loc === `/checkout/complete?o=${o.orderId}`, `${r1.status} ${r1.loc}`);
check('승인 API 1번 호출', (await state()).approvals[tid] === 1);
const st = await status(o.orderId);
check('상태 조회 paid·금액·sandbox 표시', st.status === 'paid' && st.amount === o.amount && st.sandbox === true, JSON.stringify(st));
check('상태 조회에 개인정보·tid 없음', !/테스트|010-1234|test@example|NICEUNTT/.test(JSON.stringify(st)) && !('tid' in st));
const rec = await waitFor(async () => (await state()).gas.slice(g0).find((x) => x.orderId === o.orderId));
check('Apps Script 기록 도착 (type consult·kind order·status paid·tid)', rec && rec.type === 'consult' && rec.kind === 'order' && rec.status === 'paid' && rec.tid === tid && rec.sendBrochure === false);
check('시트에 남는 칸(업종·메시지)에 결제 완료·tid·금액', rec && rec.industry.includes('카드결제 완료') && rec.message.includes(tid) && rec.message.includes('₩'), rec && rec.industry);
check('시트 메시지에 진위 확인 링크', rec && rec.message.includes(`/checkout/complete?o=${o.orderId}`));
check('샌드박스 주문은 [샌드박스 테스트] 표시', rec && rec.industry.startsWith('[샌드박스 테스트]'));
const k1 = await waitFor(async () => { const v = kv(o.orderId); return v && v.recorded ? v : null; });
check('기록 성공 후 KV에서 이름·연락처·이메일 삭제', k1 && !k1.buyer && k1.status === 'paid' && k1.tid === tid && k1.amount === o.amount, k1 ? Object.keys(k1).join(',') : 'kv 없음');

/* ── 4. 새로고침·재전송 → 중복 승인·기록 없음 ── */
const gBefore = (await state()).gas.length;
const r2 = await ret(authFields(o, tid));
const r3 = await ret(authFields(o, tid, { sig: 'bad' }));
await sleep(1500);
check('return 재전송 → 완료 페이지로', r2.status === 303 && r2.loc.startsWith('/checkout/complete'));
check('이미 paid면 서명 틀린 재전송도 승인 안 함', r3.loc.startsWith('/checkout/complete'));
check('중복 승인 없음', (await state()).approvals[tid] === 1, String((await state()).approvals[tid]));
check('중복 시트 기록 없음', (await state()).gas.length === gBefore);

/* ── 5. 위변조·실패 ── */
async function rejectCase(label, mk, wantReason) {
  const oo = (await order([{ key: 'seo' }])).body;
  const t = tidOf('OK');
  await register(t, oo);
  const r = await ret(mk(oo, t));
  const s = await state();
  check(`${label} → reason=${wantReason}, 승인 호출 없음, paid 아님`, r.loc.includes(`reason=${wantReason}`) && !s.approvals[t] && (await status(oo.orderId)).status === 'pending', `${r.status} ${r.loc}`);
}
await rejectCase('서명 틀림', (oo, t) => authFields(oo, t, { sig: 'a'.repeat(64) }), 'verify');
await rejectCase('금액 조작(서명은 조작 금액으로 맞춤)', (oo, t) => authFields(oo, t, { amount: '1000' }), 'verify');
await rejectCase('다른 가맹점 clientId', (oo, t) => authFields(oo, t, { clientId: 'S2_other' }), 'verify');
await rejectCase('인증 실패(결제창 취소)', (oo, t) => authFields(oo, t, { code: 'A001' }), 'auth');
const ghost = await ret({ ...authFields({ orderId: 'NO-261106-AAAAAAAAAA', amount: 218900 }, 'OKghost') });
check('모르는 주문번호 → reason=expired', ghost.loc.includes('reason=expired'));

const od = (await order([])).body; const td = tidOf('DECLINE'); await register(td, od);
const rd = await ret(authFields(od, td));
check('카드 승인 거절 → reason=approve&code=3011, paid 아님', rd.loc.includes('reason=approve') && rd.loc.includes('code=3011') && (await status(od.orderId)).status === 'pending', rd.loc);

/* ── 6. 승인 응답 지연 → 망취소 ── */
const os = (await order([])).body; const ts = tidOf('SLOW'); await register(ts, os);
const gs = (await state()).gas.length;
const t0 = Date.now();
const rs = await ret(authFields(os, ts));
const s6 = await state();
const nc = s6.netcancels.find((x) => x.orderId === os.orderId);
check('승인 타임아웃 → reason=timeout', rs.loc.includes('reason=timeout'), `${rs.loc} (${Date.now() - t0}ms)`);
check('망취소 호출 (orderId·ediDate·signData 서명 맞음)', nc && nc.okSig);
check('타임아웃 주문은 paid 아님(check)', (await status(os.orderId)).status === 'check');
const recS = await waitFor(async () => (await state()).gas.slice(gs).find((x) => x.orderId === os.orderId));
check('사장님께 "결제 확인 필요" 기록', recS && recS.industry.includes('결제 확인 필요') && recS.message.includes('망취소'));

// 망취소까지 실패 → "다시 결제" 화면이 아니라 완료 페이지(확인 필요)로, 망취소 한 번 더
const on = (await order([])).body; const tn = tidOf('SLOWNC'); await register(tn, on);
const rn = await ret(authFields(on, tn));
check('승인 지연 + 망취소 실패 → 완료 페이지(check), 재결제 안내 안 함', rn.loc === `/checkout/complete?o=${on.orderId}` && (await status(on.orderId)).status === 'check', rn.loc);
const nc2 = await waitFor(async () => (await state()).netcancels.filter((x) => x.orderId === on.orderId).length >= 2, 10000);
check('망취소 재시도', Boolean(nc2));

/* ── 7. 승인 응답 서명 틀림 → 완료 처리 안 함 ── */
const ob = (await order([])).body; const tb = tidOf('BADSIG'); await register(tb, ob);
const rb = await ret(authFields(ob, tb));
check('승인 응답 서명 틀림 → paid 아님(check)', (await status(ob.orderId)).status === 'check', rb.loc);

/* ── 8. 동시 재전송(같은 tid 두 번) ── */
const oq = (await order([])).body; const tq = tidOf('DUPE'); await register(tq, oq);
const gq = (await state()).gas.length;
const [qa, qb] = await Promise.all([ret(authFields(oq, tq)), ret(authFields(oq, tq))]);
await sleep(2500);
const recQ = (await state()).gas.slice(gq).filter((x) => x.orderId === oq.orderId);
check('동시 재전송 둘 다 완료 페이지', qa.loc.startsWith('/checkout/complete') && qb.loc.startsWith('/checkout/complete'), `${qa.loc} | ${qb.loc}`);
check('동시 재전송: paid 1건', (await status(oq.orderId)).status === 'paid');
check('동시 재전송: 시트 기록 1건(KV 특성상 2건 가능 — 참고)', recQ.length === 1, `${recQ.length}건`);

/* ── 9. 웹훅 ── */
async function hook(body, raw) {
  const r = await fetch(W + '/api/nicepay/webhook', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: raw ?? JSON.stringify(body) });
  return { status: r.status, type: r.headers.get('content-type'), text: await r.text() };
}
const signRes = (d) => ({ ...d, signature: sha(d.tid + d.amount + d.ediDate + SECRET) });
const ed = new Date().toISOString();
const h1 = await hook(signRes({ resultCode: '0000', status: 'paid', tid: 'X', orderId: 'NO-261106-ZZZZZZZZZZ', amount: 218900, ediDate: ed }));
check('웹훅: 모르는 주문 → 200 "OK" text/html', h1.status === 200 && h1.text === 'OK' && /text\/html/.test(h1.type), JSON.stringify(h1));
const h2 = await hook({ resultCode: '0000', status: 'cancelled', tid, orderId: o.orderId, amount: o.amount, ediDate: ed, signature: 'b'.repeat(64) });
check('웹훅: 서명 틀림 → 거절(400), 상태 그대로', h2.status === 400 && (await status(o.orderId)).status === 'paid');
const h2b = await hook(signRes({ resultCode: '0000', status: 'cancelled', tid, orderId: o.orderId, amount: 1000, ediDate: ed }));
check('웹훅: 금액 다름 → 거절', h2b.status === 400 && (await status(o.orderId)).status === 'paid');
const gw = (await state()).gas.length;
const h3 = await hook(signRes({ resultCode: '0000', status: 'paid', tid, orderId: o.orderId, amount: o.amount, ediDate: ed }));
await sleep(1000);
check('웹훅: 이미 paid → OK, 추가 기록 없음', h3.text === 'OK' && (await state()).gas.length === gw);
const h4 = await hook(signRes({ resultCode: '0000', status: 'cancelled', tid, orderId: o.orderId, amount: o.amount, ediDate: ed, cancelledAt: ed }));
check('웹훅: 취소(관리자 환불) → 상태 cancelled', h4.text === 'OK' && (await status(o.orderId)).status === 'cancelled');
check('웹훅: 깨진 JSON → 400', (await hook(null, '{oops')).status === 400);

// returnUrl 처리 없이 승인만 된 경우(예외) → 웹훅이 8초 뒤 paid로 맞춤
const ow = (await order([{ key: 'rush' }])).body; const tw = tidOf('OK'); await register(tw, ow);
const pb = await (await fetch(M + '/__approve_silently', { method: 'POST', body: JSON.stringify({ tid: tw, amount: ow.amount }) })).json();
const gw2 = (await state()).gas.length;
const h5 = await hook(pb);
const okW = await waitFor(async () => (await status(ow.orderId)).status === 'paid', 15000);
const recW = (await state()).gas.slice(gw2).filter((x) => x.orderId === ow.orderId);
check('웹훅: 대기 주문인데 승인됨 → 8초 뒤 paid + 시트 1건', h5.text === 'OK' && okW && recW.length === 1, `${recW.length}건`);

/* ── 10. 시트 기록 실패 → 개인정보 보관(사장님 확인용), 결제는 완료 ── */
await fetch(M + '/__gasfail?on=1');
const of = (await order([])).body; const tf = tidOf('OK'); await register(tf, of);
const rf = await ret(authFields(of, tf));
await sleep(5000);
const kf = kv(of.orderId);
check('시트 기록 실패해도 결제 완료 페이지', rf.loc.startsWith('/checkout/complete') && (await status(of.orderId)).status === 'paid');
check('시트 기록 실패 → KV에 주문자 정보 유지(recorded=false)', kf && kf.buyer && kf.recorded === false);
await fetch(M + '/__gasfail?on=0');
// 크론이 기록 안 된 결제를 다시 보냄
const gc = (await state()).gas.length;
await sleep(2500);
const sr = await fetch(W + '/cdn-cgi/handler/scheduled?cron=*/15+*+*+*+*');
const recC = await waitFor(async () => (await state()).gas.slice(gc).find((x) => x.orderId === of.orderId), 15000);
const kc = await waitFor(async () => { const v = kv(of.orderId); return v && v.recorded ? v : null; }, 15000);
check('크론 재시도 → 시트 기록 + KV 개인정보 삭제', recC && kc && !kc.buyer, `scheduled ${sr.status}`);

/* ── 결과 ── */
console.log(results.join('\n'));
console.log(`\n${pass} 통과 / ${failN} 실패`);
process.exit(failN ? 1 : 0);
