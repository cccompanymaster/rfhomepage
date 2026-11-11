#!/usr/bin/env python3
"""
차트 채우기 — content/charts.json 의 차트를 루트 페이지의 표시 자리에 다시 그립니다.

  python3 tools/build_charts.py      # build_columns.py 다음, build_assets.py 전에

페이지에 이렇게 자리를 두면 그 사이를 매번 새로 채웁니다.
  <!-- vz:price-compare dark -->  …  <!-- /vz:price-compare -->
테마: light(기본) / dark(다크 카드 안)
칼럼 본문은 build_columns.py 가 <!--vz:이름--> 자리표시를 같은 방식으로 채웁니다.
차트 숫자나 문구를 고칠 땐 charts.json 만 고치고 이 스크립트와 build_columns.py 를 돌리세요.
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import viz  # noqa: E402

BLOCK = re.compile(r'(?P<indent>[ \t]*)<!-- vz:(?P<name>[\w-]+)(?: (?P<theme>light|dark))? -->.*?<!-- /vz:(?P=name) -->', re.S)


def fill(s, specs):
    def rep(m):
        ind, name, theme = m.group('indent'), m.group('name'), m.group('theme') or 'light'
        chart = viz.render(name, theme, specs)
        body = '\n'.join(ind + line if line else line for line in chart.split('\n'))
        return f'{ind}<!-- vz:{name}{" " + theme if m.group("theme") else ""} -->\n{body}\n{ind}<!-- /vz:{name} -->'
    return BLOCK.subn(rep, s)


def main():
    specs = viz.load_specs()
    done = []
    for f in sorted(glob.glob(os.path.join(viz.ROOT, '*.html'))):
        s = open(f, encoding='utf-8').read()
        new, n = fill(s, specs)
        if n:
            if new != s:
                open(f, 'w', encoding='utf-8').write(new)
            done.append(f'{os.path.basename(f)} {n}개')
    print('✓ 차트 ' + (', '.join(done) if done else '자리 없음'))


if __name__ == '__main__':
    main()
