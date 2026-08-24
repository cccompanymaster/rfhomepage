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
