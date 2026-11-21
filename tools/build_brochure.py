#!/usr/bin/env python3
"""
소개서 PDF 만들기 — content/brochure/brochure.html → assets/brochure/NOAH-brochure.pdf

  python3 tools/build_brochure.py

- 가격·옵션·문구를 바꿀 때는 content/brochure/brochure.html 을 고치고 이 스크립트를 다시 돌립니다.
- '홈페이지 제작, 보통 얼마 드나요?' 차트는 content/charts.json(price-compare)에서 자동으로 채웁니다.
- 필요한 것: node + playwright(Chromium). 사이트 /brochure·/소개서 주소와 소개서 받기 버튼이 이 PDF를 내려줍니다.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import viz  # noqa: E402
from build_charts import fill  # noqa: E402

ROOT = viz.ROOT
SRC = os.path.join(ROOT, 'content', 'brochure', 'brochure.html')
TMP = os.path.join(ROOT, 'content', 'brochure', '_print.html')   # 같은 폴더에 둬야 글꼴·CSS 상대 경로가 맞음
OUT = os.path.join(ROOT, 'assets', 'brochure', 'NOAH-brochure.pdf')


def main():
    s = open(SRC, encoding='utf-8').read()
    s, n = fill(s, viz.load_specs())
    open(TMP, 'w', encoding='utf-8').write(s)
    try:
        r = subprocess.run(['node', os.path.join(ROOT, 'tools', 'print_pdf.mjs'), TMP, OUT], cwd=ROOT)
        if r.returncode:
            sys.exit('✗ PDF 만들기 실패')
    finally:
        os.remove(TMP)
    print(f'✓ 소개서 — 차트 {n}개 포함, {os.path.getsize(OUT) // 1024}KB')


if __name__ == '__main__':
    main()
