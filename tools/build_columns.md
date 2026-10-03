# 칼럼 빌더 — 검색 노출 설계

`content/columns/batch-*.json`(원고)에서 `columns/` 아래 정적 페이지를 만듭니다.

```bash
python3 tools/build_columns.py          # 페이지만 재생성
python3 tools/build_columns.py --og     # OG 이미지까지 재생성
```

원고를 고쳤거나 새 글을 추가했으면 이 한 줄만 다시 돌리면 목록·허브·사이트맵·RSS까지 전부 갱신됩니다.

## 무엇이 만들어지나

| 산출물 | 개수 | 역할 |
|---|---|---|
| `columns/<slug>.html` | 100 | 개별 칼럼 |
| `columns/topic/<cluster>.html` | 8 | 토픽 허브(필라 페이지) |
| `columns/index.html` | 1 | 전체 목록 — 검색·필터·페이지네이션 |
| `columns/feed.xml` | 1 | RSS (최근 40편) |
| `assets/images/og/<slug>.png` | 100 | 공유용 OG 카드 1200×630 |
| `sitemap.xml` | — | 칼럼 109 URL을 `lastmod`와 함께 갱신 |

## 검색 노출을 위해 넣은 것

**1. 토픽 클러스터 구조**
100편을 8개 주제로 묶고, 주제마다 허브 페이지를 둡니다.
개별 글 → 허브 → 다른 글로 이어지는 내부링크가 만들어져 주제별 권위가 한곳에 모입니다.
빵부스러기(Breadcrumb)도 `홈 › 칼럼 › 주제 › 글` 4단계로 잡았습니다.

**2. 본문 문맥 내부링크**
`ANCHOR_TERMS` 사전을 기준으로, 본문에 나오는 용어를 관련 칼럼으로 연결합니다.
- 용어당 1회, 글당 최대 5개 (과다 링크는 오히려 감점 요인)
- `<p>`·`<li>` 안의 텍스트만, 이미 링크인 곳은 건너뜀
- 자기 자신으로는 연결하지 않음
현재 총 331개, 글당 평균 3.3개가 붙습니다.

새 용어를 늘리려면 `ANCHOR_TERMS`에 `'용어': 'slug'`를 추가하세요.

**3. 목차 + 제목 앵커**
h2마다 `id`를 부여하고 상단에 목차를 만듭니다.
검색 결과에서 특정 섹션으로 바로 들어가는 링크(sitelinks)가 잡힐 수 있고, 긴 글의 이탈도 줄어듭니다.

**4. 구조화 데이터**
- 개별 글: `Article`(wordCount·articleSection·about·isPartOf 포함) + `BreadcrumbList`
- 허브: `CollectionPage` + `ItemList` + `BreadcrumbList`
- 목록: `Blog` + `BreadcrumbList`

> FAQ 스키마는 넣지 않았습니다. 구글이 2023년 이후 일반 사이트의 FAQ 리치결과 노출을 크게 줄여, 내용에 맞지 않는 FAQ를 억지로 붙이는 쪽이 손해라고 판단했습니다.

**5. 크롤 유도**
- `sitemap.xml`에 `lastmod` 기입 — 갱신된 글부터 다시 수집됩니다
- 허브 우선순위 0.8, 개별 글 0.7, 목록 0.9
- RSS 피드 + `<link rel="alternate">`
- `robots` 메타에 `max-snippet:-1, max-image-preview:large` — 발췌·썸네일 제한 해제

**6. 이어 읽기 동선**
같은 주제 안에서 이전/다음 글을 `rel="prev"`·`rel="next"`로 연결하고, 하단에 관련 글 4편(같은 주제 3 + 다른 주제 1)을 둡니다.

**7. OG 카드**
글마다 제목·주제가 들어간 1200×630 이미지를 생성합니다. 카카오톡·페이스북 공유 시 클릭률에 직접 영향을 줍니다.

## OG 이미지 재생성

Pretendard OTF가 필요합니다(한글 렌더링).

```bash
mkdir -p /tmp/pf && cd /tmp/pf && npm init -y && npm i pretendard
PRETENDARD_DIR=/tmp/pf/node_modules/pretendard/dist/public/static \
  python3 /home/user/rfhomepage/tools/build_columns.py --og
```

폰트를 못 찾으면 OG 생성만 건너뛰고 나머지는 정상 진행됩니다(이미 커밋된 이미지는 유지).

## 주의

- **순위를 약속하는 문구는 원고에 넣지 마세요.** 신뢰도에도, 검색엔진 평가에도 해롭습니다.
- 지역 칼럼 10편은 지역명만 바꾼 복제글이 되지 않도록 각 지역 산업 특성을 축으로 씁니다. 현재 실측 유사도 8.5%로 안전 범위입니다.
- 새 글을 추가하면 `content/keywords-100.json`에도 slug·cluster를 등록해야 순서와 허브 분류가 잡힙니다.

---

## 배포 전 순서 (2026-09-25부터)

사이트는 이제 Tailwind CDN 대신 **미리 빌드한 CSS**를 씁니다. 무엇을 고쳤든 마지막에 `build_assets.py`를 꼭 돌리세요.

```bash
python3 tools/optimize_images.py --delete   # 사진을 새로 넣었을 때만
python3 tools/build_columns.py              # 칼럼을 고쳤을 때만
python3 tools/build_assets.py               # 항상 마지막 (node 필요)
git add -A && git commit && git push
# 배포가 끝난 뒤
python3 tools/indexnow.py --since YYYY-MM-DD   # 바뀐 페이지를 네이버·빙에 알림
```

- `build_assets.py`를 빼먹으면: 새로 쓴 Tailwind 클래스가 적용되지 않고, 고친 CSS가 재방문자에게 안 갑니다.
- 루트의 `d1ebd682684f953fad9c2a85b7c238bf.txt`는 IndexNow 키 파일입니다. 지우지 마세요.

## 칼럼 날짜 규칙

발행일·수정일은 **실제 날짜만** 씁니다. 원고 JSON의 git 최초 커밋일이 발행일, 마지막 커밋일이 수정일이 됩니다.
기존 배치 파일에 새 글을 추가할 때는 그 글에 `"published": "YYYY-MM-DD"`를 직접 적어주세요(안 적으면 배치 파일의 최초 커밋일이 붙습니다).

## AI 검색용 파일

- `llms.txt` — AI가 사이트를 요약해 읽는 파일. **가격·포함 항목·환불 규정·디자인 목록이 바뀌면 같이 고쳐야 합니다.**
- `robots.txt` — AI 크롤러 허용 목록과 Content-Signal. 학습만 막으려면 `ai-train=no`.
- FAQPage 구조화 데이터 — `build_assets.py`가 화면의 `<details class="faq">`에서 자동으로 만듭니다. 직접 고치지 마세요.

## 홈 첫 화면 쇼케이스 (레퍼런스 18종 · 모니터 + 휴대폰)

위 줄 모니터(데스크톱 화면), 아래 줄 휴대폰(모바일 화면)이 같은 디자인끼리 짝을 이뤄 함께 넘어갑니다. 펼치면 두 화면이 실제 사이트처럼 스크롤됩니다. HTML/CSS만 쓰고 3D 엔진은 쓰지 않습니다.

- 순서·이름·한 줄 소개·대표색: `content/showcase/designs.json`
- 템플릿 화면을 바꿨으면 다시 캡처: `python3 -m http.server 8799 &` → `node tools/capture_showcase.mjs [slug …]`
- 빌드: `python3 tools/build_showcase.py` → `python3 tools/build_assets.py`
- 노출 규칙: 세션당 1회 자동. 주소에 `#해시`가 있거나 데이터 절약 모드면 건너뜀. 스크립트가 4초 안에 안 뜨면 자동으로 걷힘. 홈 레퍼런스 구간 "18종 펼쳐 보기"로 다시 열림
- 분석 이벤트: `intro_view` · `intro_open` · `intro_visit` · `intro_exit`(method: how / skip)
