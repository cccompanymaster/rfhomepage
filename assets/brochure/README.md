# NOAH 소개서 PDF

`NOAH-brochure.pdf` — 사이트의 "소개서 받기", `/brochure`, `/소개서` 주소가 이 파일을 내려줍니다.

## 고치는 법 (2026-11-21부터)

원본은 `content/brochure/brochure.html` 입니다. 가격·옵션·문구를 바꾸면 원본을 고친 뒤:

```bash
python3 tools/build_brochure.py      # → assets/brochure/NOAH-brochure.pdf (10쪽, 16:9)
```

- "홈페이지 제작, 보통 얼마 드나요?" 차트는 `content/charts.json`(price-compare)에서 자동으로 들어갑니다.
- node + playwright(Chromium)가 필요합니다.
- 파일 이름은 그대로 둡니다. `_headers`가 소개서 PDF를 1시간만 캐시하므로 같은 이름으로 덮어써도 금방 바뀝니다.
