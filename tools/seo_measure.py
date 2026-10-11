#!/usr/bin/env python3
"""
실사이트 SEO 측정 — 크롤러의 눈 (자바스크립트 없이 받은 HTML 기준)

운영 사이트에 직접 요청을 보내 확인합니다. 작업 환경(클라우드 세션)에서는 운영 사이트 접속이
막혀 있어 GitHub Actions(.github/workflows/seo-measure.yml)에서 실행합니다.

  python3 tools/seo_measure.py                        # 사이트맵 전체 + 사이트 수준 점검
  python3 tools/seo_measure.py --json out.json        # 결과를 JSON 으로도 저장
  python3 tools/seo_measure.py --lighthouse lh/       # lh/*.json (Lighthouse 결과) 요약을 합침

요약(마크다운)은 표준출력으로, GITHUB_STEP_SUMMARY 가 있으면 Actions 실행 요약에도 씁니다.
요청은 GET 만 보내고, 동시에 6개까지만 보냅니다. 분석 스크립트를 실행하지 않으므로
GA4 방문 통계에는 잡히지 않습니다.
"""
import argparse
import datetime as dt
import glob
import gzip
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
import zlib
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

HOST = 'noahhomepage.co.kr'
SITE = f'https://{HOST}'
UA = 'Mozilla/5.0 (compatible; NOAH-SEO-Measure/1.0; +https://noahhomepage.co.kr/about)'
INDEXNOW_KEY = 'd1ebd682684f953fad9c2a85b7c238bf'
KST = dt.timezone(dt.timedelta(hours=9))

# robots.txt 로 허용 여부를 확인할 크롤러 (검색 + AI)
BOTS = ['Googlebot', 'Bingbot', 'Yeti', 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User',
        'ClaudeBot', 'Claude-User', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended']


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(url, ua=UA, follow=True, max_hops=5, timeout=25):
    """GET. 리다이렉트를 직접 따라가며 단계별 상태를 기록합니다."""
    hops, cur = [], url
    t0 = time.monotonic()
    for _ in range(max_hops + 1):
        req = urllib.request.Request(cur, headers={'User-Agent': ua, 'Accept-Encoding': 'gzip, deflate',
                                                   'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8'})
        t1 = time.monotonic()
        try:
            r = OPENER.open(req, timeout=timeout)
            status, headers = r.status, r.headers
            ttfb = time.monotonic() - t1
            raw = r.read()
        except urllib.error.HTTPError as e:
            status, headers = e.code, e.headers
            ttfb = time.monotonic() - t1
            raw = e.read() if e.fp else b''
        except Exception as e:  # DNS·TLS·타임아웃
            return {'url': url, 'error': f'{type(e).__name__}: {e}'[:200], 'hops': hops}
        headers = {k.lower(): v for k, v in headers.items()}   # 서버마다 대소문자가 달라 소문자로 통일
        loc = headers.get('location')
        if status in (301, 302, 303, 307, 308) and loc:
            hops.append({'status': status, 'from': cur, 'to': urljoin(cur, loc)})
            if not follow:
                break
            cur = urljoin(cur, loc)
            continue
        enc = (headers.get('content-encoding') or '').lower()
        body = raw
        try:
            if enc == 'gzip':
                body = gzip.decompress(raw)
            elif enc == 'deflate':
                body = zlib.decompress(raw)
        except Exception:
            pass
        return {'url': url, 'final': cur, 'status': status, 'hops': hops, 'headers': headers,
                'ttfb': round(ttfb, 3), 'total': round(time.monotonic() - t0, 3),
                'bytes': len(raw), 'html_bytes': len(body), 'body': body.decode('utf-8', 'replace')}
    return {'url': url, 'final': cur, 'status': hops[-1]['status'] if hops else None, 'hops': hops,
            'headers': {}, 'ttfb': None, 'total': round(time.monotonic() - t0, 3), 'bytes': 0, 'html_bytes': 0, 'body': ''}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title, self._in_title = '', False
        self.meta = {}
        self.canonical = None
        self.h1 = 0
        self.ld, self._in_ld, self._buf = [], False, []
        self._skip = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or '') for k, v in attrs}
        if tag == 'html':
            self.lang = a.get('lang')
        elif tag == 'title':
            self._in_title = True
        elif tag == 'meta':
            key = (a.get('name') or a.get('property') or '').lower()
            if key and key not in self.meta:
                self.meta[key] = a.get('content', '')
        elif tag == 'link' and 'canonical' in a.get('rel', '').lower().split():
            self.canonical = a.get('href')
        elif tag == 'h1':
            self.h1 += 1
        elif tag == 'script':
            if a.get('type', '').lower() == 'application/ld+json':
                self._in_ld, self._buf = True, []
            else:
                self._skip += 1
        elif tag in ('style', 'noscript', 'template'):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
        elif tag == 'script':
            if self._in_ld:
                self.ld.append(''.join(self._buf))
                self._in_ld = False
            elif self._skip:
                self._skip -= 1
        elif tag in ('style', 'noscript', 'template') and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_ld:
            self._buf.append(data)
        elif self._in_title:
            self.title += data
        elif not self._skip:
            self.text.append(data)


def ld_types(blocks):
    types, errors = [], 0
    for b in blocks:
        try:
            d = json.loads(b)
        except Exception:
            errors += 1
            continue
        nodes = d if isinstance(d, list) else d.get('@graph', [d])
        for n in nodes:
            t = n.get('@type') if isinstance(n, dict) else None
            types += t if isinstance(t, list) else ([t] if t else [])
    return types, errors


def norm(u):
    """canonical 비교용 — 끝 슬래시 차이(루트 제외)만 무시"""
    if not u:
        return u
    p = urlparse(u)
    path = p.path if p.path in ('', '/') else p.path.rstrip('/')
    return f'{p.scheme}://{p.netloc}{path or "/"}'


def check_page(url):
    r = fetch(url)
    if 'error' in r:
        return r
    out = {k: r[k] for k in ('url', 'final', 'status', 'hops', 'ttfb', 'total', 'bytes', 'html_bytes')}
    ctype = r['headers'].get('content-type', '')
    out['x_robots'] = r['headers'].get('x-robots-tag', '')
    out['cache'] = r['headers'].get('cache-control', '')
    if 'html' not in ctype:
        out['ctype'] = ctype
        return out
    p = PageParser()
    try:
        p.feed(r['body'])
    except Exception as e:
        out['parse_error'] = str(e)[:120]
    types, ld_err = ld_types(p.ld)
    text = re.sub(r'\s+', ' ', ' '.join(p.text)).strip()
    out.update({
        'lang': p.lang,
        'title': p.title.strip(),
        'desc': p.meta.get('description', '').strip(),
        'robots': p.meta.get('robots', ''),
        'canonical': p.canonical,
        'h1': p.h1,
        'ld_blocks': len(p.ld), 'ld_errors': ld_err, 'ld_types': sorted(set(types)),
        'og_image': bool(p.meta.get('og:image')),
        'google_verify': bool(p.meta.get('google-site-verification')),
        'naver_verify': bool(p.meta.get('naver-site-verification')),
        'text_chars': len(text),
    })
    return out


def sitemap_urls(xml):
    return re.findall(r'<url>\s*<loc>([^<]+)</loc>', xml)


def pct(vals, q):
    if not vals:
        return None
    vals = sorted(vals)
    i = min(len(vals) - 1, max(0, round(q * (len(vals) - 1))))
    return vals[i]


def site_checks():
    s = {}
    # robots.txt
    r = fetch(f'{SITE}/robots.txt')
    s['robots_status'] = r.get('status')
    body = r.get('body', '')
    s['robots_has_sitemap'] = 'sitemap:' in body.lower()
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(body.splitlines())
    s['robots_allow'] = {b: rp.can_fetch(b, f'{SITE}/') for b in BOTS}
    # sitemap
    r = fetch(f'{SITE}/sitemap.xml')
    s['sitemap_status'] = r.get('status')
    sm = r.get('body', '')
    urls = sitemap_urls(sm)
    lastmods = re.findall(r'<lastmod>([^<]+)</lastmod>', sm)
    s['sitemap_urls'] = len(urls)
    s['sitemap_dupes'] = len(urls) - len(set(urls))
    s['sitemap_offhost'] = [u for u in urls if urlparse(u).netloc != HOST]
    s['sitemap_lastmod_max'] = max(lastmods) if lastmods else None
    # llms.txt · 피드 · 키 파일 · 빙 인증
    for name, path in [('llms', '/llms.txt'), ('rss', '/columns/feed.xml'), ('bing_auth', '/BingSiteAuth.xml')]:
        s[f'{name}_status'] = fetch(f'{SITE}{path}').get('status')
    k = fetch(f'{SITE}/{INDEXNOW_KEY}.txt')
    s['indexnow_key_ok'] = k.get('status') == 200 and k.get('body', '').strip() == INDEXNOW_KEY
    # 404 가 진짜 404 인가 (소프트 404 방지)
    s['notfound_status'] = fetch(f'{SITE}/__seo_measure_not_found_check').get('status')
    # 리다이렉트 규칙
    redirs = {}
    for label, u in [('http→https', f'http://{HOST}/'), ('www', f'https://www.{HOST}/'),
                     ('/index.html', f'{SITE}/index.html'), ('/pricing.html', f'{SITE}/pricing.html')]:
        x = fetch(u)
        redirs[label] = x.get('error') or ' → '.join(f"{h['status']} {urlparse(h['to']).netloc}{urlparse(h['to']).path}" for h in x['hops']) + f" → {x.get('status')}"
    s['redirects'] = redirs
    # 참고: User-Agent 만 바꾼 요청 (IP 기반 봇 판별과는 다를 수 있음)
    probe = {}
    for name, ua in [('브라우저', UA),
                     ('GPTBot', 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.2; +https://openai.com/gptbot'),
                     ('ClaudeBot', 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ClaudeBot/1.0; +claudebot@anthropic.com'),
                     ('PerplexityBot', 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot')]:
        probe[name] = fetch(f'{SITE}/', ua=ua).get('status')
    s['ua_probe'] = probe
    return s, urls


def lighthouse_summary(folder):
    rows = []
    for f in sorted(glob.glob(os.path.join(folder, '*.json'))):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        cat = d.get('categories', {})
        au = d.get('audits', {})
        def sc(k):
            v = (cat.get(k) or {}).get('score')
            return None if v is None else round(v * 100)
        def nv(k):
            return (au.get(k) or {}).get('numericValue')
        seo_fail = [a['id'] for a in (au.get(r['id']) for r in (cat.get('seo') or {}).get('auditRefs', []))
                    if a and a.get('score') is not None and a.get('score') < 1]
        rows.append({
            'url': d.get('finalDisplayedUrl') or d.get('requestedUrl'),
            'perf': sc('performance'), 'seo': sc('seo'), 'a11y': sc('accessibility'), 'bp': sc('best-practices'),
            'lcp_s': round(nv('largest-contentful-paint') / 1000, 2) if nv('largest-contentful-paint') else None,
            'cls': round(nv('cumulative-layout-shift'), 3) if nv('cumulative-layout-shift') is not None else None,
            'tbt_ms': round(nv('total-blocking-time')) if nv('total-blocking-time') is not None else None,
            'fcp_s': round(nv('first-contentful-paint') / 1000, 2) if nv('first-contentful-paint') else None,
            'seo_fail': seo_fail,
        })
    return rows


def mark(ok, warn=False):
    return '✅' if ok else ('⚠️' if warn else '❌')


def report(site, pages, lh, when):
    ok = [p for p in pages if p.get('status') == 200 and 'error' not in p]
    html = [p for p in ok if 'title' in p]
    bad_status = [p for p in pages if 'error' in p or p.get('status') != 200]
    redirected = [p for p in pages if p.get('hops')]
    noindex = [p for p in html if 'noindex' in (p.get('robots') or '').lower() or 'noindex' in (p.get('x_robots') or '').lower()]
    canon_missing = [p for p in html if not p.get('canonical')]
    canon_mismatch = [p for p in html if p.get('canonical') and norm(p['canonical']) != norm(p['url'])]
    no_title = [p for p in html if not p.get('title')]
    no_desc = [p for p in html if not p.get('desc')]
    titles, descs = {}, {}
    for p in html:
        titles.setdefault(p['title'], []).append(p['url'])
        descs.setdefault(p['desc'], []).append(p['url'])
    dup_titles = {t: u for t, u in titles.items() if t and len(u) > 1}
    dup_descs = {t: u for t, u in descs.items() if t and len(u) > 1}
    h1_bad = [p for p in html if p.get('h1') != 1]
    ld_err = [p for p in html if p.get('ld_errors')]
    ld_none = [p for p in html if not p.get('ld_blocks')]
    no_lang = [p for p in html if not p.get('lang')]
    thin = [p for p in html if p.get('text_chars', 0) < 400]
    ttfb = [p['ttfb'] for p in ok if p.get('ttfb') is not None]
    kb = [p['bytes'] / 1024 for p in ok]
    tlen = [len(p['title']) for p in html if p.get('title')]
    dlen = [len(p['desc']) for p in html if p.get('desc')]
    home = next((p for p in html if norm(p['url']) == norm(SITE + '/')), {})

    L = []
    w = L.append
    w(f'## NOAH SEO 측정 — {when} (KST)')
    w('')
    w(f'측정 위치: GitHub Actions 서버(미국) · 기준: 자바스크립트 없이 받은 HTML · 대상: 사이트맵 {len(pages)}개 URL')
    if os.environ.get('GITHUB_SHA'):
        w(f'저장소 커밋: `{os.environ["GITHUB_SHA"][:7]}`')
    w('')
    w('### 요약')
    w('')
    w('| 항목 | 결과 | 상태 |')
    w('|---|---|---|')
    w(f'| 응답 200 | {len(ok)}/{len(pages)} | {mark(not bad_status)} |')
    w(f'| HTML 분석된 페이지 | {len(html)}/{len(ok)} | {mark(html and len(html) == len(ok), warn=bool(html))} |')
    w(f'| noindex (메타·헤더) | {len(noindex)}개 | {mark(not noindex)} |')
    w(f'| canonical 없음 / 불일치 | {len(canon_missing)} / {len(canon_mismatch)} | {mark(not canon_missing and not canon_mismatch)} |')
    w(f'| 제목 없음 / 중복 | {len(no_title)} / {len(dup_titles)}건 | {mark(not no_title and not dup_titles, warn=not no_title)} |')
    w(f'| 설명문 없음 / 중복 | {len(no_desc)} / {len(dup_descs)}건 | {mark(not no_desc and not dup_descs, warn=not no_desc)} |')
    w(f'| h1 이 1개가 아닌 페이지 | {len(h1_bad)} | {mark(not h1_bad, warn=True)} |')
    w(f'| 구조화 데이터 오류 / 없음 | {len(ld_err)} / {len(ld_none)} | {mark(not ld_err and not ld_none, warn=not ld_err)} |')
    w(f'| html lang 없음 | {len(no_lang)} | {mark(not no_lang)} |')
    w(f'| 본문 400자 미만 | {len(thin)} | {mark(not thin, warn=True)} |')
    w(f'| 서버 응답(TTFB) 중앙값 / 90% | {pct(ttfb, .5)}s / {pct(ttfb, .9)}s | {mark((pct(ttfb, .9) or 9) < 0.8, warn=True)} |')
    w(f'| HTML 전송량 중앙값 / 최대 | {pct(kb, .5) and round(pct(kb, .5), 1)}KB / {kb and round(max(kb), 1)}KB | ✅ |')
    w(f'| 제목 길이(자) 최소·중앙·최대 | {tlen and min(tlen)} · {pct(tlen, .5)} · {tlen and max(tlen)} | – |')
    w(f'| 설명문 길이(자) 최소·중앙·최대 | {dlen and min(dlen)} · {pct(dlen, .5)} · {dlen and max(dlen)} | – |')
    w('')
    w('### 사이트 수준')
    w('')
    w(f"- robots.txt {site['robots_status']} · 사이트맵 안내 {'있음' if site['robots_has_sitemap'] else '없음'}")
    blocked = [b for b, v in site['robots_allow'].items() if not v]
    w(f"- robots.txt 허용: {'모두 허용' if not blocked else '차단: ' + ', '.join(blocked)} ({', '.join(BOTS)})")
    w(f"- sitemap.xml {site['sitemap_status']} · URL {site['sitemap_urls']}개 · 중복 {site['sitemap_dupes']} · 다른 도메인 {len(site['sitemap_offhost'])} · 최근 lastmod {site['sitemap_lastmod_max']}")
    w(f"- llms.txt {site['llms_status']} · RSS {site['rss_status']} · BingSiteAuth.xml {site['bing_auth_status']} · IndexNow 키 {'정상' if site['indexnow_key_ok'] else '확인 필요'}")
    w(f"- 없는 주소 응답: {site['notfound_status']} {'(정상: 진짜 404)' if site['notfound_status'] == 404 else '(⚠️ 소프트 404 의심)'}")
    w(f"- 소유 확인 메타(홈): 구글 {'있음' if home.get('google_verify') else '없음(파일·DNS 방식이면 정상)'} · 네이버 {'있음' if home.get('naver_verify') else '없음'}")
    for k, v in site['redirects'].items():
        w(f'- 리다이렉트 {k}: {v}')
    w(f"- 참고(User-Agent 만 바꾼 요청, 확정 아님): " + ' · '.join(f'{k} {v}' for k, v in site['ua_probe'].items()))
    if lh:
        w('')
        w('### Lighthouse (모바일, 분석 스크립트 차단)')
        w('')
        w('| 페이지 | 성능 | SEO | 접근성 | 권장사항 | LCP | CLS | TBT | SEO 감점 항목 |')
        w('|---|---|---|---|---|---|---|---|---|')
        for r in lh:
            path = urlparse(r['url'] or '').path or '/'
            w(f"| {path} | {r['perf']} | {r['seo']} | {r['a11y']} | {r['bp']} | {r['lcp_s']}s | {r['cls']} | {r['tbt_ms']}ms | {', '.join(r['seo_fail']) or '-'} |")
    issues = [('응답 이상', bad_status, lambda p: f"{p.get('status') or p.get('error')}"),
              ('리다이렉트되는 사이트맵 URL', redirected, lambda p: ' → '.join(str(h['status']) for h in p['hops']) + f" → {p.get('final')}"),
              ('noindex', noindex, lambda p: p.get('robots') or p.get('x_robots')),
              ('canonical 불일치', canon_mismatch, lambda p: p.get('canonical')),
              ('h1 개수', h1_bad, lambda p: f"h1 {p.get('h1')}개"),
              ('구조화 데이터 파싱 오류', ld_err, lambda p: f"{p.get('ld_errors')}블록"),
              ('구조화 데이터 없음', ld_none, lambda p: ''),
              ('본문 400자 미만', thin, lambda p: f"{p.get('text_chars')}자")]
    shown = [(n, xs, f) for n, xs, f in issues if xs]
    if shown or dup_titles or dup_descs:
        w('')
        w('### 확인할 페이지')
        for n, xs, f in shown:
            w('')
            w(f'**{n}** ({len(xs)})')
            for p in xs[:12]:
                w(f"- {urlparse(p['url']).path or '/'} — {f(p)}")
            if len(xs) > 12:
                w(f'- … 외 {len(xs) - 12}개')
        for n, d in [('제목 중복', dup_titles), ('설명문 중복', dup_descs)]:
            if d:
                w('')
                w(f'**{n}** ({len(d)}건)')
                for t, us in list(d.items())[:8]:
                    w(f"- “{t[:40]}” — " + ', '.join(urlparse(u).path for u in us[:4]))
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json')
    ap.add_argument('--lighthouse')
    args = ap.parse_args()
    when = dt.datetime.now(KST).strftime('%Y-%m-%d %H:%M')
    site, urls = site_checks()
    with ThreadPoolExecutor(max_workers=6) as ex:
        pages = list(ex.map(check_page, urls))
    lh = lighthouse_summary(args.lighthouse) if args.lighthouse and os.path.isdir(args.lighthouse) else []
    md = report(site, pages, lh, when)
    print(md)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
            f.write(md + '\n')
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump({'measured_at': when, 'site': site, 'pages': pages, 'lighthouse': lh}, f, ensure_ascii=False, indent=1)
    # 치명적 문제(응답 이상·noindex·구조화 데이터 오류)가 있으면 실패로 표시해 눈에 띄게 함
    fatal = not any('title' in p for p in pages) or \
        any('error' in p or p.get('status') != 200 for p in pages) or \
        any('noindex' in (p.get('robots') or '').lower() or 'noindex' in (p.get('x_robots') or '').lower() for p in pages) or \
        any(p.get('ld_errors') for p in pages)
    sys.exit(1 if fatal else 0)


if __name__ == '__main__':
    main()
