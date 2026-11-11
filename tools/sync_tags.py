#!/usr/bin/env python3
"""assets/js/tags.js의 TAG_IDS에 맞춰 세 가지를 같이 고칩니다.

  1) _headers 의 Content-Security-Policy — 켜진 도구의 주소만 허용
  2) privacy.html 8항 — 켜진 광고 도구 목록과 맞춤형 광고 안내 (<!-- tags:start --> … <!-- tags:end -->)
  3) 모든 HTML의 /assets/js/tags.js?v=… — 파일 내용 해시 (assets 는 1년 캐시라 주소가 바뀌어야 새 ID가 퍼짐)

    python3 tools/sync_tags.py          고치기
    python3 tools/sync_tags.py --check  어긋나면 1로 끝남 (주간 'SEO 측정' 워크플로가 실행)
"""
import glob
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGS = os.path.join(ROOT, 'assets', 'js', 'tags.js')
HEADERS = os.path.join(ROOT, '_headers')
PRIVACY = os.path.join(ROOT, 'privacy.html')

TOOLS = {
    'naver': {'script-src': ['https://wcs.naver.net'], 'connect-src': ['https://wcs.naver.com'],
              'row': ('네이버 주식회사 (검색광고 프리미엄 로그분석·네이버 애널리틱스)', '네이버 검색·광고 유입 통계, 광고 전환 측정'), 'ad': True},
    'meta': {'script-src': ['https://connect.facebook.net'], 'connect-src': ['https://www.facebook.com', 'https://connect.facebook.net'],
             'row': ('Meta Platforms, Inc. (Meta 픽셀)', '페이스북·인스타그램 광고 전환 측정과 맞춤형 광고'), 'ad': True},
    'kakao': {'script-src': ['https://t1.daumcdn.net', 'https://t1.kakaocdn.net'], 'connect-src': ['https://*.ds.kakao.com'],
              'row': ('주식회사 카카오 (카카오 픽셀)', '카카오 광고 전환 측정과 맞춤형 광고'), 'ad': True},
    'karrot': {'script-src': ['https://karrot-pixel.business.daangn.com'], 'connect-src': ['https://collect.daangn.com'],
               'row': ('당근마켓 주식회사 (당근 픽셀)', '당근 광고 전환 측정과 맞춤형 광고'), 'ad': True},
    # Clarity 는 8항 본문에 이미 고지되어 있어 표에 넣지 않음
    'clarity': {'script-src': ['https://www.clarity.ms', 'https://*.clarity.ms'], 'connect-src': ['https://*.clarity.ms', 'https://c.bing.com'],
                'row': None, 'ad': False},
}
DIRECTIVES = ('script-src', 'connect-src')  # img-src 는 이미 https: 전체 허용
MANAGED = {o for t in TOOLS.values() for d in DIRECTIVES for o in t[d]}
START, END = '<!-- tags:start -->', '<!-- tags:end -->'
TAGS_REF = re.compile(r'/assets/js/tags\.js(?:\?v=[0-9a-f]+)?"')


def read_ids():
    block = re.search(r'var TAG_IDS = \{(.*?)\};', open(TAGS, encoding='utf-8').read(), re.S)
    if not block:
        sys.exit('assets/js/tags.js: TAG_IDS 블록을 찾지 못했습니다')
    ids = {k: v.strip() for k, v in re.findall(r"(\w+):\s*'([^']*)'", block.group(1))}
    if set(ids) - set(TOOLS):
        sys.exit(f'assets/js/tags.js: 모르는 도구 {sorted(set(ids) - set(TOOLS))}')
    return ids


def fix_csp(csp, on):
    out = []
    for part in [p.strip() for p in csp.split(';') if p.strip()]:
        name, *values = part.split()
        if name in DIRECTIVES:
            values = [v for v in values if v not in MANAGED]
            for key in on:
                values += [o for o in TOOLS[key][name] if o not in values]
        out.append(' '.join([name, *values]))
    return '; '.join(out)


def privacy_block(on):
    ads = [k for k in on if TOOLS[k]['ad']]
    if not ads:
        return f'{START}{END}'
    rows = '\n'.join(f'            <tr><td>{TOOLS[k]["row"][0]}</td><td>{TOOLS[k]["row"][1]}</td></tr>' for k in ads)
    return f'''{START}
        <p>광고를 보고 들어온 방문자가 상담·주문을 했는지 확인하고 관심 있을 만한 광고를 보여 주기 위해(맞춤형 광고) 아래 광고 도구가 쿠키 등으로 방문 페이지·기기 정보 같은 이용 기록(행태정보)을 수집합니다. 신청서·주문서에 입력한 이름·연락처·내용은 보내지 않습니다.</p>
        <table>
          <thead><tr><th>사업자 (도구)</th><th>목적</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
        <p>행태정보는 각 광고 사업자가 정한 기간(대개 2년 이내) 동안 보관하며, 브라우저에서 쿠키를 거부하거나 휴대폰 설정에서 광고 식별자를 재설정·제한하면 맞춤형 광고를 거부할 수 있습니다.</p>
        {END}'''


def render():
    ids = read_ids()
    on = [k for k in TOOLS if ids.get(k)]
    out = {}
    h = open(HEADERS, encoding='utf-8').read()
    nh = re.sub(r'^(\s*Content-Security-Policy:\s*)(.*)$', lambda m: m.group(1) + fix_csp(m.group(2), on), h, count=1, flags=re.M)
    if nh != h:
        out[HEADERS] = nh
    p = open(PRIVACY, encoding='utf-8').read()
    if START not in p:
        sys.exit('privacy.html: <!-- tags:start --> 표시를 찾지 못했습니다')
    np_ = p[:p.index(START)] + privacy_block(on) + p[p.index(END) + len(END):]
    version = hashlib.sha1(open(TAGS, 'rb').read()).hexdigest()[:8]
    for path in [f for f in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True) if '/.git/' not in f]:
        text = out.get(path) or (np_ if path == PRIVACY else open(path, encoding='utf-8').read())
        new = TAGS_REF.sub(f'/assets/js/tags.js?v={version}"', text)
        if path == PRIVACY:
            new = new if new != p else None
        elif new == text:
            new = None
        if new is not None:
            out[path] = new
    return out


def main():
    changes = render()
    names = sorted(os.path.relpath(p, ROOT) for p in changes)
    if '--check' in sys.argv:
        if changes:
            sys.exit(f'assets/js/tags.js와 어긋남 ({len(names)}개 파일, 예: {", ".join(names[:3])}) — python3 tools/sync_tags.py 실행')
        print('tags: CSP·개인정보처리방침·캐시 버전이 assets/js/tags.js와 일치')
        return
    for path, text in changes.items():
        open(path, 'w', encoding='utf-8').write(text)
    print(f'tags: {len(names)}개 파일 갱신' if names else 'tags: 이미 최신')


if __name__ == '__main__':
    main()
