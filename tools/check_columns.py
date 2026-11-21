#!/usr/bin/env python3
"""
칼럼 발행 전 점검 — 하나라도 걸리면 1로 끝나고, 그 상태로는 올리지 않습니다.

  python3 tools/check_columns.py            # 원고 + 만들어진 페이지 점검
  python3 tools/check_columns.py --since 2026-11-19   # 이 날짜 이후 발행분은 새 글 기준(더 엄격)으로

원고(content/columns/batch-*.json)
  - 필수 칸, slug 형식, slug·제목·질문 중복, keywords-100.json 등록 여부, 주제(cluster) 이름
  - 날짜 형식, 발행일이 오늘(한국 시간)보다 뒤가 아님
  - 본문: <h1> 없음, 태그 짝 맞음, 본문 속 /columns/… 링크가 실제 글
  - 새 글: 한 줄 답 150자 이하, 소제목(h2) 3개 이상, 표나 목록 1개 이상, 출처 링크 1개 이상,
          순위·효과 보장 표현 없음, 기본 패키지 금액은 149,000원만
페이지(columns/**/*.html)
  - 사이트 안 링크가 실제 파일로 이어짐, 구조화 데이터(JSON-LD)가 읽힘
"""
import glob
import html.parser
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_columns import CLUSTERS  # noqa: E402

TODAY = (datetime.now(timezone.utc) + timedelta(hours=9)).strftime('%Y-%m-%d')
REQ = ['slug', 'kw', 'cluster', 'title', 'desc', 'tags', 'question', 'answer', 'body', 'published', 'updated']
GUARANTEE = re.compile(r'(상위\s*노출\s*(을|이)?\s*보장|순위\s*(를|을)?\s*보장|1위\s*보장|노출\s*보장|효과\s*(를|을)?\s*보장|매출\s*(을|이)?\s*보장|무조건\s*(1위|상위)|100%\s*(노출|상위|효과))')
VOID = {'br', 'hr', 'img', 'input', 'meta', 'link', 'wbr', 'col', 'source'}

errors, warns = [], []


class Balance(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.bad = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.bad.append(tag)


def page_exists(href):
    path = href.split('#')[0].split('?')[0]
    if not path or path == '/':
        return True
    rel = path.lstrip('/')
    cands = [rel, rel + '.html', os.path.join(rel, 'index.html'), rel.rstrip('/') + '.html']
    return any(os.path.isfile(os.path.join(ROOT, c)) for c in cands)


def check_drafts(since):
    order = json.load(open(os.path.join(ROOT, 'content/keywords-100.json'), encoding='utf-8'))['keywords']
    reg = {k['slug'] for k in order}
    seen_slug, seen_title, seen_q, all_slugs, items = {}, {}, {}, set(), []
    for f in sorted(glob.glob(os.path.join(ROOT, 'content/columns/batch-*.json'))):
        for a in json.load(open(f, encoding='utf-8')):
            items.append((os.path.basename(f), a))
            all_slugs.add(a.get('slug'))
    for fn, a in items:
        sl = a.get('slug', '?')
        where = f'{fn}:{sl}'
        new = bool(since) and (a.get('published') or '') >= since
        for k in REQ:
            if not a.get(k):
                (errors if new else warns).append(f'{where} — "{k}" 칸이 비었음')
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', sl):
            errors.append(f'{where} — slug는 영문 소문자·숫자·하이픈만')
        for key, seen, label in [(sl, seen_slug, 'slug'), (a.get('title'), seen_title, '제목'), (a.get('question'), seen_q, '질문')]:
            if key and key in seen:
                errors.append(f'{where} — {label} 중복 ({seen[key]})')
            elif key:
                seen[key] = where
        if sl not in reg:
            errors.append(f'{where} — content/keywords-100.json에 등록 안 됨')
        if a.get('cluster') not in CLUSTERS:
            errors.append(f'{where} — 주제(cluster) "{a.get("cluster")}"가 build_columns.py CLUSTERS에 없음')
        for k in ('published', 'updated'):
            v = a.get(k) or ''
            if v and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', v):
                errors.append(f'{where} — {k} 날짜 형식(YYYY-MM-DD) 아님')
        if (a.get('published') or '') > TODAY:
            errors.append(f'{where} — 발행일 {a.get("published")}이 오늘({TODAY})보다 뒤')
        body = a.get('body') or ''
        if '<h1' in body:
            errors.append(f'{where} — 본문에 <h1> 금지 (제목은 페이지가 붙임)')
        p = Balance()
        p.feed(body)
        if p.stack or p.bad:
            errors.append(f'{where} — 태그 짝이 안 맞음 (열림 {p.stack[-3:]}, 엉킨 닫힘 {p.bad[:3]})')
        for m in re.findall(r'href="/columns/([a-z0-9-]+)"', body):
            if m not in all_slugs:
                errors.append(f'{where} — 본문 링크 /columns/{m} 글이 없음')
        for m in re.findall(r'href="(/[^"#?]*)', body):
            if not m.startswith('/columns/') and not page_exists(m):
                errors.append(f'{where} — 본문 링크 {m} 페이지가 없음')
        if new:
            text = re.sub(r'<[^>]+>', ' ', body)
            if len(a.get('answer') or '') > 150:
                errors.append(f'{where} — 한 줄 답이 150자 넘음 ({len(a["answer"])}자)')
            if body.count('<h2') < 3:
                errors.append(f'{where} — 소제목(h2) 3개 이상 필요')
            if '<table' not in body and '<ul' not in body and '<ol' not in body:
                errors.append(f'{where} — 표나 목록 1개 이상 필요')
            if not re.search(r'href="https?://(?!noahhomepage\.co\.kr)', body):
                errors.append(f'{where} — 출처 링크(공식 자료) 1개 이상 필요')
            for t in (text, a.get('answer') or '', a.get('title') or '', a.get('desc') or ''):
                m = GUARANTEE.search(t)
                if m:
                    errors.append(f'{where} — 보장 표현 금지: "{m.group(0)}"')
            for m in re.finditer(r'기본\s*패키지[^.。]{0,30}?([\d,]{5,})\s*원', text):
                if m.group(1).replace(',', '') != '149000':
                    errors.append(f'{where} — 기본 패키지 금액이 149,000원이 아님: {m.group(0)}')
            if len(text) < 1800:
                warns.append(f'{where} — 본문이 짧음 ({len(text)}자)')
    return len(items)


def check_pages():
    n = 0
    for f in glob.glob(os.path.join(ROOT, 'columns/**/*.html'), recursive=True):
        s = open(f, encoding='utf-8').read()
        n += 1
        rel = os.path.relpath(f, ROOT)
        for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                json.loads(m)
            except Exception as e:  # noqa: BLE001
                errors.append(f'{rel} — 구조화 데이터를 읽을 수 없음: {e}')
        for h in set(re.findall(r'href="(/[^"]*)"', s)):
            if h.startswith('//') or h.startswith('/cdn-cgi/') or '${' in h:   # 스크립트 안 템플릿 문자열은 제외
                continue
            if not page_exists(h):
                errors.append(f'{rel} — 링크 {h} 페이지가 없음')
    return n


def main():
    since = None
    if '--since' in sys.argv:
        since = sys.argv[sys.argv.index('--since') + 1]
    n_d = check_drafts(since)
    n_p = check_pages()
    for w in warns[:20]:
        print('  주의', w)
    if errors:
        for e in errors[:60]:
            print('✗', e)
        print(f'✗ 점검 실패 {len(errors)}건 (원고 {n_d}편 · 페이지 {n_p}개)')
        sys.exit(1)
    print(f'✓ 점검 통과 — 원고 {n_d}편 · 페이지 {n_p}개' + (f' · 새 글 기준 {since} 이후' if since else ''))


if __name__ == '__main__':
    main()
