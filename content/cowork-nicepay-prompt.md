# 노아홈페이지 — 나이스페이 결제 연동 작업 지시서 (Claude Cowork용)

너는 노아홈페이지(https://noahhomepage.co.kr) 결제 페이지에 **나이스페이먼츠 Start API(Server 승인 모델)** 카드·간편결제를 붙이는 개발자다.
아래 사실·규칙·순서를 그대로 따른다. 모르는 것은 추측하지 말고 나에게 묻는다. 사람이 해야 하는 단계(⏸ 표시)에서는 멈추고 요청한다.

---

## 1. 저장소와 배포 — 반드시 먼저 이해할 것

- 저장소: GitHub `cccompanymaster/rfhomepage` (**공개 저장소** — 비밀 값은 절대 커밋 금지)
- 운영 배포 브랜치: `claude/homepage-reference-designs-SXEMC` — 이 브랜치에 push하면 Cloudflare Workers Builds가 **바로 운영 사이트에 배포**한다.
  → 작업은 새 브랜치 `feature/nicepay-payment`에서 하고, 샌드박스 테스트를 내가 확인한 뒤에만 배포 브랜치에 합친다.
- 호스팅: Cloudflare **Workers Static Assets**. 지금 `wrangler.toml`은 정적 파일만 올린다:
  ```toml
  name = "rfhomepage"
  compatibility_date = "2024-11-01"
  [assets]
  directory = "."
  not_found_handling = "404-page"
  ```
  - `directory = "."` 이라서 **저장소 루트의 모든 파일이 공개 URL로 올라간다.** 새로 만드는 서버 코드 폴더(예: `worker/`)와 `.dev.vars`는 반드시 `.assetsignore`에 추가해 공개되지 않게 한다. `.dev.vars`는 `.gitignore`에도 추가한다.
  - `/x.html` 은 `/x` 로 서빙된다. `_headers`(보안 헤더·CSP), `_redirects` 가 적용된다.
- 빌드 순서: 페이지를 고친 뒤 **마지막에 항상** `python3 tools/build_assets.py` 실행 (Tailwind 빌드 + CSS·JS 링크에 `?v=해시` 부여 + FAQ 구조화 데이터 동기화). node/npx 필요.
- 화면 문구는 쉬운 한국어. 과장·거짓 금지(아래 7절).

## 2. 지금 결제 페이지 상태 (`checkout.html`)

- 상품 정의(부가세 별도 단가, 원):
  - BASE `base` NOAH 홈페이지 패키지 199,000
  - `subpage` 서브페이지 추가 50,000 × 수량(1–10)
  - `logo` 로고 제작 — 심플 0 (무료 옵션)
  - `card` 명함 제작 50,000
  - `form` 문의 폼 + 자동 메일 50,000
  - `register` 네이버·구글·빙 검색 등록 0 (무료 옵션)
  - `seo` SEO 심화 세팅 50,000
  - `rush` 당일 제작 50,000
  - `maint_y` 유지보수 1년 200,000
  - 합계 = 공급가 + 부가세 `Math.round(공급가 × 0.1)` (예: 기본만 199,000 + 19,900 = 218,900)
- 결제 모듈은 **포트원(PortOne) V2 코드**가 들어 있지만 키가 비어 있어 **데모 모드**로 동작한다: 결제창 없이 주문만 Google Apps Script(`GAS_URL`)로 보내고 "영업일 1일 안에 연락" 안내를 띄운다.
  - 주문 전송: `postGAS({ type: 'consult', kind: 'order', sendBrochure: false, orderId, status, name, phone, email, industry, reference, message, total, receipt, bizno })` — Apps Script `handleConsult`가 시트에 적고 사장님께 메일을 보낸다. **이 경로를 그대로 재사용**한다(Apps Script 수정 없이 주문이 사장님께 도착).
- 포트원 관련: `<script src="https://cdn.portone.io/v2/browser-sdk.js">`, `PORTONE` 설정, `PortOne.requestPayment`, `afterPayment`, `?paymentId=` 복귀 처리, `_headers` CSP의 portone 도메인, 이용약관 3조 "포트원 연동", 개인정보처리방침 위탁표 "포트원(PortOne)" — **나이스페이로 교체하면서 모두 정리**한다.
- 입력 필드: 성함 `#b-name`, 연락처 `#b-phone`(010-0000-0000), 이메일 `#b-email`, 상호 `#b-biz`, 메모 `#b-memo`, 영수증 `receipt`(none/cash/tax) + 사업자번호 `#b-bizno`, 약관·개인정보 동의 체크, 봇 허니팟 `#b-site`. 옵션 선택은 `?add=키` 딥링크로도 들어온다.

## 3. 나이스페이 Start API 사실 (공식 매뉴얼 github.com/nicepayments/nicepay-manual 기준 — 구현 전에 최신 문서로 다시 확인)

- 결제창 JS SDK: `<script src="https://pay.nicepay.co.kr/v1/js/"></script>` → `AUTHNICE.requestPay({...})`
  - 필수: `clientId`, `method`, `orderId`(가맹점 고유, 64자 이내, 재사용 금지), `amount`(정수), `goodsName`(40자 이내), `returnUrl`
  - 선택: `buyerName`, `buyerTel`(숫자만), `buyerEmail`, `mallReserved`(500자), `fnError: function(result){...}`
  - `method`: 계약된 수단에 맞춰 `card` 또는 `cardAndEasyPay` 등. **가상계좌(vbank)는 이번 범위에서 제외**(입금 웹훅 처리가 따로 필요).
  - 샌드박스와 운영의 SDK 주소는 같고, 어느 쪽인지는 `clientId`가 정한다.
- 인증 결과: 결제창이 끝나면 **사용자 브라우저가 `returnUrl`로 form POST**(`application/x-www-form-urlencoded`) 한다.
  - 필드: `authResultCode`('0000'=인증 성공), `authResultMsg`, `tid`, `clientId`, `orderId`, `amount`, `mallReserved`, `authToken`, `signature`
  - 위변조 검증: `signature === hex(sha256(authToken + clientId + amount + secretKey))`
  - 문서 요구: **금액·orderId·서명이 내가 만든 주문과 일치하는지 확인한 뒤에만** 승인 API를 호출한다.
- 승인 API(Server 승인): `POST {API_BASE}/v1/payments/{tid}`
  - `API_BASE`: 샌드박스 `https://sandbox-api.nicepay.co.kr`, 운영 `https://api.nicepay.co.kr`
  - 헤더: `Content-Type: application/json`, `Authorization: Basic base64(clientId:secretKey)`
  - 본문: `{ "amount": 정수 }`
  - 성공: 응답 `resultCode === "0000"` 이고 `status === "paid"`. 응답 `signature === hex(sha256(tid + amount + ediDate + secretKey))` 도 검증한다.
  - **승인 호출이 read-timeout 나면 망취소**: `POST {API_BASE}/v1/payments/netcancel` 본문 `{ orderId, ediDate, signData: hex(sha256(orderId + ediDate + secretKey)) }` (1시간 안에만 가능)
- 조회: `GET {API_BASE}/v1/payments/{tid}`, `GET {API_BASE}/v1/payments/find/{orderId}`
- 취소: `POST {API_BASE}/v1/payments/{tid}/cancel` 본문 `{ reason, orderId, cancelAmt(부분취소 시) }` — **이번 범위에서는 만들지 않는다.** 환불은 나이스페이 가맹점 관리자에서 처리한다.
- 웹훅: 가맹점 관리자 **개발정보 > 웹훅**에 URL 등록. 승인·취소 시 `POST application/json`(본문은 승인 응답과 같은 형식, `signature` 포함). 응답은 **HTTP 200 + 본문 `OK`**(`Content-Type: text/html;charset=utf-8`)여야 성공 처리된다.
- 샌드박스: 키가 운영과 따로 있고, 승인 응답은 실제 결제가 아닌 임의 값이다(카드사는 삼성카드로 고정). 부분취소 불가.
- 운영 전환: clientId·secretKey를 운영 키로, `API_BASE`를 운영 주소로 바꾼다.

## 4. 만들 구조

```
[결제 페이지 checkout]
  1) POST /api/order  { items:[{key,qty}], name, phone, email, biz, memo, receipt, bizno }
       → Worker가 단가표로 금액을 **서버에서 다시 계산**, orderId 발급, 대기 주문 저장(KV, 2시간 만료)
       → { orderId, amount, goodsName, clientId }   (결제 키 미설정이면 { mode:"demo" } → 기존 데모 접수 흐름 유지)
  2) AUTHNICE.requestPay({ clientId, method, orderId, amount, goodsName, returnUrl: origin + "/api/nicepay/return", buyerName, buyerTel, buyerEmail, fnError })
[나이스페이 → 브라우저 form POST]
  3) POST /api/nicepay/return
       → authResultCode 확인 → KV에서 주문 조회 → amount·orderId·signature 검증
       → 승인 API 호출 → 응답 resultCode·status·amount·signature 검증
       → 주문 상태 paid 저장, Apps Script로 주문 기록(type:'consult', kind:'order', status:'paid', tid 포함)
       → 303 리다이렉트 /checkout/complete?o={orderId}   (실패는 /checkout?pay=fail&reason=...)
  4) GET /api/order/{orderId}/status → { status, amount, itemText }  (이름·연락처 같은 개인정보는 돌려주지 않음)
[나이스페이 → 서버]
  5) POST /api/nicepay/webhook → signature·금액 검증 → 상태 동기화(이미 paid면 그대로) → "OK"
```

- Worker 엔트리: `worker/index.js`(또는 `.ts`). `wrangler.toml`에 `main`, `[assets] binding = "ASSETS"`, `/api/*`만 Worker가 먼저 처리하도록 설정(`run_worker_first` — 현재 Cloudflare 문서의 문법을 확인해서 쓴다). 그 밖의 요청은 `env.ASSETS.fetch(request)`로 정적 파일을 그대로 돌려준다. `not_found_handling = "404-page"` 유지.
- 설정 값:
  - `wrangler.toml [vars]`: `NICEPAY_CLIENT_ID`(공개돼도 되는 클라이언트 키), `NICEPAY_API_BASE`, `NICEPAY_METHOD`, `GAS_URL`
  - **비밀 값 `NICEPAY_SECRET_KEY`는 코드·toml·커밋에 절대 넣지 않는다.** 로컬은 `.dev.vars`(커밋·공개 제외), 운영은 Cloudflare 대시보드의 **Secret** 타입(⏸ 사장님이 입력).
  - KV 바인딩 `ORDERS` (⏸ 사장님이 네임스페이스를 만들어 id 전달)
- 단가표는 **한 곳에서만** 정의한다(예: `assets/data/catalog.json`을 Worker가 import하고 결제 페이지도 같은 파일을 사용). 결제 페이지 화면 금액과 서버 계산 금액이 어긋날 수 없게.
- 완료 페이지 `/checkout/complete`(정적 페이지 + 상태 조회): paid일 때만 "결제가 완료되었습니다" + 주문번호·금액·다음 단계(영업일 1일 안 착수 안내). GA4 `purchase` 이벤트는 **여기서 서버가 paid로 확인한 뒤 한 번만**(orderId로 중복 방지) 보낸다. 지금 checkout.html의 클라이언트 측 `purchase` 이벤트는 제거.
- 저장 정보 최소화: Apps Script 기록이 성공하면 KV에서 이름·연락처·이메일은 지우고 상태·금액·tid·주문 내역만 남긴다.

## 5. 결제·보안 규칙 (어기면 안 됨)

1. 금액은 **항상 서버가 단가표로 계산**한다. 브라우저가 보낸 금액·옵션명은 믿지 않는다(옵션 키·수량만 받는다, 알 수 없는 키·범위 밖 수량은 거절).
2. `returnUrl`에서 **서명·금액·orderId를 모두 검증한 뒤에만** 승인 API 호출. 승인 응답도 금액·서명을 다시 검증.
3. 같은 주문 중복 승인 방지: 이미 paid면 승인 API를 다시 부르지 않고 완료 페이지로 보낸다(새로고침·뒤로가기 대비).
4. 승인 호출 타임아웃(예: 15초) → 망취소 → 실패 안내 + 전화번호.
5. **실제 승인(resultCode 0000, status paid)을 확인하기 전에는 어떤 화면에서도 "결제 완료"를 표시하지 않는다.** 결제 키가 없으면 지금처럼 "주문 접수" 데모 흐름만.
6. secretKey는 서버 코드에서만 쓰고, 응답·로그·에러 메시지·클라이언트 번들에 절대 노출하지 않는다. 로그에 카드·개인정보를 남기지 않는다.
7. 웹훅은 서명·금액 검증 후에만 상태를 바꾸고, 모르는 orderId는 무시하고 "OK".

## 6. 함께 고칠 것

- `_headers` CSP: 포트원 도메인 제거, 나이스페이 추가 — `script-src`에 `https://pay.nicepay.co.kr`, 결제창이 쓰는 `frame-src`·`form-action`·`connect-src` 도메인은 **샌드박스 결제를 실제로 띄워 브라우저 콘솔의 CSP 위반을 보고 최소한으로** 추가한다(`*.nicepay.co.kr` 범위 안에서).
- 이용약관(`terms.html`) 3조: "카드·간편결제(포트원 연동)" → "카드·간편결제(나이스페이먼츠)". 문서 끝 개정일에 날짜와 "(결제대행사 변경)" 추가.
- 개인정보처리방침(`privacy.html`) 위탁표: "포트원(PortOne) 및 연동 결제대행사" → "나이스페이먼츠 주식회사 — 결제 승인·취소 처리". 개정일 추가.
- 데모 모드 안내 문구 "온라인 카드결제는 준비 중입니다"는 결제가 켜지면 나오지 않게.

## 7. 사람이 할 일 — 이 단계에서 멈추고 나에게 요청 (⏸)

1. ⏸ 나이스페이 가맹점 관리자(start.nicepay.co.kr) → 개발정보: **샌드박스 키(Server 승인 방식)** 발급. 클라이언트 키는 알려 주고, 시크릿 키는 `.dev.vars`에 내가 직접 넣거나 너에게 로컬 파일로만 전달한다(채팅·커밋 금지).
2. ⏸ Cloudflare 대시보드: KV 네임스페이스 생성(예: `rfhomepage-orders`) → id 전달 / Workers → rfhomepage → Settings → Variables and Secrets 에 `NICEPAY_SECRET_KEY`를 **Secret**으로 입력.
3. ⏸ 배포 후 나이스페이 개발정보 > 웹훅에 `https://noahhomepage.co.kr/api/nicepay/webhook` 등록 → TEST 호출.
4. ⏸ 운영 전환: 운영 키 발급, Secret 교체, `NICEPAY_API_BASE`를 운영 주소로 — 내가 승인한 뒤에만.

## 8. 작업 순서 (단계마다 확인하고 다음으로)

1. 저장소 클론·브랜치 생성, `checkout.html`·`_headers`·`wrangler.toml`·`.assetsignore`·`tools/build_assets.py` 읽고 계획을 5줄로 나에게 보고.
2. 단가표 단일 소스화 + Worker 골격(`/api/*` 라우팅, 그 외 정적 파일) + `npx wrangler dev`로 기존 페이지가 그대로 뜨는지 확인.
3. `/api/order` (금액 서버 계산·검증, KV 저장, 데모 모드 판정).
4. 결제 페이지 교체(SDK·requestPay·실패 처리), 포트원 코드 제거.
5. `/api/nicepay/return` (검증·승인·망취소·Apps Script 기록·리다이렉트), 완료 페이지와 상태 조회.
6. `/api/nicepay/webhook`.
7. CSP·약관·개인정보처리방침 수정, `python3 tools/build_assets.py`.
8. 샌드박스 테스트(아래) → 결과 보고 → 내 확인 후 배포 브랜치에 합치기.

## 9. 테스트 체크리스트 (샌드박스, 로컬 `wrangler dev`와 배포 후 각각)

- [ ] 기본 패키지만 / 옵션 여러 개 / 서브페이지 수량 3 → 결제창 금액이 화면 합계(부가세 포함)와 같다
- [ ] 무료 옵션(로고·검색 등록)만 더해도 금액 변화 없음
- [ ] 개발자도구로 금액·옵션을 조작한 요청 → 서버가 거절하거나 올바른 금액으로 계산
- [ ] 결제창 닫기·실패 → 실패 안내, 주문은 paid가 아님
- [ ] 승인 성공 → 완료 페이지, Apps Script 시트·메일에 주문(tid 포함) 도착, GA4 purchase 1회
- [ ] 완료 페이지 새로고침·return 재전송 → 중복 승인·중복 기록 없음
- [ ] 서명이 틀린 return/웹훅 → 거절
- [ ] 휴대폰(390px)에서 결제창·복귀 정상, 가로 스크롤 없음
- [ ] 결제 키 미설정 상태 → 지금과 같은 데모 주문 접수
- [ ] 공개 URL로 `/worker/…`, `/.dev.vars` 접근 시 404 (서버 코드·비밀이 공개되지 않음)
- [ ] 브라우저 콘솔 CSP 위반·에러 0

## 10. 보고 형식

① 바꾼 파일과 이유 ② 테스트 체크리스트 결과(통과/실패와 증거) ③ 내가 해야 할 남은 단계(⏸) ④ 하지 않은 것과 이유.

## 하지 말 것

- 운영 배포 브랜치에 바로 push, 운영 키 사용(내 승인 전), secretKey 커밋·노출
- 클라이언트에서 승인 API 호출, 클라이언트가 보낸 금액 신뢰
- 결제 실패·미확인 상태에서 "결제 완료" 표시, 가짜 성공 화면
- 가상계좌·정기결제·자동 취소 기능 추가(이번 범위 밖)
- 관련 없는 페이지 디자인·문구 변경
