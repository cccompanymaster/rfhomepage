# 방문·광고 성과 측정 설정 (2026-11-11, 같은 날 2차 갱신)

사이트 코드에 넣을 수 있는 건 다 넣었습니다. 아래 **"사장님이 하실 일"**은 GA4·태그 매니저 관리 화면에서만 할 수 있는 설정입니다.

## 1. 사이트에 이미 들어간 것

| 무엇 | 하는 일 |
|---|---|
| GA4 `G-5CRNX231R3` | 모든 페이지 방문·유입 경로 |
| 측정 허브 `assets/js/tags.js` | 광고 픽셀·Clarity를 `TAG_IDS`에 ID만 넣으면 켬. 페이지의 전환 이벤트(`generate_lead`, `purchase`, 전화·카톡 클릭)를 켜진 광고 도구에도 그 도구의 이름으로 같이 보냄. **태그 매니저(GTM)는 걷어 냄** — 안에 Clarity 하나뿐이었고 매 페이지 수백 KB를 받았음 |
| Microsoft Clarity `wrzc98zj2h` | 히트맵·세션 녹화. GTM에서 꺼내 `tags.js`로 옮김 (같은 프로젝트라 기존 기록은 그대로) |
| 전환 이벤트 | `generate_lead`(상담·주문 접수), `consult_submit`, `brochure_submit`, `brochure_download`, `begin_checkout`, `purchase`, `intake_submit`, `buy_now_click` |
| **AI 유입 이벤트 `ai_referral`** (11/11 추가) | ChatGPT·Perplexity·Claude·Gemini·Copilot·뤼튼 등에서 들어오면 `ai_source`에 어느 AI인지 담아 보냄 |
| **신청서 유입 경로** (11/11 추가) | 상담·소개서·주문·사전정보 신청 때 구글 시트 `referrer` 칸에 "처음: naver / cpc 「홈페이지 제작」 → /pricing (11/11) \| 신청: /contact" 같은 한 줄이 같이 기록됨 (`assets/js/attrib.js`) |
| Cloudflare 방문 분석 | 보안 설정(CSP) 허용 + 개인정보처리방침 고지 완료. 대시보드에서 켜기만 하면 됨 → 아래 4번 |

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
7. ~~방문 수 2배 집계 확인~~ — 태그 매니저를 걷어 내서 해당 없음 (11/11 확인 당시에도 컨테이너 안에 GA4 태그는 없었음)
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

`assets/js/tags.js`의 `TAG_IDS`에 넣고 `python3 tools/sync_tags.py` → 보안 설정(`_headers` CSP)·개인정보처리방침 8항(맞춤형 광고 고지)·캐시 버전(`?v=`)이 같이 바뀝니다. 주간 'SEO 측정' 워크플로가 `--check`로 어긋남을 잡습니다.

| 키 | 도구 | 필요한 것 |
|---|---|---|
| `naver` | 네이버 검색광고 프리미엄 로그분석 (또는 네이버 애널리틱스 — 둘 중 하나만) | 광고 관리 → 도구 → 프리미엄 로그분석 신청 → 설치 안내 메일의 AccountId. 설치 후 메일의 "검수 요청" |
| `meta` | 메타 픽셀 | 이벤트 관리자 → 픽셀 ID |
| `kakao` | 카카오 픽셀 & SDK | 카카오 비즈니스 → 픽셀 & SDK → Track ID |
| `karrot` | 당근 픽셀 | 당근 비즈니스 전문가모드 → 전환 추적 관리 → 코드 ID |
| `clarity` | Microsoft Clarity | 켜짐 `wrzc98zj2h`. Clarity 설정 → AI Visibility → Cloudflare 연결하면 AI 봇 방문도 보임 |
| — | Cloudflare Web Analytics | 대시보드 → Analytics & Logs → Web Analytics → 사이트 추가 (코드 불필요) |

| 공통 이벤트 | 네이버 | 메타 | 카카오 | 당근 |
|---|---|---|---|---|
| `generate_lead` (상담·주문 접수) | lead | Lead | participation | Lead |
| `purchase` (결제 완료, 금액 포함) | purchase | Purchase | purchase | Purchase |
| 전화·카톡·톡톡 클릭 | custom001 | Contact | — | — |

## 5. Cloudflare — AI 크롤러 설정 확인 (중요)

2026-11-11 점검: 저장소의 `robots.txt`는 모든 AI 크롤러 허용(학습 포함)인데, 실제 사이트에서는
- GPTBot·ClaudeBot 요청이 **403으로 차단**되고 (ChatGPT·Claude **검색** 봇과 PerplexityBot은 통과)
- robots.txt 맨 앞에 Cloudflare 관리형 차단 목록(`ai-train=no`, GPTBot·ClaudeBot·Google-Extended 등 `Disallow: /`)이 붙어 내려갑니다.

dash.cloudflare.com → noahhomepage.co.kr → **AI Crawl Control** 에서
- 학습까지 허용하려면(저장소 방침): 차단 중인 크롤러를 "허용"으로, **관리형 robots.txt(Managed robots.txt) 끄기**
- 학습만 막으려면: Cloudflare 설정은 두고 `robots.txt`의 `ai-train=yes`를 `ai-train=no`로 바꿔 달라고 클로드에게 요청
주간 'SEO 측정'이 이 상태(실제 robots.txt·봇 응답 코드)를 매주 기록합니다.
