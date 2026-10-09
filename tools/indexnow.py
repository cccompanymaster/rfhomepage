#!/usr/bin/env python3
"""
IndexNow — 새로 올리거나 고친 페이지를 검색엔진에 바로 알립니다.
네이버 서치어드바이저와 Bing(+ Yandex 등 IndexNow 참여 엔진)에 동시에 전달됩니다.

  python3 tools/indexnow.py                         # 사이트맵의 모든 URL
  python3 tools/indexnow.py --since 2026-09-25      # 이 날짜 이후 lastmod 인 URL만
  python3 tools/indexnow.py --changed BASE HEAD     # 두 커밋 사이에 바뀐 페이지만 (GitHub Actions 가 씀)
  python3 tools/indexnow.py /columns/new-slug /pricing   # 지정한 경로만
  … --dry-run                                       # 보내지 않고 목록만 출력

푸시하면 .github/workflows/indexnow.yml 이 Cloudflare 배포 완료를 기다렸다가
--changed 모드로 자동 실행합니다. 손으로 돌릴 일은 거의 없습니다.

⚠ 배포가 끝난 뒤에 돌리세요. 검색엔진이 https://noahhomepage.co.kr/<키>.txt 를
  직접 열어 키를 확인하므로, 키 파일이 실제 사이트에 올라가 있어야 합니다.
  키 파일(루트의 32자리 .txt)은 지우거나 이름을 바꾸면 안 됩니다.
"""
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = 'noahhomepage.co.kr'
SITE = f'https://{HOST}'
KEY = 'd1ebd682684f953fad9c2a85b7c238bf'
ENDPOINTS = ['https://api.indexnow.org/indexnow', 'https://searchadvisor.naver.com/indexnow']
PRIMARY = ENDPOINTS[0]


def sitemap_urls(since=None):
    sm = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
    out = []
    for loc, rest in re.findall(r'<loc>([^<]+)</loc>(.*?)</url>', sm, re.S):
        m = re.search(r'<lastmod>([^<]+)</lastmod>', rest)
        if since and (not m or m.group(1) < since):
            continue
        out.append(loc)
    return out


def file_to_url(path):
    """저장소 안 HTML 경로 → 실제 주소 (Cloudflare 가 .html 을 떼고 서빙)."""
    if not path.endswith('.html'):
        return None
    if path == 'index.html':
        return SITE + '/'
    if path.endswith('/index.html'):
        return f'{SITE}/{path[:-len("index.html")]}'
    return f'{SITE}/{path[:-5]}'


def changed_urls(base, head):
    """두 커밋 사이에 바뀐(추가·수정) HTML 중 사이트맵에 있는 주소만.
       noindex 페이지(결제·약관·사전정보)는 사이트맵에 없으므로 자연히 빠집니다."""
    if not base or set(base) == {'0'}:            # 브랜치 첫 푸시 등
        base = f'{head}~1'
    try:
        names = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=AM', base, head],
                               cwd=ROOT, check=True, capture_output=True, text=True).stdout.split()
    except subprocess.CalledProcessError as e:
        sys.exit(f'✗ git diff 실패: {e.stderr.strip()}')
    listed = set(sitemap_urls())
    urls = []
    for n in names:
        u = file_to_url(n)
        if u and u in listed and u not in urls:
            urls.append(u)
    return urls


def submit(urls):
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'{SITE}/{KEY}.txt',
                       'urlList': urls[:10000]}).encode()
    ok_primary = False
    for ep in ENDPOINTS:
        req = urllib.request.Request(ep, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                print(f'✓ {ep}  {r.status}  ({len(urls)}개)')
                ok_primary |= ep == PRIMARY
        except urllib.error.HTTPError as e:
            # 200·202 = 접수, 403 = 키 파일 확인 실패(배포 전), 422 = 도메인/키 불일치, 429 = 너무 잦음
            print(f'✗ {ep}  {e.code} {e.reason}')
        except Exception as e:
            print(f'✗ {ep}  {e}')
    return ok_primary


def main():
    args = sys.argv[1:]
    dry = '--dry-run' in args
    args = [a for a in args if a != '--dry-run']
    if '--changed' in args:
        i = args.index('--changed')
        urls = changed_urls(args[i + 1], args[i + 2])
    elif '--since' in args:
        urls = sitemap_urls(args[args.index('--since') + 1])
    elif args:
        urls = [a if a.startswith('http') else SITE + ('' if a.startswith('/') else '/') + a for a in args]
    else:
        urls = sitemap_urls()

    if not urls:
        print('보낼 URL이 없습니다 (사이트맵에 있는 페이지가 바뀌지 않음).')
        return 0
    print(f'{len(urls)}개 URL')
    for u in urls[:30]:
        print('  ', u)
    if len(urls) > 30:
        print(f'   … 외 {len(urls) - 30}개')
    if dry:
        return 0
    return 0 if submit(urls) else 1


if __name__ == '__main__':
    sys.exit(main())
