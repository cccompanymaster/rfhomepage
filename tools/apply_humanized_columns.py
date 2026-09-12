#!/usr/bin/env python3
"""
인간화된 칼럼 본문을 원고 JSON에 되돌린다.

  _workspace/col-NN/final.md  →  content/columns/batch-NN.json 의 body

실행:
  python3 tools/apply_humanized_columns.py           # 검증만 (dry-run)
  python3 tools/apply_humanized_columns.py --write   # 실제 반영

안전장치 — 하나라도 걸리면 그 배치는 통째로 건너뛴다:
  1) 편 수·slug·순서가 원본과 정확히 일치
  2) HTML 태그 균형 (열고 닫음)
  3) 원문에 있던 유의미한 수치가 전부 살아 있음
  4) 본문 길이가 원문의 55~160% 범위 (통째 날림·폭증 방지)
  5) 순위·효과 보장 표현이 새로 생기지 않음
"""
import json, glob, re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRITE = '--write' in sys.argv

PAIRED = ['h2', 'h3', 'p', 'ul', 'ol', 'li', 'table', 'thead', 'tbody',
          'tr', 'th', 'td', 'strong', 'em', 'code', 'blockquote']
# 새로 생기면 안 되는 표현 (허위·과장 광고 방지)
BANNED = ['순위를 보장', '상위노출을 보장', '1페이지 보장', '반드시 상위',
          '100% 보장', '무조건 상위', '효과를 보장']


def parse_final(path):
    """final.md → [(slug, body), ...]"""
    txt = open(path, encoding='utf-8').read()
    txt = re.split(r'<!--\s*HUMANIZE-SUMMARY\s*-->', txt)[0]
    parts = re.split(r'^===\s*\[([^\]]+)\]\s*([^=]+?)\s*===\s*$', txt, flags=re.M)
    out = []
    # parts = [before, idx1, slug1, body1, idx2, slug2, body2, ...]
    for i in range(1, len(parts) - 2, 3):
        slug = parts[i + 1].strip()
        body = parts[i + 2].strip()
        out.append((slug, body))
    return out


def tag_balance(html):
    bad = []
    for t in PAIRED:
        o = len(re.findall(r'<' + t + r'(?:\s[^>]*)?>', html))
        c = html.count(f'</{t}>')
        if o != c:
            bad.append(f'{t}({o}/{c})')
    return bad


def numbers(s):
    """의미 있는 수치만 — 천단위 구분 금액, 2자리 이상 숫자.
       '1, 2, 3' 같은 나열의 한 자리 숫자는 서술문으로 풀릴 수 있으므로 제외."""
    plain = re.sub(r'<[^>]+>', '', s)
    out = set(re.findall(r'\d{1,3}(?:,\d{3})+', plain))       # 1,000 / 199,000
    out |= {n for n in re.findall(r'(?<![\d,])\d{2,}(?![\d,])', plain)}  # 18 / 2026
    return out


def check(orig_arts, new_pairs, tag):
    """검증. 통과하면 None, 실패하면 사유 문자열"""
    if len(new_pairs) != len(orig_arts):
        return f'편 수 불일치 ({len(new_pairs)} vs {len(orig_arts)})'
    for (slug, body), a in zip(new_pairs, orig_arts):
        if slug != a['slug']:
            return f'slug 순서 어긋남 ({slug} vs {a["slug"]})'
        bad = tag_balance(body)
        if bad:
            return f'{slug}: 태그 불균형 {bad}'
        on, nn = numbers(a['body']), numbers(body)
        miss = on - nn
        if miss:
            return f'{slug}: 수치 유실 {sorted(miss)[:4]}'
        ol = len(re.sub(r'<[^>]+>', '', a['body']))
        nl = len(re.sub(r'<[^>]+>', '', body))
        if not (ol * 0.55 <= nl <= ol * 1.6):
            return f'{slug}: 분량 이상 ({ol}→{nl}자)'
        for b in BANNED:
            if b in body and b not in a['body']:
                return f'{slug}: 금칙 표현 신규 발생 "{b}"'
    return None


def main():
    total_ok = total_skip = 0
    changed_articles = 0
    for f in sorted(glob.glob(os.path.join(ROOT, 'content/columns/batch-*.json'))):
        tag = os.path.basename(f)[6:-5]          # '01'
        fin = os.path.join(ROOT, f'_workspace/col-{tag}/final.md')
        if not os.path.exists(fin):
            print(f'  batch-{tag}: final.md 없음 — 건너뜀')
            continue
        arts = json.load(open(f, encoding='utf-8'))
        pairs = parse_final(fin)
        err = check(arts, pairs, tag)
        if err:
            print(f'  batch-{tag}: ✗ {err}')
            total_skip += 1
            continue
        n_diff = sum(1 for (s, b), a in zip(pairs, arts) if b != a['body'])
        print(f'  batch-{tag}: ✓ {len(pairs)}편 검증 통과 · 본문 변경 {n_diff}편')
        total_ok += 1
        changed_articles += n_diff
        if WRITE:
            for (slug, body), a in zip(pairs, arts):
                a['body'] = body
            json.dump(arts, open(f, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=2)

    print(f'\n통과 {total_ok}배치 / 실패 {total_skip}배치 / 본문 바뀐 글 {changed_articles}편')
    if WRITE and total_ok:
        print('→ 원고 반영 완료. `python3 tools/build_columns.py` 로 페이지를 다시 생성하세요.')
    elif not WRITE:
        print('→ 검증만 수행했습니다. 반영하려면 --write 를 붙이세요.')


if __name__ == '__main__':
    main()
