"""결제 페이지 브라우저 테스트 (Playwright, headless Chromium).

wrangler dev(8787) + mock-nicepay(8788) 가 떠 있어야 한다. README.md 참고.
  python3 tools/payment-test/browser.py

나이스페이 결제창 SDK(pay.nicepay.co.kr)는 가짜 스크립트로 바꿔 끼워, requestPay에 넘어간 값을 확인한 뒤
나이스페이가 하는 것처럼 returnUrl로 form POST 를 보낸다(서명은 테스트용 키로 계산).
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

W = os.environ.get('WORKER', 'http://127.0.0.1:8787')
M = 'http://127.0.0.1:8788'
CLIENT, SECRET = 'S2_testclient', 'test-secret-key'
OUT = os.environ.get('SHOT_DIR', '/tmp/pay-shots')
os.makedirs(OUT, exist_ok=True)
results = []


def check(name, cond, extra=''):
    results.append(f"{'PASS' if cond else 'FAIL'}  {name}{'  — ' + str(extra) if extra else ''}")


def mock(path, body):
    req = urllib.request.Request(M + path, data=json.dumps(body).encode(), method='POST')
    return json.loads(urllib.request.urlopen(req).read())


FAKE_SDK = "window.AUTHNICE = { requestPay: function (p) { window.__payParams = p; } };"
BLOCK = ('googletagmanager.com', 'google-analytics.com', 'fonts.googleapis.com', 'fonts.gstatic.com', 'script.google.com')


def new_page(browser, width, sdk=True):
    ctx = browser.new_context(viewport={'width': width, 'height': 860}, device_scale_factor=1)
    page = ctx.new_page()
    page.__errors = []
    page.on('console', lambda m: page.__errors.append(m.text) if m.type == 'error' and 'net::ERR' not in m.text and 'Failed to load resource' not in m.text else None)
    page.on('pageerror', lambda e: page.__errors.append(str(e)))
    page.add_init_script("""
      window.__csp = [];
      document.addEventListener('securitypolicyviolation', e => window.__csp.push(e.violatedDirective + ' ' + e.blockedURI));
    """)
    ctx.route('**/*', lambda r: r.abort() if any(h in r.request.url for h in BLOCK) else r.fallback())
    if sdk:
        ctx.route('https://pay.nicepay.co.kr/v1/js/', lambda r: r.fulfill(status=200, content_type='text/javascript', body=FAKE_SDK))
    return ctx, page


def fill(page):
    page.fill('#b-name', '홍길동')
    page.fill('#b-phone', '01012345678')
    page.fill('#b-email', 'buyer@example.com')
    page.check('#ag-all')


def wait_js(page, expr, timeout=8.0):
    # wait_for_function 은 eval 을 써서 사이트 CSP에 막히므로 직접 폴링
    end = time.time() + timeout
    while time.time() < end:
        if page.evaluate(f'() => !!({expr})'):
            return True
        page.wait_for_timeout(150)
    raise TimeoutError(expr)


def no_hscroll(page):
    return page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')


with sync_playwright() as p:
    browser = p.chromium.launch()

    # ── 1. 데스크톱: 렌더·딥링크·합계·결제창 호출 값 → 복귀 → 완료 ──
    ctx, page = new_page(browser, 1280)
    page.goto(W + '/checkout?add=subpage,seo,logo', wait_until='networkidle')
    check('옵션 8개 렌더(단가표에서)', page.locator('#opt-list .item').count() == 8)
    check('딥링크 ?add= 3개 선택', page.locator('#opt-list .item.on').count() == 3)
    for _ in range(2):
        page.click('.item[data-k=subpage] .qb[data-d="1"]')
    total_txt = page.inner_text('#sum-total')
    check('서브페이지 3 + SEO + 로고(무료) 합계 ₩438,900', total_txt == '₩438,900', total_txt)
    note = page.inner_text('#pay-note')
    check('결제 켜짐(샌드박스) → 테스트 결제 표시, 데모 문구 아님', '샌드박스' in note and '주문을 먼저 접수' not in note, note)
    fill(page)
    page.click('#pay-btn')
    wait_js(page, 'window.__payParams')
    pp = page.evaluate('window.__payParams')
    check('requestPay 금액 = 화면 합계', pp['amount'] == 438900, pp['amount'])
    check('requestPay 필수값(clientId·method·orderId·goodsName·returnUrl)',
          pp['clientId'] == CLIENT and pp['method'] == 'cardAndEasyPay' and pp['orderId'].startswith('NO-')
          and len(pp['goodsName']) <= 40 and pp['returnUrl'] == W + '/api/nicepay/return', json.dumps({k: v for k, v in pp.items() if k != 'fnError'}, ensure_ascii=False))
    check('buyerTel 숫자만', pp['buyerTel'] == '01012345678')
    check('결제 키·비밀 값이 페이지에 없음', SECRET not in page.content())
    # 나이스페이가 하듯 returnUrl 로 form POST
    tid = 'OKbrowser' + str(int(time.time()))
    mock('/__register', {'tid': tid, 'orderId': pp['orderId'], 'amount': pp['amount']})
    token = 'NICEUNTT' + tid[-8:]
    fields = {'authResultCode': '0000', 'authResultMsg': '인증 성공', 'tid': tid, 'clientId': CLIENT, 'orderId': pp['orderId'],
              'amount': str(pp['amount']), 'mallReserved': '', 'authToken': token,
              'signature': hashlib.sha256((token + CLIENT + str(pp['amount']) + SECRET).encode()).hexdigest()}
    page.evaluate("""(f) => { const form = document.createElement('form'); form.method = 'POST'; form.action = '/api/nicepay/return';
      for (const [k, v] of Object.entries(f)) { const i = document.createElement('input'); i.type = 'hidden'; i.name = k; i.value = v; form.appendChild(i); }
      document.body.appendChild(form); form.submit(); }""", fields)
    page.wait_for_url('**/checkout/complete?o=*', timeout=10000)
    page.wait_for_selector('h1:has-text("결제가 완료되었습니다")', timeout=10000)
    body = page.inner_text('#box')
    check('완료 페이지: 결제 완료·주문번호·금액', pp['orderId'] in body and '₩438,900' in body, body.replace('\n', ' / ')[:160])
    n_purchase = page.evaluate("dataLayer.filter(a => a[0] === 'event' && a[1] === 'purchase').length")
    check('GA4 purchase 1회', n_purchase == 1, n_purchase)
    page.screenshot(path=f'{OUT}/complete-desktop.png', full_page=True)
    page.reload(wait_until='networkidle')
    page.wait_for_selector('h1:has-text("결제가 완료되었습니다")')
    check('새로고침해도 purchase 다시 안 보냄', page.evaluate("dataLayer.filter(a => a[0] === 'event' && a[1] === 'purchase').length") == 0)
    check('CSP 위반 0 (데스크톱 흐름)', page.evaluate('window.__csp.length') == 0, page.evaluate('window.__csp'))
    check('콘솔 에러 0 (데스크톱 흐름)', not page.__errors, page.__errors)
    ctx.close()

    # ── 2. 모바일 390px: 가로 스크롤 없음, 실패 복귀 안내, 입력 유지 ──
    ctx, page = new_page(browser, 390)
    page.goto(W + '/checkout?add=subpage', wait_until='networkidle')
    check('390px 결제 페이지 가로 스크롤 없음', no_hscroll(page))
    fill(page)
    page.wait_for_timeout(300)
    page.screenshot(path=f'{OUT}/checkout-390.png', full_page=True)
    page.goto(W + '/checkout?pay=fail&reason=timeout', wait_until='networkidle')
    modal = page.inner_text('#done-modal')
    check('실패 복귀(timeout) → 안내 + 전화번호, "결제 완료" 없음', '결제가 완료되지 않았습니다' in modal and '010-6658-6482' in modal and '결제가 완료되었습니다' not in modal, modal.replace('\n', ' / ')[:140])
    check('실패 복귀 후 주소 정리(?pay= 제거)', page.url.endswith('/checkout'), page.url)
    check('실패 복귀 후 입력값 유지', page.input_value('#b-name') == '홍길동')
    page.screenshot(path=f'{OUT}/fail-390.png')
    page.goto(W + '/checkout?pay=fail&reason=approve&code=3011', wait_until='networkidle')
    check('승인 거절 코드 표시', '코드 3011' in page.inner_text('#done-modal'))
    page.goto(W + '/checkout?pay=fail&reason=<script>x', wait_until='networkidle')
    check('모르는 reason → 기본 문구(주입 없음)', '일시적인 오류' in page.inner_text('#done-modal') and '<script>' not in page.inner_html('#done-body'))
    # 완료 페이지: 없는 주문·대기 주문
    page.goto(W + '/checkout/complete?o=NO-261106-AAAAAAAAAA', wait_until='networkidle')
    page.wait_for_selector('h1')
    check('완료 페이지: 없는 주문 → "결제 완료" 표시 안 함', '결제가 완료되었습니다' not in page.inner_text('body') and '찾지 못했습니다' in page.inner_text('h1'))
    check('390px 완료 페이지 가로 스크롤 없음', no_hscroll(page))
    check('CSP 위반 0 (모바일 흐름)', page.evaluate('window.__csp.length') == 0, page.evaluate('window.__csp'))
    ctx.close()

    # ── 3. 서버 금액이 화면과 다르면 결제창 안 엶 ──
    ctx, page = new_page(browser, 1280)
    ctx.route('**/api/order', lambda r: r.fulfill(status=200, content_type='application/json',
              body=json.dumps({'ok': True, 'mode': 'live', 'orderId': 'NO-261106-BBBBBBBBBB', 'amount': 1000, 'goodsName': 'x', 'clientId': CLIENT, 'method': 'card'})))
    page.goto(W + '/checkout', wait_until='networkidle')
    fill(page)
    page.click('#pay-btn')
    page.wait_for_selector('#done-modal.open')
    check('서버 금액 ≠ 화면 금액 → 결제창 안 엶', not page.evaluate('!!window.__payParams') and '금액' in page.inner_text('#done-modal'))
    ctx.close()

    # ── 3b. 결제가 켜져 있는데 /api/order 가 응답하지 않으면 주문 접수(데모)로 넘기지 않음 ──
    ctx, page = new_page(browser, 1280)
    ctx.route('**/api/order', lambda r: r.abort())
    page.goto(W + '/checkout', wait_until='networkidle')
    fill(page)
    page.click('#pay-btn')
    page.wait_for_selector('#done-modal.open')
    m3 = page.inner_text('#done-modal')
    check('결제 켜짐 + 서버 응답 실패 → 오류 안내(“준비 중” 데모 아님)', '일시적인 오류' in m3 and '준비 중' not in m3, m3.replace('\n', ' / ')[:100])
    page.goto(W + '/checkout?add=seo,%22]x', wait_until='networkidle')
    check('?add= 에 이상한 값 → 페이지 정상 동작', page.locator('#opt-list .item.on').count() == 1 and page.evaluate('window.__csp.length') == 0)
    ctx.close()

    # ── 4. 결제 키 없음(데모) → 지금과 같은 주문 접수 ──
    ctx, page = new_page(browser, 390, sdk=False)
    sdk_req = []
    ctx.on('request', lambda r: sdk_req.append(r.url) if 'nicepay' in r.url else None)
    ctx.route('**/api/config', lambda r: r.fulfill(status=200, content_type='application/json', body='{"mode":"demo"}'))
    ctx.route('**/api/order', lambda r: r.fulfill(status=200, content_type='application/json', body='{"ok":true,"mode":"demo","amount":218900}'))
    page.goto(W + '/checkout', wait_until='networkidle')
    check('데모: 결제창 스크립트 안 불러옴', not sdk_req, sdk_req)
    check('데모: 안내 문구가 주문 접수로 바뀜', '주문을 먼저 접수' in page.inner_text('#pay-note'))
    fill(page)
    page.click('#pay-btn')
    page.wait_for_selector('#done-modal.open')
    m = page.inner_text('#done-modal')
    check('데모: "주문이 접수되었습니다"·"준비 중", "결제 완료" 없음', '주문이 접수되었습니다' in m and '준비 중' in m and '결제가 완료' not in m)
    check('데모: purchase 이벤트 없음', page.evaluate("dataLayer.filter(a => a[0] === 'event' && a[1] === 'purchase').length") == 0)
    page.screenshot(path=f'{OUT}/demo-390.png')
    ctx.close()

    browser.close()

print('\n'.join(results))
fails = sum(r.startswith('FAIL') for r in results)
print(f'\n{len(results) - fails} 통과 / {fails} 실패   (스크린샷: {OUT})')
sys.exit(1 if fails else 0)
