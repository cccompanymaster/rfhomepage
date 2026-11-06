# 결제 흐름 로컬 테스트

나이스페이 서버 없이 결제 흐름(금액 계산·서명 검증·승인·망취소·웹훅·Apps Script 기록)을 확인하는 테스트입니다.
`mock-nicepay.mjs`가 가짜 나이스페이 API와 가짜 Apps Script를 띄웁니다. 실제 결제는 일어나지 않습니다.

## 준비

저장소 루트에 `.dev.vars` (커밋·공개 안 됨):

```
NICEPAY_CLIENT_ID=S2_testclient
NICEPAY_SECRET_KEY=test-secret-key
NICEPAY_API_BASE=http://127.0.0.1:8788/sandbox
NICEPAY_TIMEOUT_MS=1500
NICEPAY_WEBHOOK_IPS=
GAS_URL=http://127.0.0.1:8788/gas
RECORD_RETRY_AFTER_MS=2000
ORDER_LIMIT_OFF=1
```

## 실행

```bash
node tools/payment-test/mock-nicepay.mjs &               # 가짜 나이스페이 :8788
npx wrangler@4 dev --port 8787 --ip 127.0.0.1 --test-scheduled &   # 사이트 + 결제 서버 :8787 (크론 테스트 포함)
node tools/payment-test/run.mjs                          # API 테스트
python3 tools/payment-test/browser.py                    # 브라우저 테스트 (Playwright)
```

## 실제 나이스페이 샌드박스로 테스트할 때

`.dev.vars`를 샌드박스 키로 바꿉니다 (시크릿 키는 이 파일에만, 채팅·커밋 금지).

```
NICEPAY_CLIENT_ID=(샌드박스 클라이언트 키)
NICEPAY_SECRET_KEY=(샌드박스 시크릿 키)
NICEPAY_API_BASE=https://sandbox-api.nicepay.co.kr
```

`.dev.vars`의 `NICEPAY_TIMEOUT_MS`·`NICEPAY_WEBHOOK_IPS` 줄은 지우면 `wrangler.toml` 기본값(30초·나이스페이 IP)을 씁니다.

## 운영 주소에서 샌드박스 테스트

샌드박스 키일 때 운영 주소(noahhomepage.co.kr)에서는 손님에게 테스트 결제창이 열리지 않도록 결제가 꺼져(주문 접수) 보입니다.
테스트하는 사람만 `https://noahhomepage.co.kr/checkout?paytest=1` 로 들어가면 "테스트 결제 모드" 표시와 함께 샌드박스 결제창이 열립니다.
