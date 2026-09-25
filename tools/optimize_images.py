#!/usr/bin/env python3
"""
사진을 WebP로 바꾸고, 사이트 안의 참조(.jpg/.png → .webp)를 같이 고친다.

  python3 tools/optimize_images.py            # 변환 + 참조 교체 (원본 JPG는 남김)
  python3 tools/optimize_images.py --delete   # 위와 같고, 변환이 끝난 원본은 지움

새 사진을 올릴 때:
  1) assets/images/<업종>/ 에 JPG·PNG 그대로 넣고
  2) 이 스크립트를 한 번 돌리면 됩니다.
     같은 이름의 WebP가 있으면 덮어쓰므로, 사진 교체도 똑같이 하면 됩니다.

건드리지 않는 것:
  - og-cover.jpg          카카오톡·페이스북 미리보기 호환을 위해 JPG 유지
  - assets/images/og/     칼럼 OG 이미지(PNG)는 build_columns.py 가 관리
  - assets/images/previews/  이미 WebP
"""
import glob
import os
import re
import sys

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'assets', 'images')
MAX_W = 1600          # 템플릿에서 가장 넓게 쓰는 폭(풀블리드 히어로) 기준
QUALITY = 78
SKIP_NAMES = {'og-cover.jpg'}
SKIP_DIRS = {'og', 'previews'}
# 참조를 찾아 고칠 파일
TARGETS = ['*.html', 'templates/*.html', 'assets/js/*.js']


def sources():
    for p in sorted(glob.glob(os.path.join(IMG, '**', '*'), recursive=True)):
        rel = os.path.relpath(p, IMG)
        if not re.search(r'\.(jpe?g|png)$', p, re.I):
            continue
        if os.path.basename(p) in SKIP_NAMES or rel.split(os.sep)[0] in SKIP_DIRS:
            continue
        yield p, rel


def convert(src):
    dst = re.sub(r'\.(jpe?g|png)$', '.webp', src, flags=re.I)
    im = ImageOps.exif_transpose(Image.open(src))
    if im.mode not in ('RGB', 'RGBA'):
        im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=QUALITY, method=6)
    return dst


def main():
    delete = '--delete' in sys.argv
    done = []
    before = after = 0
    for src, rel in sources():
        dst = convert(src)
        before += os.path.getsize(src)
        after += os.path.getsize(dst)
        done.append((src, rel.replace(os.sep, '/')))

    if not done:
        print('변환할 사진이 없습니다.')
        return

    # 참조 교체: "<업종>/<파일>.jpg" 형태로 쓰인 모든 곳 (HTML 속성, JS 문자열 모두)
    names = sorted({rel for _, rel in done}, key=len, reverse=True)
    pat = re.compile('(' + '|'.join(re.escape(re.sub(r'\.(jpe?g|png)$', '', n, flags=re.I)) for n in names) + r')\.(?:jpe?g|png)\b', re.I)
    changed = 0
    for g in TARGETS:
        for f in glob.glob(os.path.join(ROOT, g)):
            s = open(f, encoding='utf-8').read()
            s2, n = pat.subn(r'\1.webp', s)
            if n:
                open(f, 'w', encoding='utf-8').write(s2)
                changed += n

    if delete:
        for src, _ in done:
            os.remove(src)

    print(f'✓ {len(done)}장 변환  {before / 1e6:.1f}MB → {after / 1e6:.1f}MB '
          f'({100 - after * 100 / before:.0f}% 감소)')
    print(f'✓ 참조 {changed}곳 교체' + ('  · 원본 삭제' if delete else '  · 원본 유지 (--delete 로 정리)'))


if __name__ == '__main__':
    main()
