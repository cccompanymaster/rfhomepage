#!/usr/bin/env python3
"""
홈 첫 화면 책장(Bookshelf) 빌드 — 표지 아틀라스 + 우리 데이터로 바꾼 렌더러.

  python3 tools/build_bookshelf.py [--upstream /path/to/threeui]
  python3 tools/build_assets.py          # 그다음 항상

원본: ThreeUI Community (MIT) — src/shaders/bookshelf/bookshelfRenderer.js
      https://github.com/MengTo/threeui   (Three.js r165)

원본에서 바꾸는 것은 아래 다섯 가지뿐입니다. 렌더러의 장면·조명·책 리그·페이지·
드래그·궤도·접근성·정리(dispose) 코드는 한 줄도 바꾸지 않습니다.
  1) BOOKS          원본 7권(개발 도구 책) → content/bookshelf/books.json 의 우리 레퍼런스
  2) COVER_CROPS    권수에 맞춰 512×768 칸 다시 계산
  3) COVER_ATLAS    내장 base64 표지 → /assets/bookshelf/covers.webp (이 스크립트가 생성)
  4) 컬렉션 이름     "WORKING VOLUMES" → books.json 의 collectionLabel
  5) import 경로     "three165" 별칭 → 자체 호스팅 ./three.module.min.js

입력
  content/bookshelf/books.json         책 데이터 (renderer 필드 + site 필드)
  content/bookshelf/screens/<slug>.png 표지에 들어갈 템플릿 모바일 화면 (780×1688 권장)
출력
  assets/bookshelf/covers.webp          표지 아틀라스 (권수 × 512, 768)
  assets/bookshelf/bookshelf-renderer.js
  assets/bookshelf/books-site.js        캡션·버튼용 데이터 (한글 이름, 링크)
"""
import hashlib
import json
import os
import random
import re
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'bookshelf')
DATA = os.path.join(ROOT, 'content', 'bookshelf', 'books.json')
SCREENS = os.path.join(ROOT, 'content', 'bookshelf', 'screens')
CELL_W, CELL_H = 512, 768
SS = 2  # 2배로 그린 뒤 줄여서 가장자리를 부드럽게


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def cloth(color, seed, w, h):
    """책 천 질감: 바탕색 + 미세 그레인 + 가로세로 올 + 가장자리 음영."""
    rnd = random.Random(seed)
    base = Image.new('RGB', (w, h), hex_rgb(color))
    grain = Image.effect_noise((w, h), 26).convert('L').filter(ImageFilter.GaussianBlur(0.6))
    weave = Image.new('L', (w, h), 128)
    d = ImageDraw.Draw(weave)
    for y in range(0, h, 3):
        d.line([(0, y), (w, y)], fill=128 + rnd.randint(-10, 10), width=1)
    for x in range(0, w, 3):
        d.line([(x, 0), (x, h)], fill=128 + rnd.randint(-8, 8), width=1)
    tex = ImageChops.add(grain, weave, scale=2.0)          # 128 근처 = 변화 없음
    dark = luminance(hex_rgb(color)) < 90
    amt = 0.10 if dark else 0.07
    over = Image.merge('RGB', [tex] * 3)
    out = Image.blend(base, ImageChops.overlay(base, over), amt * 4)
    # 가장자리를 살짝 어둡게 (원본 표지와 같은 비네트)
    vig = Image.new('L', (w, h), 0)
    ImageDraw.Draw(vig).rectangle([w * 0.06, h * 0.05, w * 0.94, h * 0.95], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(w * 0.08))
    shade = Image.new('RGB', (w, h), (0, 0, 0))
    return Image.composite(out, Image.blend(out, shade, 0.22), vig)


def rounded_mask(size, radius):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def cover(book, screen_path):
    r = book['renderer']
    w, h = CELL_W * SS, CELL_H * SS
    img = cloth(r['color'], r['seed'], w, h).convert('RGBA')

    # 휴대폰 목업 — 금박 제목(아래 약 640~720px)과 위 라벨(약 47px) 자리를 비워 둡니다
    ph_w = int(232 * SS)
    screen = Image.open(screen_path).convert('RGB')
    bezel = int(9 * SS)
    sc_w = ph_w - bezel * 2
    sc_h = int(sc_w * 2.05)
    ph_h = sc_h + bezel * 2
    x0 = (w - ph_w) // 2
    y0 = int(96 * SS)
    status_h = int(30 * SS)   # 상태 표시줄 — 카메라 섬이 사이트 로고를 가리지 않게
    page = screen.resize((sc_w, int(screen.height * sc_w / screen.width)), Image.LANCZOS)
    shot = Image.new('RGB', (sc_w, sc_h), page.getpixel((2, 2)))
    shot.paste(page.crop((0, 0, sc_w, sc_h - status_h)), (0, status_h))

    # 그림자
    sh = Image.new('L', (w, h), 0)
    ImageDraw.Draw(sh).rounded_rectangle([x0 + 6 * SS, y0 + 16 * SS, x0 + ph_w + 6 * SS, y0 + ph_h + 16 * SS], radius=34 * SS, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(18 * SS))
    img = Image.composite(Image.new('RGBA', (w, h), (0, 0, 0, 255)), img, sh.point(lambda v: int(v * 0.55)))

    # 본체 + 화면
    body = Image.new('RGBA', (ph_w, ph_h), (18, 18, 20, 255))
    hl = ImageDraw.Draw(body)
    hl.rounded_rectangle([1, 1, ph_w - 2, ph_h - 2], radius=32 * SS, outline=(70, 70, 76, 255), width=max(1, SS))
    body.paste(shot, (bezel, bezel), rounded_mask((sc_w, sc_h), 24 * SS))
    # 다이내믹 아일랜드
    isl_w, isl_h = int(64 * SS), int(18 * SS)
    ImageDraw.Draw(body).rounded_rectangle([(ph_w - isl_w) // 2, bezel + 6 * SS, (ph_w + isl_w) // 2, bezel + 6 * SS + isl_h], radius=isl_h // 2, fill=(8, 8, 9, 255))
    img.paste(body, (x0, y0), rounded_mask((ph_w, ph_h), 34 * SS))

    # 유리 반사
    gl = Image.new('L', (ph_w, ph_h), 0)
    ImageDraw.Draw(gl).polygon([(0, 0), (int(ph_w * 0.55), 0), (int(ph_w * 0.15), ph_h), (0, ph_h)], fill=22)
    gl = ImageChops.multiply(gl, rounded_mask((ph_w, ph_h), 34 * SS))
    img.paste(Image.new('RGBA', (ph_w, ph_h), (255, 255, 255, 255)), (x0, y0), gl)

    return img.convert('RGB').resize((CELL_W, CELL_H), Image.LANCZOS)


def js_value(obj, indent=6):
    """원본 BOOKS 와 같은 모양의 JS 객체 리터럴 (키에 따옴표 없음)."""
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    text = re.sub(r'^(\s*)"([A-Za-z_][A-Za-z0-9_]*)":', r'\1\2:', text, flags=re.M)
    pad = ' ' * indent
    return text.replace('\n', '\n' + pad)


def main():
    up_root = os.environ.get('THREEUI_DIR', '/home/user/mengto/threeui')
    if '--upstream' in sys.argv:
        up_root = sys.argv[sys.argv.index('--upstream') + 1]
    upstream = os.path.join(up_root, 'src', 'shaders', 'bookshelf', 'bookshelfRenderer.js')
    if not os.path.exists(upstream):
        sys.exit(f'✗ 원본 렌더러가 없습니다: {upstream}\n'
                 '  git clone https://github.com/MengTo/threeui 후 --upstream 으로 경로를 주세요.')

    data = json.load(open(DATA, encoding='utf-8'))
    books = data['books']
    os.makedirs(OUT, exist_ok=True)

    # 1) 표지 아틀라스
    atlas = Image.new('RGB', (CELL_W * len(books), CELL_H))
    for i, b in enumerate(books):
        shot = os.path.join(SCREENS, b['site']['slug'] + '.png')
        if not os.path.exists(shot):
            sys.exit(f'✗ 표지 화면이 없습니다: {shot}')
        atlas.paste(cover(b, shot), (i * CELL_W, 0))
    atlas_path = os.path.join(OUT, 'covers.webp')
    atlas.save(atlas_path, 'WEBP', quality=88, method=6)
    atlas_hash = hashlib.sha1(open(atlas_path, 'rb').read()).hexdigest()[:8]

    # 2) 렌더러 패치
    src = open(upstream, encoding='utf-8').read()
    up_sha = hashlib.sha256(src.encode('utf-8')).hexdigest()
    s = src

    def sub_once(pattern, repl, text, flags=0, count=1, what=''):
        new, n = re.subn(pattern, repl, text, count=count, flags=flags)
        if n == 0:
            sys.exit(f'✗ 원본 구조가 예상과 다릅니다 ({what}) — 원본 버전을 확인하세요.')
        return new

    s = sub_once(r'from "three165";', 'from "./three.module.min.js";', s, what='three import')
    s, n_add = re.subn(r'from "\./three165/([A-Za-z]+\.js)";', r'from "./\1";', s)
    if n_add != 4:
        sys.exit(f'✗ 애드온 import 4개를 찾지 못했습니다 ({n_add})')

    records = [b['renderer'] for b in books]
    s = sub_once(r'const BOOKS = \[.*?\n    \];', lambda m: 'const BOOKS = ' + js_value(records, 4) + ';', s, flags=re.S, what='BOOKS')
    crops = ',\n'.join(f'      [{i * CELL_W}, 0, {CELL_W}, {CELL_H}]' for i in range(len(books)))
    s = sub_once(r'const COVER_CROPS = \[.*?\n    \];', lambda m: f'const COVER_CROPS = [\n{crops}\n    ];', s, flags=re.S, what='COVER_CROPS')
    s = sub_once(r'const COVER_ATLAS_DATA = "data:image/webp;base64,[^"]+";',
                 f'const COVER_ATLAS_DATA = "/assets/bookshelf/covers.webp?v={atlas_hash}";', s, what='COVER_ATLAS')
    label = data.get('collectionLabel', 'NOAH REFERENCES')
    s, n_label = re.subn(r'WORKING VOLUMES', label, s)

    header = (f'/* NOAH 홈 책장 — ThreeUI Bookshelf (MIT, github.com/MengTo/threeui) 기반.\n'
              f' * tools/build_bookshelf.py 가 생성합니다. 직접 고치지 마세요.\n'
              f' * 원본 bookshelfRenderer.js SHA-256: {up_sha}\n'
              f' * 바꾼 것: BOOKS({len(books)}권) · COVER_CROPS · COVER_ATLAS(외부 webp) · '
              f'컬렉션 이름 {n_label}곳 · import 경로. 렌더러 동작 코드는 원본 그대로. */\n')
    open(os.path.join(OUT, 'bookshelf-renderer.js'), 'w', encoding='utf-8').write(header + s)

    # 3) 캡션·버튼용 데이터
    site = [dict(b['site'], title=b['renderer']['title'], discipline=b['renderer']['discipline'],
                 roman=b['renderer']['roman'], url=f"/templates/{b['site']['slug']}",
                 ink=b['renderer']['palette']['ink'], inkSoft=b['renderer']['palette']['inkSoft'],
                 wall=b['renderer']['palette']['wall']) for b in books]
    open(os.path.join(OUT, 'books-site.js'), 'w', encoding='utf-8').write(
        '/* tools/build_bookshelf.py 가 생성 — content/bookshelf/books.json 을 고치세요 */\n'
        'export const SITE_BOOKS = ' + json.dumps(site, ensure_ascii=False, indent=2) + ';\n')

    # intro.js 가 불러오는 데이터 주소에 해시 — /assets/* 1년 캐시라 바뀐 데이터가 바로 가게
    site_hash = hashlib.sha1(open(os.path.join(OUT, 'books-site.js'), 'rb').read()).hexdigest()[:8]
    intro = os.path.join(OUT, 'intro.js')
    if os.path.exists(intro):
        t = open(intro, encoding='utf-8').read()
        t2 = re.sub(r"from '\./books-site\.js(?:\?v=[0-9a-f]+)?'", f"from './books-site.js?v={site_hash}'", t)
        if t2 != t:
            open(intro, 'w', encoding='utf-8').write(t2)

    kb = lambda p: os.path.getsize(os.path.join(OUT, p)) / 1024
    print(f'✓ 표지 아틀라스 {len(books)}권  {atlas.size[0]}×{atlas.size[1]}  {kb("covers.webp"):.0f}KB')
    print(f'✓ 렌더러 {kb("bookshelf-renderer.js"):.0f}KB (원본 {len(src) / 1024:.0f}KB) · 컬렉션 이름 {n_label}곳 교체')
    print(f'✓ 캡션 데이터 books-site.js')


if __name__ == '__main__':
    main()
