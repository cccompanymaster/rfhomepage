#!/usr/bin/env python3
"""
IndexNow — 새로 올리거나 고친 페이지를 검색엔진에 바로 알립니다.
네이버 서치어드바이저와 Bing(+ Yandex 등 IndexNow 참여 엔진)에 동시에 전달됩니다.

  python3 tools/indexnow.py                         # 사이트맵의 모든 URL
  python3 tools/indexnow.py --since 2026-09-25      # 이 날짜 이후 lastmod 인 URL만
  python3 tools/indexnow.py /columns/new-slug /pricing   # 지정한 경로만

⚠ 배포가 끝난 뒤에 돌리세요. 검색엔진이 https://noahhomepage.co.kr/<키>.txt 를
  직접 열어 키를 확인하므로, 키 파일이 실제 사이트에 올라가 있어야 합니다.
  키 파일(루트의 32자리 .txt)은 지우거나 이름을 바꾸면 안 됩니다.
"""
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = 'noahhomepage.co.kr'
KEY = 'd1ebd682684f953fad9c2a85b7c238bf'
ENDPOINTS = ['https://api.indexnow.org/indexnow', 'https://searchadvisor.naver.com/indexnow']


def urls_from_sitemap(since=None):
    sm = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
    out = []
    for loc, rest in re.findall(r'<loc>([^<]+)</loc>(.*?)</url>', sm, re.S):
        m = re.search(r'<lastmod>([^<]+)</lastmod>', rest)
        if since and (not m or m.group(1) < since):
            continue
        out.append(loc)
    return out


def main():
    args = sys.argv[1:]
    if '--since' in args:
        urls = urls_from_sitemap(args[args.index('--since') + 1])
    elif args:
        urls = [a if a.startswith('http') else f'https://{HOST}' + ('' if a.startswith('/') else '/') + a for a in args]
    else:
        urls = urls_from_sitemap()
    if not urls:
        print('보낼 URL이 없습니다.')
        return
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt',
                       'urlList': urls[:10000]}).encode()
    for ep in ENDPOINTS:
        req = urllib.request.Request(ep, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                print(f'✓ {ep}  {r.status}  ({len(urls)}개)')
        except urllib.error.HTTPError as e:
            # 200·202 = 접수, 403 = 키 파일 확인 실패(배포 전), 422 = 도메인/키 불일치
            print(f'✗ {ep}  {e.code} {e.reason}')
        except Exception as e:
            print(f'✗ {ep}  {e}')


if __name__ == '__main__':
    main()
