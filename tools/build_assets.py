#!/usr/bin/env python3
"""
CSS 빌드 + 캐시 버전 붙이기.  페이지·칼럼을 고친 뒤 마지막에 한 번 돌립니다.

  python3 tools/build_columns.py     # 칼럼을 고쳤다면 먼저
  python3 tools/build_assets.py      # 항상 마지막에

하는 일
  1) Tailwind 빌드  →  assets/css/tw.css
     (tailwind.config.js 가 모든 HTML을 훑어 실제로 쓰인 클래스만 담습니다.
      새 클래스를 썼는데 빌드를 안 돌리면 그 클래스는 적용되지 않습니다.)
  2) 모든 HTML의 <head> 정리
       cdn.tailwindcss.com 스크립트  →  /assets/css/tw.css
       jsdelivr Pretendard            →  /assets/fonts/pretendard/pretendard.css
       Google Fonts 쓰는 페이지에 preconnect 추가
  3) CSS·JS 링크 뒤에 내용 해시(?v=abcd1234)를 붙입니다.
     _headers 가 /assets/* 를 1년 캐시하므로, 파일 내용이 바뀌면
     주소도 바뀌어야 재방문자에게 새 파일이 갑니다.

필요한 것: node(npx). 처음 한 번 인터넷에서 tailwindcss@3.4.17 을 받아옵니다.
"""
import glob
import hashlib
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TW_VERSION = '3.4.17'
PAGES = ['*.html', 'templates/*.html', 'columns/*.html', 'columns/topic/*.html']

TW_SCRIPT = re.compile(r'<script src="https://cdn\.tailwindcss\.com"></script>')
PRETENDARD_CDN = re.compile(r'<link\s+rel="stylesheet"\s+href="https://cdn\.jsdelivr\.net/gh/orioncactus/pretendard@[^"]+"\s*/>')
GFONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/'
PRECONNECT = ('<link rel="preconnect" href="https://fonts.googleapis.com" />\n    '
              '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n    ')
# 버전을 붙일 자산: /assets/css/*.css, /assets/js/*.js, 폰트 CSS (상대경로 ./ ../ 포함)
ASSET_REF = re.compile(r'((?:\.\.?/|/)assets/(?:css|js|fonts/pretendard)/[\w.-]+\.(?:css|js))(?:\?v=[0-9a-f]+)?"')


def build_tailwind():
    local = os.path.join(ROOT, 'node_modules', '.bin', 'tailwindcss')
    cmd = [local] if os.path.exists(local) else [shutil.which('npx') or 'npx', '--yes', f'tailwindcss@{TW_VERSION}']
    cmd += ['-c', 'tailwind.config.js', '-i', 'assets/css/tw.src.css', '-o', 'assets/css/tw.css', '--minify']
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(os.path.join(ROOT, 'assets/css/tw.css')):
        sys.stderr.write(r.stderr or r.stdout)
        sys.exit('✗ Tailwind 빌드 실패 — node/npx 가 설치돼 있는지 확인하세요.')
    return os.path.getsize(os.path.join(ROOT, 'assets/css/tw.css'))


def short_hash(rel):
    with open(os.path.join(ROOT, rel.lstrip('/')), 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def main():
    size = build_tailwind()
    hashes = {}
    touched = 0
    for g in PAGES:
        for f in sorted(glob.glob(os.path.join(ROOT, g))):
            s = orig = open(f, encoding='utf-8').read()
            s = TW_SCRIPT.sub('<link rel="stylesheet" href="/assets/css/tw.css" />', s)
            s = PRETENDARD_CDN.sub('<link rel="stylesheet" href="/assets/fonts/pretendard/pretendard.css" />', s)
            if GFONTS in s and 'rel="preconnect" href="https://fonts.gstatic.com"' not in s:
                s = s.replace(GFONTS, PRECONNECT + GFONTS, 1)

            def ver(m):
                ref = m.group(1)
                key = re.sub(r'^(\.\.?/)+', '/', ref)
                if key not in hashes:
                    hashes[key] = short_hash(key)
                return f'{ref}?v={hashes[key]}"'
            s = ASSET_REF.sub(ver, s)
            if s != orig:
                open(f, 'w', encoding='utf-8').write(s)
                touched += 1

    left = [os.path.relpath(f, ROOT) for g in PAGES for f in glob.glob(os.path.join(ROOT, g))
            if 'cdn.tailwindcss.com' in open(f, encoding='utf-8').read()]
    print(f'✓ tw.css {size / 1024:.0f}KB')
    print(f'✓ HTML {touched}개 갱신 · 버전 붙은 자산 {len(hashes)}개')
    for k, v in sorted(hashes.items()):
        print(f'    {k}?v={v}')
    if left:
        print('! 아직 CDN을 쓰는 파일:', ', '.join(left))


if __name__ == '__main__':
    main()
