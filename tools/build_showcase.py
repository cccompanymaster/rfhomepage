#!/usr/bin/env python3
"""
홈 첫 화면 기기 목업 쇼케이스 빌드 (위: 모니터 줄, 아래: 휴대폰 줄).

  node tools/capture_showcase.mjs     # 템플릿 화면 캡처 → content/showcase/screens/ (화면을 바꿨을 때만)
  python3 tools/build_showcase.py     # → assets/showcase/*.webp + showcase-data.js
  python3 tools/build_assets.py       # 항상 마지막

입력  content/showcase/designs.json   순서·이름·업종·한 줄 소개·대표색
      content/showcase/screens/<slug>-{desktop,desktop-tall,mobile,mobile-tall}.png
출력  assets/showcase/<slug>-d.webp   모니터 첫 화면      1120×700
      assets/showcase/<slug>-dt.webp  모니터 스크롤 화면  1120×(최대 2100)
      assets/showcase/<slug>-m.webp   휴대폰 첫 화면      440×952
      assets/showcase/<slug>-mt.webp  휴대폰 스크롤 화면  440×(최대 2860)
      assets/showcase/showcase-data.js
"""
import hashlib
import json
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'content', 'showcase')
OUT = os.path.join(ROOT, 'assets', 'showcase')

VIEWS = [  # (캡처 이름, 출력 접미사, 출력 폭, 품질)
    ('desktop', 'd', 1120, 80),
    ('desktop-tall', 'dt', 1120, 72),
    ('mobile', 'm', 440, 80),
    ('mobile-tall', 'mt', 440, 72),
]


def main():
    designs = json.load(open(os.path.join(SRC, 'designs.json'), encoding='utf-8'))['designs']
    os.makedirs(OUT, exist_ok=True)
    total = 0
    items = []
    for d in designs:
        item = {k: d[k] for k in ('slug', 'nameKo', 'industryKo', 'tagKo', 'accent')}
        item['url'] = f"/templates/{d['slug']}"
        for cap, suf, width, q in VIEWS:
            src = os.path.join(SRC, 'screens', f"{d['slug']}-{cap}.png")
            if not os.path.exists(src):
                sys.exit(f'✗ 캡처가 없습니다: {src}  (node tools/capture_showcase.mjs {d["slug"]})')
            im = Image.open(src).convert('RGB')
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            dst = os.path.join(OUT, f"{d['slug']}-{suf}.webp")
            im.save(dst, 'WEBP', quality=q, method=6)
            total += os.path.getsize(dst)
            h = hashlib.sha1(open(dst, 'rb').read()).hexdigest()[:8]
            item[suf] = f"/assets/showcase/{d['slug']}-{suf}.webp?v={h}"
            if suf in ('dt', 'mt'):
                item[suf + 'Ratio'] = round(im.height / im.width, 4)   # 스크롤 길이 계산용
        items.append(item)

    with open(os.path.join(OUT, 'showcase-data.js'), 'w', encoding='utf-8') as f:
        f.write('/* tools/build_showcase.py 가 생성 — content/showcase/designs.json 을 고치세요 */\n')
        f.write('export const DESIGNS = ' + json.dumps(items, ensure_ascii=False, indent=2) + ';\n')

    # intro.js 가 불러오는 데이터 주소에 해시 (/assets/* 1년 캐시)
    data_hash = hashlib.sha1(open(os.path.join(OUT, 'showcase-data.js'), 'rb').read()).hexdigest()[:8]
    intro = os.path.join(OUT, 'intro.js')
    if os.path.exists(intro):
        import re
        t = open(intro, encoding='utf-8').read()
        t2 = re.sub(r"from '\./showcase-data\.js(?:\?v=[0-9a-f]+)?'", f"from './showcase-data.js?v={data_hash}'", t)
        if t2 != t:
            open(intro, 'w', encoding='utf-8').write(t2)

    print(f'✓ {len(items)}종 × 4장 WebP  합계 {total / 1e6:.1f}MB (한 번에 다 받지 않음 — 보이는 것부터)')
    print('✓ showcase-data.js')


if __name__ == '__main__':
    main()
