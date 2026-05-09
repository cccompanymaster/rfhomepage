# Cloudflare Pages 배포 가이드

NOAH 사이트를 GitHub Pages → **Cloudflare Pages**로 옮기는 5분 가이드.

---

## 🎯 왜 Cloudflare Pages인가

| 항목 | GitHub Pages | Cloudflare Pages |
|---|---|---|
| 빌드 안정성 | Jekyll 빌더 이슈 ⚠️ | **정적 그대로 업로드** ✅ |
| 한국 응답속도 | 보통 | **빠름** (CDN) |
| 트래픽 한도 | 100GB/월 | **무제한** |
| 사용자 정의 도메인 | 무료 + SSL | 무료 + SSL |
| Preview URL | ❌ | ✅ 브랜치별 자동 |
| 비용 | 무료 | **무료** |

---

## ✅ 사전 준비 (이미 완료됨)

- [x] GitHub 저장소 푸시 완료
- [x] `.nojekyll` 파일 (있어도 무관)
- [x] `_headers` — 캐시·보안 헤더 (방금 추가)
- [x] `_redirects` — 리다이렉트 룰 (방금 추가)
- [x] `404.html` — 커스텀 404 페이지

---

## 🚀 배포 단계 (5분)

### 1단계 — Cloudflare Pages 접속

1. https://dash.cloudflare.com 로그인
2. 좌측 메뉴 → **Workers & Pages**
3. 우측 상단 **Create application** → **Pages** 탭 → **Connect to Git** 클릭

### 2단계 — GitHub 연결

1. **Connect GitHub account** → 기존 연결 사용 또는 신규 인증
2. 저장소 선택: **`cccompanymaster/rfhomepage`**
3. **Begin setup** 클릭

### 3단계 — 빌드 설정

다음과 같이 정확히 입력:

| 항목 | 값 |
|---|---|
| **Project name** | `noah` (또는 원하는 이름 — 임시 URL이 됨) |
| **Production branch** | `claude/homepage-reference-designs-SXEMC` ⚠️ 정확히 |
| **Framework preset** | **None** |
| **Build command** | (비워두기) |
| **Build output directory** | `/` |
| **Root directory** | (비워두기) |
| **Environment variables** | (없음) |

> ⚠️ Framework preset은 **반드시 None** 으로. Jekyll·Next.js 등을 자동 감지하면 빌드 실패합니다.

### 4단계 — 배포 시작

1. **Save and Deploy** 클릭
2. 약 30초~1분 후 배포 완료 ✅
3. 임시 URL 발급: `https://noah.pages.dev` 형식

이 URL로 접속하면 NOAH 사이트가 정상 표시되어야 합니다.

### 5단계 — 자동 재배포 확인

이후부터는 **GitHub에 푸시할 때마다 자동으로 재배포**됩니다.
- 매번 배포 로그를 Cloudflare 대시보드에서 확인 가능
- 다른 브랜치 푸시 시 자동으로 **Preview URL** 생성

---

## 🌐 (선택) 사용자 정의 도메인 연결

도메인을 가지고 계시거나 새로 사실 거라면:

### A. Cloudflare에 도메인 등록되어 있는 경우

1. Pages 프로젝트 → **Custom domains** → **Set up a custom domain**
2. 도메인 입력 (예: `noah.kr`)
3. Cloudflare가 DNS를 자동으로 설정 → SSL도 자동
4. 1~2분 안에 활성화

### B. 도메인이 다른 곳에 있는 경우

1. **Cloudflare Dashboard → Add a Site** 로 도메인을 Cloudflare에 먼저 등록
2. 등록 시 안내되는 Cloudflare **네임서버** 2개를 도메인 등록업체(가비아 등)에서 변경
3. 24시간 이내 전파 완료 후, A 단계로

### 추천 도메인

| 후보 | 가격(연) | 비고 |
|---|---|---|
| `noah.kr` | ₩22,000 | 가장 짧음, 한국 신뢰 |
| `noah.co.kr` | ₩22,000 | 전통적, 신뢰 |
| `noahhomepage.com` | ₩15,000 | 명확함 |
| `getnoah.com` | ₩15,000 | SaaS 톤 |

---

## 🧹 GitHub Pages 끄기 (배포 확인 후)

Cloudflare Pages가 정상 동작하면, 혼란 방지를 위해 GitHub Pages는 끄시는 걸 추천:

1. https://github.com/cccompanymaster/rfhomepage/settings/pages
2. 우측 상단 **Unpublish site** 클릭
3. 확인

(`.github/workflows/deploy-pages.yml` 파일은 그대로 두셔도 무방. 사용 안 됨)

---

## 🔍 배포 후 확인 체크리스트

배포 완료 URL에서 다음 5가지 확인:

- [ ] **메인 페이지** "돈 벌어다주는 홈페이지, 199,000원으로" 정상
- [ ] **하단 배너** "이달 잔여 N건" 표시 (IP 기반 카운트 동작)
- [ ] **우측 세로 배너** 카카오·전화·메일 아이콘 3개
- [ ] **12개 레퍼런스 카드** iframe 미리보기 정상 (호버 시 동작)
- [ ] **상담 신청 폼** 드롭다운 가독성 OK + 제출 시 Apps Script로 전송

---

## 🛠️ 문제 해결

### 배포가 실패하면

- **Build log** 확인: Cloudflare 대시보드 → Pages 프로젝트 → Deployments → 실패한 항목 클릭
- 가장 흔한 원인: Framework preset이 None이 아님 → 다시 설정

### iframe 프리뷰가 안 뜨면

- 모든 레퍼런스 페이지가 **같은 도메인**에서 서빙되어야 함 (Cloudflare Pages는 자동으로 OK)
- 이전 GitHub Pages URL을 캐시해 둔 브라우저는 **강력 새로고침** (`⌘+Shift+R`)

### 이미지 로딩 느림

- Cloudflare Pages는 자동 CDN 캐싱하므로 첫 1회 후 빠름
- `_headers` 파일에 1년 캐시 설정해 두었으니 정상

---

## 📊 비용 / 한도 (현재 NOAH 기준)

| 자원 | 사용량 (예상) | 무료 한도 |
|---|---|---|
| 월 빌드 횟수 | 10~30회 | 500회 |
| 트래픽 | <10GB/월 | 무제한 |
| 동시 빌드 | 1 | 1 |
| 사이트 수 | 1 | 무제한 |

→ **유료 전환 가능성: 거의 0** (월 100만 PV 기준)

---

## 📌 Cloudflare 무료 플랜에서 추가로 활용 가능

이미 Cloudflare를 쓰시면 다음도 무료로 켤 수 있습니다:

- **Web Analytics**: 쿠키 없는 방문자 통계 (GDPR 안전)
- **Bot Fight Mode**: 무료 봇 차단
- **Brotli 압축**: 자동 적용
- **HTTP/3**: 자동 적용
- **이미지 자동 최적화** (Polish): 유료 플랜이지만 고려 가치

---

배포하다 막히는 부분 있으면 어디 단계인지 알려주세요. 화면 캡처도 환영입니다.
