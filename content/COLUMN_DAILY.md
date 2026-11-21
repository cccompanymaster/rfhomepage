# 칼럼 하루 2편 — 예약 작업 순서 (2026-11-19 시작)

매일 예약 작업이 이 문서대로 진행합니다. 대표님이 11/17에 정한 "하루 2편" 기준입니다.

## 순서

1. **최신 받기** — `git pull --ff-only origin claude/homepage-reference-designs-SXEMC`
   - 다른 작업의 미커밋 변경이 있으면 건드리지 않고, 아래 커밋에도 섞지 않습니다.
2. **주제 2개 고르기** — `content/column-queue.md`에서 위에서부터 `대기` 2줄.
   - 대기열이 비었으면 `content/backlog.md` A 항목(전용 페이지가 없는 질문)에서 고릅니다. 그것도 없으면 쓰지 말고 "새 주제가 필요하다"고 보고합니다.
   - 이미 있는 글(`content/keywords-100.json`의 kw·slug, 원고의 title·question)과 겹치면 건너뛰고 다음 줄로.
3. **사실 확인** — 수치·법·정책은 WebSearch로 **서로 다른 출처 두 곳 이상**에서 같은 내용이 확인될 때만 씁니다.
   - 이 작업 환경은 naver.com·law.go.kr·ftc.go.kr 직접 접속이 막혀 있습니다. 공식 문서를 읽지 못했으면 그 문서를 출처로 적지 않고, "자세한 기준은 네이버 공식 도움말에서 확인하세요"처럼 확인할 곳으로만 안내합니다.
   - 확인이 안 되는 숫자는 빼고, 숫자 없이도 쓸 수 있으면 그렇게 씁니다. 주제 자체가 확인 안 되는 숫자에 기대면 `보류: 이유`로 바꾸고 다음 주제로.
4. **쓰기** — `content/columns/batch-13.json`(목록)에 2편 추가. 기존 글 형식 그대로:
   `slug, kw, cluster("marketing" 등), readMin, title, desc, tags(3개), question, answer, body, published, updated`
   - `published`·`updated` = 오늘(한국 시간) — 날짜를 앞당기거나 미래로 쓰지 않음
   - `answer`: 첫 문단과 같은 내용의 직답, 150자 이하
   - `body`: 첫 문단에 바로 답 → h2 4~6개 → 표나 목록 1개 이상 → 마지막 문단 `<p class="note">이 글은 YYYY년 M월 기준 공개 자료로 정리한 일반 정보이며…</p>` → `<h2>참고한 자료</h2><ul class="refs">…</ul>` (실제로 읽은 글만, `rel="noopener" target="_blank"`)
   - 사이트 안 링크 2~3개(관련 칼럼 `/columns/<slug>`), 노아홈페이지 언급은 마지막 쪽에 한 번, 짧게
   - 합니다체. 번역투·과한 불릿·"다양한/결론적으로" 같은 AI 티 나는 표현 피하기
   - **금지**: 순위·노출·효과·매출 보장 표현, 리워드·트래픽·가짜 리뷰·가구매 권유, 실제 업체 이름 비방, 근거 없는 평균 금액·통계
   - 노아 가격·옵션을 쓰면 사이트와 똑같이: 기본 패키지 149,000원(부가세 별도), 유지보수 1년 200,000원(이미 만든 페이지의 이미지·텍스트 수정 + 팝업 배너), AI·구글 상위노출은 가격 문의, 명함 옵션 없음, 옵션 안내 링크는 `/pricing#options`
5. **등록** — `content/keywords-100.json`의 `keywords` 끝에 `{n: 다음 번호, kw, slug, cluster}` 추가
6. **만들기·점검**
   ```bash
   python3 tools/build_columns.py
   python3 tools/build_charts.py
   python3 tools/build_assets.py
   python3 tools/check_columns.py --since 2026-11-19
   ```
   - 점검이 실패하면 원고를 고쳐 다시 돌립니다. 끝내 통과하지 못하면 올리지 말고 이유를 보고합니다.
   - 칼럼 수(홈 "칼럼 N편")와 llms.txt 칼럼 구역은 `build_columns.py`가 자동으로 맞춥니다.
7. **대기열 표시** — `content/column-queue.md`에서 쓴 줄을 `발행 YYYY-MM-DD /columns/<slug>`로
8. **올리기** — 이 작업으로 바뀐 파일만 커밋:
   `content/columns/batch-13.json content/keywords-100.json content/column-queue.md columns/ sitemap.xml llms.txt index.html`
   (+ build_assets가 바꾼 캐시 버전만 있는 파일). 커밋 후 `git push -u origin claude/homepage-reference-designs-SXEMC`, 네트워크 오류면 2·4·8·16초 간격으로 최대 4번 재시도.
   - 푸시되면 Cloudflare가 배포하고 GitHub Actions의 IndexNow가 새 글을 검색엔진에 알립니다.
9. **보고** — 한국어로 짧게: 오늘 2편 제목과 주소(https://noahhomepage.co.kr/columns/<slug>), 확인한 주요 출처, 남은 대기 주제 수, 문제가 있었다면 그 내용.
