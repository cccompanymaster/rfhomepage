# 방문·광고 성과 측정 설정 (2026-11-11)

사이트 코드에 넣을 수 있는 건 다 넣었습니다. 아래 **"사장님이 하실 일"**은 GA4·태그 매니저 관리 화면에서만 할 수 있는 설정입니다.

## 1. 사이트에 이미 들어간 것

| 무엇 | 하는 일 |
|---|---|
| GA4 `G-5CRNX231R3` | 모든 페이지 방문·유입 경로 |
| 구글 태그 매니저 `GTM-WZWCZTKJ` | 코드 수정 없이 태그 추가하는 보관함 |
| 전환 이벤트 | `generate_lead`(상담·주문 접수), `consult_submit`, `brochure_submit`, `brochure_download`, `begin_checkout`, `purchase`, `intake_submit`, `buy_now_click` |
| **AI 유입 이벤트 `ai_referral`** (11/11 추가) | ChatGPT·Perplexity·Claude·Gemini·Copilot·뤼튼 등에서 들어오면 `ai_source`에 어느 AI인지 담아 보냄 |
| **신청서 유입 경로** (11/11 추가) | 상담·소개서·주문·사전정보 신청 때 구글 시트 `referrer` 칸에 "처음: naver / cpc 「홈페이지 제작」 → /pricing (11/11) \| 신청: /contact" 같은 한 줄이 같이 기록됨 (`assets/js/attrib.js`) |
| Clarity·Cloudflare 방문 분석 | 보안 설정(CSP) 허용 + 개인정보처리방침 고지 완료. **스크립트는 아직 없음** → 아래 4번 |

## 2. 사장님이 GA4에서 하실 일 (https://analytics.google.com → 관리 톱니바퀴)

1. **데이터 보관 기간 14개월로** — 관리 → 데이터 수집 및 수정 → 데이터 보존 → 이벤트 데이터 보존 **14개월** → 저장
   (기본값 2개월이라 그대로 두면 탐색 보고서에서 지난 기록이 사라집니다)
2. **전환(주요 이벤트) 표시** — 관리 → 데이터 표시 → 이벤트 → `generate_lead`, `purchase` 오른쪽 별(☆) 켜기
   (이벤트는 한 번이라도 발생한 뒤 24시간 안에 목록에 나타납니다. 안 보이면 상담 폼을 한 번 테스트로 보내 보세요)
3. **맞춤 측정기준 등록** — 관리 → 데이터 표시 → 맞춤 정의 → 맞춤 측정기준 만들기 (범위: 이벤트)
   - `ai_source` — 어느 AI에서 왔는지
   - `design` — 고른 디자인
   - `lead_source` — 어느 신청서에서 접수됐는지
4. **AI 검색 채널 따로 묶기** — 관리 → 데이터 표시 → 채널 그룹 → 새 채널 그룹 만들기 → 채널 추가
   - 채널 이름: `AI 검색`
   - 조건: **소스** · **정규식과 일치** · 아래 식을 붙여넣기
     ```
     .*(chatgpt|openai|perplexity|claude|gemini|copilot|wrtn|clova-x|liner|you\.com|phind|deepseek|grok).*
     ```
   - 채널 순서에서 `AI 검색`을 **추천(Referral)보다 위**로 올리고 저장
5. **서치콘솔 연결** — 관리 → 제품 링크 → Search Console 링크 → noahhomepage.co.kr 선택
6. **내 방문 빼기** — 관리 → 데이터 스트림 → 웹 스트림 → 태그 설정 구성 → 내부 트래픽 정의 → 사무실·집 IP 추가 → 관리 → 데이터 필터에서 "내부 트래픽" 필터를 **활성**으로
7. **방문 수 2배 집계 확인** — 사이트에 GA4가 직접 들어가 있는데, 태그 매니저 안에도 GA4 태그(`G-5CRNX231R3`)가 있으면 페이지뷰가 두 번 잡힙니다.
   https://tagmanager.google.com → 컨테이너 `GTM-WZWCZTKJ` → 태그 목록에 "Google 태그"나 "GA4 구성"이 있으면 알려 주세요. 정리해 드립니다.
8. **구글 애즈를 시작하면** — 관리 → 제품 링크 → Google Ads 링크 → 2번의 전환을 애즈로 가져오기

## 3. 광고 링크 주소 규칙 (어느 광고에서 왔는지 이름표 붙이기)

광고나 SNS에 사이트 주소를 넣을 때 뒤에 아래처럼 붙이면, GA4와 구글 시트 신청 기록 양쪽에 그 이름이 남습니다.

| 어디 | 주소 뒤에 붙일 것 |
|---|---|
| 네이버 검색광고 | 광고 관리 → 도구 → **자동 추적 URL 파라미터 사용** 켜기 (키워드가 자동으로 붙음, 따로 안 붙여도 됨) |
| 구글 애즈 | 계정 설정 → **자동 태그 추가** 켜기 |
| 인스타·페이스북 광고 | `?utm_source=meta&utm_medium=paid_social&utm_campaign=광고이름` |
| 카카오모먼트 | `?utm_source=kakao&utm_medium=display&utm_campaign=광고이름` |
| 당근 광고 | `?utm_source=daangn&utm_medium=local_ad&utm_campaign=광고이름` |
| 크몽 소개글 링크 | `?utm_source=kmong&utm_medium=referral` |
| 네이버 블로그 글 속 링크 | `?utm_source=naver_blog&utm_medium=social&utm_campaign=글제목` |
| 인스타 프로필 링크 | `?utm_source=instagram&utm_medium=profile` |

예) `https://noahhomepage.co.kr/pricing?utm_source=meta&utm_medium=paid_social&utm_campaign=11월_카페업종`

## 4. ID를 받으면 설치할 것

| 도구 | 필요한 것 | 비고 |
|---|---|---|
| Microsoft Clarity | 프로젝트 ID (https://clarity.microsoft.com) | 보안 설정 허용됨. 설치 후 Clarity 설정 → Google Analytics 연동 켜기 |
| Cloudflare Web Analytics | Cloudflare 대시보드에서 켜기만 | Analytics & Logs → Web Analytics → 사이트 추가 → 자동 설치. 보안 설정 허용됨 |
| 네이버 애널리틱스 / 검색광고 프리미엄 로그분석 | 공통 스크립트 ID | 보안 설정에 wcs.naver.net 추가 필요 (설치할 때 함께) |
| 메타·카카오·당근 픽셀 | 각 픽셀 ID | 개인정보처리방침에 '맞춤형 광고(행태정보)' 조항 추가 필요 (설치할 때 함께) |
