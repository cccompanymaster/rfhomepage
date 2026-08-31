#!/usr/bin/env python3
"""
칼럼 정적 페이지 빌더 (SEO 고도화판)

  content/columns/batch-*.json
      ↓
  columns/<slug>.html        개별 칼럼 100편
  columns/index.html         전체 목록 (검색·필터·페이지네이션)
  columns/topic/<cluster>.html  토픽 허브 8개 (필라 페이지)
  columns/feed.xml           RSS

실행:  python3 tools/build_columns.py
OG 이미지까지 재생성:  python3 tools/build_columns.py --og
  (OG는 Pretendard OTF 필요 — tools/build_columns.md 참고)
"""
import json, glob, re, os, html, sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'columns')
HUB_DIR = os.path.join(OUT_DIR, 'topic')
OG_DIR = os.path.join(ROOT, 'assets/images/og')
SITE = 'https://noahhomepage.co.kr'
BRAND = 'NOAH 노아홈페이지'

# 토픽 허브 — 클러스터별 필라 페이지 (내부링크 권위 집중)
CLUSTERS = {
    'cost':     {'name': '비용·견적',      'h': '홈페이지 제작 비용, 얼마가 적정할까',
                 'lead': '견적서를 받아도 비교가 어려운 이유는 항목 기준이 제각각이기 때문입니다. 무엇에 돈이 드는지부터 정리했습니다.'},
    'guide':    {'name': '제작 가이드',     'h': '홈페이지, 처음부터 끝까지 이렇게 만듭니다',
                 'lead': '도메인·호스팅부터 필수 페이지와 법적 표기까지. 순서대로 따라가면 빠뜨릴 일이 줄어듭니다.'},
    'industry': {'name': '업종별 제작',     'h': '업종마다 홈페이지의 숙제가 다릅니다',
                 'lead': '치과에는 의료광고 심의가, 카페에는 사진이, 제조업에는 카탈로그가 관건입니다. 업종별로 짚었습니다.'},
    'seo':      {'name': 'SEO·검색노출',    'h': '만든 다음, 검색에서 발견되게 하는 법',
                 'lead': '네이버·구글 등록부터 사이트맵·메타태그·지역 검색까지. 순위를 약속하는 대신 기본기를 정리했습니다.'},
    'compare':  {'name': '제작 방식 비교',   'h': '어떤 방식으로 만들지 정하는 기준',
                 'lead': '템플릿·맞춤 제작·빌더·프리랜서·에이전시. 정답은 없고 상황에 맞는 선택만 있습니다.'},
    'ops':      {'name': '운영·유지보수',    'h': '오픈이 끝이 아니라 시작인 이유',
                 'lead': '속도·보안·백업·콘텐츠 갱신. 만든 뒤에 해야 할 일들을 현실적인 범위로 정리했습니다.'},
    'design':   {'name': '디자인·기획',      'h': '보기 좋은 것과 잘 팔리는 것 사이',
                 'lead': '카피·컬러·사진·폼 설계까지, 방문자를 문의로 이어지게 만드는 구성 요소를 다룹니다.'},
    'local':    {'name': '지역별 제작',      'h': '우리 지역 손님에게 발견되려면',
                 'lead': '지역마다 주력 산업과 검색 습관이 다릅니다. 지역 검색 최적화와 함께 정리했습니다.'},
}


# 본문 문맥 내부링크 사전 — 실제 본문에 자주 등장하는 용어만 엄선
# (긴 표현이 먼저 매칭되도록 길이순 정렬해서 사용)
ANCHOR_TERMS = {
    '도메인': 'domain-register', '웹호스팅': 'web-hosting', '호스팅': 'web-hosting',
    'SSL': 'ssl-setup', '개인정보처리방침': 'privacy-policy', '이용약관': 'terms-of-service',
    '사이트맵': 'sitemap-submit', 'robots.txt': 'robots-txt', '메타태그': 'meta-tags',
    '서치콘솔': 'search-console', '서치어드바이저': 'naver-advisor',
    '네이버 플레이스': 'naver-place', '구글 비즈니스 프로필': 'google-business',
    '구글 애널리틱스': 'ga4-setup', '유지보수': 'maintenance-scope', '백업': 'backup-guide',
    '리뉴얼': 'renewal-timing', '워드프레스': 'wordpress-vs-imweb', '아임웹': 'imweb-review',
    '카페24': 'cafe24-guide', '윅스': 'wix-review', '템플릿': 'template-homepage',
    '모바일 최적화': 'mobile-optimize', '로고': 'logo-design', '카피라이팅': 'copywriting',
    '브랜드 컬러': 'brand-color', '폰트': 'font-choice', 'AI 이미지': 'ai-image',
    '전환율': 'conversion-rate', '문의 폼': 'form-design', '상담 폼': 'form-design',
    '소유권': 'ownership-transfer', '계약서': 'contract-check', '지역 검색': 'local-seo',
    '제작 비용': 'homepage-cost', '견적': 'homepage-quote', '제작 기간': 'production-period',
    '속도': 'speed-optimize', '보안': 'security-check', '키워드 선정': 'keyword-research',
    '필수 페이지': 'essential-pages', '무료 홈페이지': 'free-homepage',
    # 업종·주제 교차 링크 (0개였던 글 보강)
    '의료광고': 'hospital-homepage', '전후사진': 'plastic-surgery',
    '치과': 'dental-homepage', '한의원': 'oriental-clinic', '피부과': 'dermatology-homepage',
    '카페': 'cafe-homepage', '음식점': 'restaurant-homepage', '법무법인': 'law-firm-homepage',
    '세무사': 'tax-accountant', '인테리어': 'interior-homepage', '학원': 'academy-homepage',
    '필라테스': 'pilates-homepage', '펜션': 'pension-homepage', '제조업': 'manufacturing-homepage',
    '스타트업': 'startup-homepage', '검색 순위': 'ranking-problems', '방문자 분석': 'visitor-analysis',
    '네이버 검색 등록': 'naver-register', '상위노출': 'blog-ranking', '콘텐츠': 'content-strategy',
    '메인페이지': 'main-page-structure', '사진': 'photo-prepare', '서브페이지': 'essential-pages',
}
ANCHOR_TERMS = {k: v for k, v in ANCHOR_TERMS.items() if v}

GTM = '''<!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-WZWCZTKJ');</script>
    <!-- End Google Tag Manager -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-5CRNX231R3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-5CRNX231R3', { anonymize_ip: true });
    </script>'''

GTM_NOSCRIPT = '''<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WZWCZTKJ"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'''

HEAD_COMMON = '''<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
    <link rel="icon" href="/favicon.ico" sizes="any" />
    <link rel="icon" type="image/png" sizes="512x512" href="/favicon.png" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="alternate" type="application/rss+xml" title="NOAH 칼럼" href="/columns/feed.xml" />
    <meta name="theme-color" content="#FFFFFF" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" />
    <script src="https://cdn.tailwindcss.com"></script>'''

STYLE = '''      body { background: var(--bg); color: var(--text); }
      .disp { font-family: 'Space Grotesk', 'Pretendard Variable', sans-serif; letter-spacing: -0.03em; font-weight: 700; }
      .col-head { border-bottom: 1px solid var(--line); }
      .chip { display:inline-flex; align-items:center; padding: 7px 15px; border-radius: 999px; border: 1px solid var(--line); font-size: 13px; font-weight: 600; color: var(--text-dim); background: transparent; transition: all .2s; white-space: nowrap; cursor: pointer; }
      .chip:hover { border-color: rgba(17,24,33,.24); color: var(--text); }
      .chip[aria-pressed="true"] { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
      .card { display:block; border: 1px solid var(--line); border-radius: 16px; background: var(--bg-soft); padding: 22px; transition: transform .25s, border-color .25s; height: 100%; }
      .card:hover { transform: translateY(-3px); border-color: rgba(17,24,33,.20); box-shadow: 0 14px 30px -18px rgba(17,24,33,.22); }
      .card .cat { font-size: 11px; letter-spacing: .16em; color: var(--accent); font-weight: 700; text-transform: uppercase; }
      .card h3 { font-size: 17px; font-weight: 700; line-height: 1.4; margin: 10px 0 8px; }
      .card p { font-size: 13.5px; line-height: 1.7; color: var(--text-dim); }
      .card .meta { font-size: 12px; color: var(--text-quiet); margin-top: 14px; }
      .f-search { width: 100%; padding: 14px 18px; background: var(--bg-soft); border: 1px solid var(--line); border-radius: 12px; color: var(--text); font-size: 15px; }
      .f-search:focus { outline: none; border-color: var(--accent-deep); box-shadow: 0 0 0 3px rgba(255,90,43,.16); }
      .pager button { min-width: 40px; height: 40px; border-radius: 10px; border: 1px solid var(--line); color: var(--text-dim); font-size: 14px; font-weight: 600; transition: all .2s; }
      .pager button:hover:not(:disabled) { border-color: rgba(17,24,33,.24); color: var(--text); }
      .pager button[aria-current="true"] { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
      .pager button:disabled { opacity: .35; cursor: not-allowed; }

      /* 목차 */
      .toc { border: 1px solid var(--line); border-radius: 14px; background: var(--bg-soft); padding: 20px 22px; }
      .toc p.lb { font-size: 11px; letter-spacing: .18em; color: var(--accent); font-weight: 700; margin-bottom: 12px; }
      .toc ol { list-style: none; counter-reset: t; }
      .toc li { counter-increment: t; margin-bottom: 9px; }
      .toc li:last-child { margin-bottom: 0; }
      .toc a { font-size: 14.5px; color: var(--text-dim); line-height: 1.55; display: flex; gap: 10px; transition: color .18s; }
      .toc a::before { content: counter(t, decimal-leading-zero); font-size: 11.5px; color: var(--text-quiet); font-weight: 700; padding-top: 3px; flex-shrink: 0; }
      .toc a:hover { color: var(--text); }

      /* 본문 타이포 */
      .prose { font-size: 16px; line-height: 1.95; color: var(--text-dim); }
      .prose h2 { font-family:'Space Grotesk','Pretendard Variable',sans-serif; font-size: clamp(21px, 3.4vw, 27px); font-weight: 700; letter-spacing: -0.02em; color: var(--text); margin: 46px 0 16px; padding-top: 22px; border-top: 1px solid var(--line-soft); scroll-margin-top: 24px; }
      .prose h2:first-child { margin-top: 0; border-top: 0; padding-top: 0; }
      .prose h3 { font-size: 18px; font-weight: 700; color: var(--text); margin: 28px 0 10px; scroll-margin-top: 24px; }
      .prose p { margin: 0 0 18px; }
      .prose strong { color: var(--text); font-weight: 700; }
      .prose a { color: var(--accent-deep); text-decoration: underline; text-underline-offset: 3px; text-decoration-color: rgba(255,90,43,.42); transition: text-decoration-color .2s; }
      .prose a:hover { text-decoration-color: var(--accent); }
      .prose ul, .prose ol { margin: 0 0 20px; padding-left: 20px; }
      .prose li { margin-bottom: 9px; }
      .prose ul li { list-style: none; position: relative; padding-left: 16px; }
      .prose ul li::before { content: '—'; position: absolute; left: 0; color: var(--accent-deep); }
      .prose ol { list-style: decimal; }
      .prose ol li { padding-left: 4px; }
      .prose blockquote { border-left: 3px solid var(--accent-deep); padding: 4px 0 4px 18px; margin: 0 0 20px; color: var(--text); font-style: normal; }
      .prose table { width: 100%; border-collapse: collapse; margin: 0 0 22px; font-size: 14.5px; display: block; overflow-x: auto; }
      .prose th, .prose td { border: 1px solid var(--line); padding: 11px 13px; text-align: left; vertical-align: top; }
      .prose th { background: var(--bg-soft); color: var(--text); font-weight: 700; white-space: nowrap; }
      .prose code { background: var(--bg-elev); padding: 2px 7px; border-radius: 5px; font-size: 13.5px; color: var(--accent); }
      .cta-box { border: 1px solid rgba(255,90,43,.28); border-radius: 18px; background: linear-gradient(160deg, var(--accent-soft), rgba(255,255,255,0)); padding: 30px; }
      .rel a { display:block; border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; transition: border-color .2s, background .2s; }
      .rel a:hover { border-color: rgba(17,24,33,.20); background: var(--bg-soft); }
      .pn a { display:block; border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; transition: border-color .2s, background .2s; }
      .pn a:hover { border-color: rgba(17,24,33,.20); background: var(--bg-soft); }
      .hub-pill { display:inline-flex; align-items:center; gap:7px; padding: 9px 16px; border-radius: 999px; border: 1px solid var(--line); font-size: 13.5px; font-weight: 600; color: var(--text-dim); transition: all .2s; }
      .hub-pill:hover { border-color: var(--accent); color: var(--text); }'''

NAV = '''    <header class="container-x pt-8 pb-2 flex items-center justify-between gap-4">
      <a href="/" class="inline-flex items-center gap-2 text-sm shrink-0" style="color: var(--text-dim)">
        <span style="width:26px;height:26px;border-radius:7px;background:linear-gradient(135deg,#FF5A2B,#FFB300);display:inline-block"></span>
        <span class="font-semibold" style="color: var(--text)">NOAH</span>
        <span class="hidden sm:inline" style="color: var(--text-quiet)">· 칼럼</span>
      </a>
      <div class="flex items-center gap-2 shrink-0">
        <a href="/references" class="text-sm hidden sm:inline" style="color: var(--text-dim)">레퍼런스</a>
        <a href="/columns/" class="text-sm hidden sm:inline" style="color: var(--text-dim)">칼럼 목록</a>
        <a href="/contact" class="text-sm font-bold px-5 py-2.5 rounded-full" style="background:var(--accent);color:var(--on-accent)">무료 상담</a>
      </div>
    </header>'''


def footer(hubs_html=''):
    return f'''    <footer class="container-x py-12 mt-16 text-xs" style="border-top: 1px solid var(--line); color: var(--text-quiet)">
      {hubs_html}
      <div class="flex gap-5 justify-center flex-wrap mb-4">
        <a href="/" class="hover:text-[color:var(--text)]">홈</a>
        <a href="/references" class="hover:text-[color:var(--text)]">레퍼런스</a>
        <a href="/columns/" class="hover:text-[color:var(--text)]">칼럼</a>
        <a href="/pricing" class="hover:text-[color:var(--text)]">가격</a>
        <a href="/contact" class="hover:text-[color:var(--text)]">상담 신청</a>
      </div>
      <p class="text-center">NOAH · 노아홈페이지 — 씨씨컴퍼니(CC Company) · 대표: 채희준 · 사업자등록번호: 275-05-01613</p>
      <p class="mt-1 text-center">본 칼럼은 일반적인 정보 제공을 목적으로 하며, 법률·세무 등 전문 자문을 대체하지 않습니다.</p>
    </footer>'''


def esc(s):
    return html.escape(str(s), quote=True)


def slugify_heading(text, used):
    """h2 텍스트 → URL 앵커. 한글은 로마자 대신 순번 기반으로 안전하게."""
    base = re.sub(r'[^0-9a-zA-Z가-힣\s-]', '', text).strip()
    base = re.sub(r'\s+', '-', base)[:40] or 'section'
    s, i = base, 2
    while s in used:
        s = f'{base}-{i}'; i += 1
    used.add(s)
    return s


def add_anchors_and_toc(body):
    """본문 h2에 id 부여 + 목차 데이터 반환 (구글 섹션 직행 링크 대응)"""
    used, toc = set(), []

    def rep(m):
        inner = m.group(1)
        txt = re.sub(r'<[^>]+>', '', inner).strip()
        aid = slugify_heading(txt, used)
        toc.append((aid, txt))
        return f'<h2 id="{aid}">{inner}</h2>'

    body = re.sub(r'<h2>(.*?)</h2>', rep, body, flags=re.S)
    return body, toc


def link_keywords(body, self_slug, slugset, limit=5):
    """본문 <p>·<li> 텍스트에 다른 칼럼으로 가는 문맥 내부링크 삽입.
       용어당 1회, 글당 최대 limit개, 이미 <a> 안이면 건너뜀."""
    used, count = set(), 0
    terms = sorted(
        ((t, sl) for t, sl in ANCHOR_TERMS.items() if sl != self_slug and sl in slugset),
        key=lambda x: -len(x[0]))

    def in_text(text):
        nonlocal count
        for term, sl in terms:
            if count >= limit:
                break
            if sl in used or term not in text:
                continue
            text = text.replace(term, f'<a href="/columns/{sl}">{term}</a>', 1)
            used.add(sl); count += 1
        return text

    out, pos = [], 0
    for m in re.finditer(r'<(p|li)>(.*?)</\1>', body, flags=re.S):
        parts = re.split(r'(<[^>]+>)', m.group(2))
        inside_a = False
        for i, seg in enumerate(parts):
            if seg.startswith('<'):
                if seg.startswith('<a'):
                    inside_a = True
                elif seg.startswith('</a'):
                    inside_a = False
                continue
            if not inside_a and count < limit:
                parts[i] = in_text(seg)
        out.append(body[pos:m.start(2)]); out.append(''.join(parts))
        pos = m.end(2)
    out.append(body[pos:])
    return ''.join(out)


def load_all():
    cols = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'content/columns/batch-*.json'))):
        for a in json.load(open(f, encoding='utf-8')):
            cols[a['slug']] = a
    order = json.load(open(os.path.join(ROOT, 'content/keywords-100.json'), encoding='utf-8'))['keywords']
    base = date(2026, 8, 19)
    out = []
    for i, k in enumerate(order):
        a = cols.get(k['slug'])
        if not a:
            continue
        a['n'] = k['n']
        a['cluster'] = a.get('cluster') or k['cluster']
        a['date'] = (base - timedelta(days=i * 2)).isoformat()
        out.append(a)
    return out


def related(art, all_cols):
    same = [a for a in all_cols if a['cluster'] == art['cluster'] and a['slug'] != art['slug']]
    other = [a for a in all_cols if a['cluster'] != art['cluster']]
    idx = art['n']
    picks = [same[(idx + i) % len(same)] for i in range(min(3, len(same)))] if same else []
    if other:
        picks.append(other[(idx * 7) % len(other)])
    seen, res = set(), []
    for p in picks:
        if p['slug'] not in seen:
            seen.add(p['slug']); res.append(p)
    return res[:4]


def build_article(art, all_cols, slugset, by_cluster):
    cl = art['cluster']
    cat = CLUSTERS[cl]['name']
    body, toc = add_anchors_and_toc(art['body'])
    body = link_keywords(body, art['slug'], slugset)
    plain = re.sub(r'<[^>]+>', '', body)

    # 클러스터 내 이전/다음
    sib = by_cluster[cl]
    pos = [i for i, a in enumerate(sib) if a['slug'] == art['slug']][0]
    prev_a = sib[pos - 1] if pos > 0 else None
    next_a = sib[pos + 1] if pos < len(sib) - 1 else None

    rels = related(art, all_cols)
    rel_html = '\n'.join(
        f'''        <a href="/columns/{r['slug']}">
          <span class="text-[11px] font-bold tracking-widest" style="color:var(--accent)">{esc(CLUSTERS[r['cluster']]['name'])}</span>
          <p class="text-sm font-bold mt-1.5 leading-6">{esc(r['title'])}</p>
        </a>''' for r in rels)

    toc_html = ''
    if len(toc) >= 3:
        items = '\n'.join(f'          <li><a href="#{aid}">{esc(t)}</a></li>' for aid, t in toc)
        toc_html = f'''      <nav class="toc mt-10" aria-label="목차">
        <p class="lb">이 글의 순서</p>
        <ol>
{items}
        </ol>
      </nav>'''

    pn_html = ''
    if prev_a or next_a:
        cells = []
        if prev_a:
            cells.append(f'''        <a href="/columns/{prev_a['slug']}" rel="prev">
          <span class="text-[11px] font-bold" style="color:var(--text-quiet)">← 이전 글</span>
          <p class="text-sm font-bold mt-1.5 leading-6">{esc(prev_a['title'])}</p>
        </a>''')
        if next_a:
            cells.append(f'''        <a href="/columns/{next_a['slug']}" rel="next" class="sm:text-right">
          <span class="text-[11px] font-bold" style="color:var(--text-quiet)">다음 글 →</span>
          <p class="text-sm font-bold mt-1.5 leading-6">{esc(next_a['title'])}</p>
        </a>''')
        pn_html = f'''      <nav class="pn grid sm:grid-cols-2 gap-3 mt-12" aria-label="이어 읽기">
{chr(10).join(cells)}
      </nav>'''

    ld_article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": art['title'][:110],
        "description": art['desc'],
        "datePublished": art['date'],
        "dateModified": art['date'],
        "inLanguage": "ko-KR",
        "wordCount": len(plain),
        "articleSection": cat,
        "keywords": art['kw'] + ', ' + ', '.join(art.get('tags', [])),
        "image": f"{SITE}/assets/images/og/{art['slug']}.png",
        "author": {"@type": "Organization", "name": BRAND, "url": SITE},
        "publisher": {"@type": "Organization", "name": BRAND,
                      "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.png"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE}/columns/{art['slug']}"},
        "isPartOf": {"@type": "Blog", "name": "NOAH 홈페이지 제작 칼럼", "@id": f"{SITE}/columns/"},
        "about": {"@type": "Thing", "name": art['kw']},
    }
    ld_crumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "칼럼", "item": f"{SITE}/columns/"},
            {"@type": "ListItem", "position": 3, "name": cat, "item": f"{SITE}/columns/topic/{cl}"},
            {"@type": "ListItem", "position": 4, "name": art['title'], "item": f"{SITE}/columns/{art['slug']}"},
        ],
    }

    tags = ' '.join(
        f'<span class="text-xs px-3 py-1.5 rounded-full" style="border:1px solid var(--line); color:var(--text-quiet)">#{esc(t)}</span>'
        for t in art.get('tags', []))

    prev_link = f'<link rel="prev" href="{SITE}/columns/{prev_a["slug"]}" />\n    ' if prev_a else ''
    next_link = f'<link rel="next" href="{SITE}/columns/{next_a["slug"]}" />\n    ' if next_a else ''

    return f'''<!doctype html>
<html lang="ko">
  <head>
    {GTM}
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(art['title'])} · NOAH 칼럼</title>
    <meta name="description" content="{esc(art['desc'])}" />
    <link rel="canonical" href="{SITE}/columns/{art['slug']}" />
    {prev_link}{next_link}<meta property="og:type" content="article" />
    <meta property="og:title" content="{esc(art['title'])}" />
    <meta property="og:description" content="{esc(art['desc'])}" />
    <meta property="og:url" content="{SITE}/columns/{art['slug']}" />
    <meta property="og:site_name" content="{BRAND}" />
    <meta property="og:image" content="{SITE}/assets/images/og/{art['slug']}.png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:locale" content="ko_KR" />
    <meta property="article:published_time" content="{art['date']}" />
    <meta property="article:section" content="{esc(cat)}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{esc(art['title'])}" />
    <meta name="twitter:description" content="{esc(art['desc'])}" />
    <meta name="twitter:image" content="{SITE}/assets/images/og/{art['slug']}.png" />
    {HEAD_COMMON}
    <link rel="stylesheet" href="/assets/css/common.css" />
    <style>
{STYLE}
    </style>
    <script type="application/ld+json">{json.dumps(ld_article, ensure_ascii=False)}</script>
    <script type="application/ld+json">{json.dumps(ld_crumb, ensure_ascii=False)}</script>
  </head>
  <body>
    {GTM_NOSCRIPT}
    <div class="bg-blobs" aria-hidden="true"></div>
{NAV}

    <main class="container-x py-10" style="max-width: 760px">
      <nav class="text-xs mb-7" style="color: var(--text-quiet)" aria-label="위치">
        <a href="/" class="hover:text-[color:var(--text)]">홈</a> ·
        <a href="/columns/" class="hover:text-[color:var(--text)]">칼럼</a> ·
        <a href="/columns/topic/{cl}" class="hover:text-[color:var(--text)]">{esc(cat)}</a>
      </nav>

      <p class="text-[11px] font-bold tracking-[0.2em] mb-4" style="color: var(--accent)">{esc(cat).upper()}</p>
      <h1 class="disp" style="font-size: clamp(28px, 5.6vw, 42px); line-height: 1.32">{esc(art['title'])}</h1>
      <p class="mt-5 text-[15px] leading-8" style="color: var(--text-dim)">{esc(art['desc'])}</p>
      <div class="flex items-center gap-3 mt-6 pb-8 text-xs col-head" style="color: var(--text-quiet)">
        <time datetime="{art['date']}">{art['date'].replace('-', '.')}</time>
        <span>·</span><span>약 {art.get('readMin', 5)}분</span>
        <span>·</span><span>NOAH 편집팀</span>
      </div>

{toc_html}

      <article class="prose mt-10">
{body}
      </article>

      <div class="flex gap-2 flex-wrap mt-10">{tags}</div>

      <section class="cta-box mt-14">
        <h2 class="disp text-xl">홈페이지, 7일이면 열립니다</h2>
        <p class="mt-3 text-sm leading-7" style="color: var(--text-dim)">
          18개 업종 레퍼런스 중 마음에 드는 디자인을 고르시면, 그 위에 사장님 브랜드를 옮겨 드립니다.
          199,000원(부가세 별도) · 1년 무료 호스팅 · 1년 무제한 텍스트 수정 포함.
        </p>
        <div class="flex gap-2.5 mt-6 flex-wrap">
          <a href="/references" class="px-6 py-3 rounded-full font-bold text-sm" style="background:var(--accent); color:var(--on-accent)">레퍼런스 보기</a>
          <a href="/contact" class="px-6 py-3 rounded-full font-bold text-sm" style="border:1px solid var(--line); color:var(--text)">무료 상담</a>
        </div>
      </section>

{pn_html}

      <section class="mt-14">
        <h2 class="disp text-lg mb-4">함께 읽으면 좋은 글</h2>
        <div class="rel grid sm:grid-cols-2 gap-3">
{rel_html}
        </div>
      </section>

      <div class="mt-12 text-center">
        <a href="/columns/topic/{cl}" class="hub-pill">{esc(cat)} 글 전체 보기 →</a>
      </div>
    </main>
{footer()}
  </body>
</html>
'''


def build_hub(cl, arts, all_cols):
    meta = CLUSTERS[cl]
    cards = '\n'.join(f'''          <a class="card" href="/columns/{a['slug']}">
            <span class="cat">{esc(meta['name'])}</span>
            <h3>{esc(a['title'])}</h3>
            <p>{esc(a['desc'])}</p>
            <p class="meta">{a['date'].replace('-', '.')} · 약 {a.get('readMin', 5)}분</p>
          </a>''' for a in arts)

    others = '\n'.join(
        f'<a href="/columns/topic/{k}" class="hub-pill">{esc(v["name"])}</a>'
        for k, v in CLUSTERS.items() if k != cl)

    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": meta['h'],
        "description": meta['lead'],
        "url": f"{SITE}/columns/topic/{cl}",
        "inLanguage": "ko-KR",
        "isPartOf": {"@type": "Blog", "name": "NOAH 홈페이지 제작 칼럼", "@id": f"{SITE}/columns/"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(arts),
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": a['title'],
                 "url": f"{SITE}/columns/{a['slug']}"} for i, a in enumerate(arts)
            ],
        },
    }
    ld_crumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "칼럼", "item": f"{SITE}/columns/"},
            {"@type": "ListItem", "position": 3, "name": meta['name'], "item": f"{SITE}/columns/topic/{cl}"},
        ],
    }

    return f'''<!doctype html>
<html lang="ko">
  <head>
    {GTM}
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(meta['h'])} — {esc(meta['name'])} 칼럼 {len(arts)}편 · NOAH</title>
    <meta name="description" content="{esc(meta['lead'])} {esc(meta['name'])} 관련 칼럼 {len(arts)}편을 모았습니다." />
    <link rel="canonical" href="{SITE}/columns/topic/{cl}" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="{esc(meta['h'])} · NOAH 칼럼" />
    <meta property="og:description" content="{esc(meta['lead'])}" />
    <meta property="og:url" content="{SITE}/columns/topic/{cl}" />
    <meta property="og:locale" content="ko_KR" />
    {HEAD_COMMON}
    <link rel="stylesheet" href="/assets/css/common.css" />
    <style>
{STYLE}
    </style>
    <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
    <script type="application/ld+json">{json.dumps(ld_crumb, ensure_ascii=False)}</script>
  </head>
  <body>
    {GTM_NOSCRIPT}
    <div class="bg-blobs" aria-hidden="true"></div>
{NAV}

    <main class="container-x py-12" style="max-width: 1100px">
      <nav class="text-xs mb-8" style="color: var(--text-quiet)" aria-label="위치">
        <a href="/" class="hover:text-[color:var(--text)]">홈</a> ·
        <a href="/columns/" class="hover:text-[color:var(--text)]">칼럼</a> ·
        <span>{esc(meta['name'])}</span>
      </nav>

      <div class="max-w-2xl">
        <p class="text-[11px] font-bold tracking-[0.2em]" style="color: var(--accent)">{esc(meta['name']).upper()}</p>
        <h1 class="disp mt-4" style="font-size: clamp(28px, 5vw, 44px); line-height: 1.3">{esc(meta['h'])}</h1>
        <p class="mt-6 text-[15px] leading-8" style="color: var(--text-dim)">{esc(meta['lead'])}</p>
        <p class="mt-4 text-sm" style="color: var(--text-quiet)">총 {len(arts)}편</p>
      </div>

      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-12">
{cards}
      </div>

      <section class="mt-16 pt-10" style="border-top:1px solid var(--line)">
        <h2 class="disp text-lg mb-5">다른 주제도 살펴보기</h2>
        <div class="flex gap-2 flex-wrap">
{others}
        </div>
      </section>
    </main>
{footer()}
  </body>
</html>
'''


def build_index(cols):
    data = [{
        'slug': a['slug'], 'title': a['title'], 'desc': a['desc'],
        'cluster': a['cluster'], 'cat': CLUSTERS[a['cluster']]['name'],
        'date': a['date'], 'readMin': a.get('readMin', 5),
        'kw': a['kw'], 'tags': a.get('tags', []),
    } for a in cols]

    chips = '\n'.join(
        f'<button class="chip" data-c="{k}" aria-pressed="false">{esc(v["name"])}</button>'
        for k, v in CLUSTERS.items())

    by_cat = {}
    for a in cols:
        by_cat.setdefault(a['cluster'], []).append(a)

    hub_cards = '\n'.join(f'''        <a class="card" href="/columns/topic/{k}">
          <span class="cat">{esc(v['name'])} · {len(by_cat.get(k, []))}편</span>
          <h3>{esc(v['h'])}</h3>
          <p>{esc(v['lead'])}</p>
        </a>''' for k, v in CLUSTERS.items() if by_cat.get(k))

    static_list = '\n'.join(
        '        <section class="mb-8"><h2 class="disp text-base mb-3">' + esc(CLUSTERS[k]['name'])
        + f' <a href="/columns/topic/{k}" class="text-xs font-normal" style="color:var(--accent)">주제 전체 →</a></h2>'
        + '<ul class="grid sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">'
        + ''.join(f'<li><a href="/columns/{a["slug"]}" style="color:var(--text-dim)">{esc(a["title"])}</a></li>' for a in by_cat.get(k, []))
        + '</ul></section>'
        for k in CLUSTERS if by_cat.get(k))

    ld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "NOAH 홈페이지 제작 칼럼",
        "description": "홈페이지 제작 비용·업종별 제작·SEO·운영까지, 사장님이 실제로 궁금해하는 것들을 정리한 100편의 칼럼.",
        "url": f"{SITE}/columns/",
        "inLanguage": "ko-KR",
        "publisher": {"@type": "Organization", "name": BRAND, "url": SITE},
    }
    ld_crumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "칼럼", "item": f"{SITE}/columns/"},
        ],
    }

    return f'''<!doctype html>
<html lang="ko">
  <head>
    {GTM}
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>홈페이지 제작 칼럼 100선 · NOAH 노아홈페이지</title>
    <meta name="description" content="홈페이지 제작 비용부터 업종별 제작, SEO, 운영·유지보수까지. 사장님이 실제로 궁금해하는 것들을 정리한 100편의 칼럼입니다." />
    <link rel="canonical" href="{SITE}/columns/" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="홈페이지 제작 칼럼 100선 · NOAH" />
    <meta property="og:description" content="비용·업종별·SEO·운영까지, 홈페이지 제작의 모든 것." />
    <meta property="og:url" content="{SITE}/columns/" />
    <meta property="og:locale" content="ko_KR" />
    {HEAD_COMMON}
    <link rel="stylesheet" href="/assets/css/common.css" />
    <style>
{STYLE}
    </style>
    <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
    <script type="application/ld+json">{json.dumps(ld_crumb, ensure_ascii=False)}</script>
  </head>
  <body>
    {GTM_NOSCRIPT}
    <div class="bg-blobs" aria-hidden="true"></div>
{NAV}

    <main class="container-x py-12" style="max-width: 1100px">
      <div class="text-center mb-12">
        <p class="text-xs tracking-[0.24em] mb-4" style="color: var(--text-quiet)">NOAH COLUMNS</p>
        <h1 class="disp" style="font-size: clamp(30px, 5.4vw, 46px); line-height: 1.3">홈페이지 제작,<br />궁금한 것부터 하나씩</h1>
        <p class="mt-6 text-[15px] leading-8" style="color: var(--text-dim)">
          비용·업종별 제작·검색 노출·운영까지 <strong style="color:var(--text)">100편</strong>으로 정리했습니다.<br />
          광고가 아니라, 사장님이 판단하실 수 있게 쓴 글입니다.
        </p>
      </div>

      <!-- 토픽 허브 -->
      <section class="mb-14">
        <h2 class="disp text-lg mb-5">주제별로 보기</h2>
        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
{hub_cards}
        </div>
      </section>

      <div class="mb-6">
        <label class="sr-only" for="q">칼럼 검색</label>
        <input class="f-search" id="q" type="search" placeholder="검색 — 예: 비용, 치과, SEO, 도메인" autocomplete="off" />
      </div>

      <div class="flex gap-2 overflow-x-auto pb-6" role="group" aria-label="분야 필터" id="chips" style="scrollbar-width:none">
        <button class="chip" data-c="all" aria-pressed="true">전체</button>
{chips}
      </div>

      <p class="text-xs mb-5" style="color: var(--text-quiet)" id="count" role="status" aria-live="polite"></p>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4" id="grid"></div>
      <div class="flex gap-2 justify-center mt-12 pager flex-wrap" id="pager"></div>

      <!-- JS 미실행 환경 및 크롤러용 전체 목록 (JS 로드 시 숨김) -->
      <div id="static-list">
{static_list}
      </div>
    </main>
{footer()}

    <script>
      const COLUMNS = {json.dumps(data, ensure_ascii=False)};
      const PER = 12;
      let cat = 'all', q = '', page = 1;
      const $ = (s) => document.querySelector(s);

      function filtered() {{
        const kw = q.trim().toLowerCase();
        return COLUMNS.filter(c => {{
          if (cat !== 'all' && c.cluster !== cat) return false;
          if (!kw) return true;
          return (c.title + c.desc + c.kw + c.cat + c.tags.join(' ')).toLowerCase().includes(kw);
        }});
      }}

      function render() {{
        const list = filtered();
        const pages = Math.max(1, Math.ceil(list.length / PER));
        page = Math.min(page, pages);
        const slice = list.slice((page - 1) * PER, page * PER);

        $('#count').textContent = list.length ? `총 ${{list.length}}편 · ${{page}}/${{pages}} 페이지` : '';
        $('#grid').innerHTML = slice.length ? slice.map(c => `
          <a class="card" href="/columns/${{c.slug}}">
            <span class="cat">${{c.cat}}</span>
            <h3>${{c.title}}</h3>
            <p>${{c.desc}}</p>
            <p class="meta">${{c.date.replace(/-/g, '.')}} · 약 ${{c.readMin}}분</p>
          </a>`).join('')
          : `<p class="sm:col-span-2 lg:col-span-3 text-center py-20" style="color:var(--text-quiet)">검색 결과가 없습니다. 다른 키워드로 찾아보세요.</p>`;

        let p = '';
        if (pages > 1) {{
          p += `<button ${{page === 1 ? 'disabled' : ''}} data-p="${{page - 1}}" aria-label="이전 페이지">←</button>`;
          for (let i = 1; i <= pages; i++) {{
            if (i === 1 || i === pages || Math.abs(i - page) <= 1) {{
              p += `<button data-p="${{i}}" aria-current="${{i === page}}">${{i}}</button>`;
            }} else if (Math.abs(i - page) === 2) {{
              p += `<span style="color:var(--text-quiet); align-self:center; padding:0 4px">…</span>`;
            }}
          }}
          p += `<button ${{page === pages ? 'disabled' : ''}} data-p="${{page + 1}}" aria-label="다음 페이지">→</button>`;
        }}
        $('#pager').innerHTML = p;
        $('#pager').querySelectorAll('button[data-p]').forEach(b => b.onclick = () => {{
          page = +b.dataset.p; render();
          window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});
      }}

      $('#chips').querySelectorAll('.chip').forEach(b => b.onclick = () => {{
        $('#chips').querySelectorAll('.chip').forEach(x => x.setAttribute('aria-pressed', x === b));
        cat = b.dataset.c; page = 1; render();
      }});
      let t;
      $('#q').addEventListener('input', e => {{
        clearTimeout(t);
        t = setTimeout(() => {{ q = e.target.value; page = 1; render(); }}, 200);
      }});
      document.getElementById('static-list').style.display = 'none';
      render();
    </script>
  </body>
</html>
'''


def build_rss(cols):
    items = []
    for a in cols[:40]:
        d = date.fromisoformat(a['date'])
        items.append(f'''    <item>
      <title>{esc(a['title'])}</title>
      <link>{SITE}/columns/{a['slug']}</link>
      <guid isPermaLink="true">{SITE}/columns/{a['slug']}</guid>
      <description>{esc(a['desc'])}</description>
      <category>{esc(CLUSTERS[a['cluster']]['name'])}</category>
      <pubDate>{d.strftime('%a, %d %b %Y')} 09:00:00 +0900</pubDate>
    </item>''')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>NOAH 홈페이지 제작 칼럼</title>
    <link>{SITE}/columns/</link>
    <atom:link href="{SITE}/columns/feed.xml" rel="self" type="application/rss+xml" />
    <description>홈페이지 제작 비용·업종별 제작·SEO·운영까지 정리한 칼럼</description>
    <language>ko</language>
{chr(10).join(items)}
  </channel>
</rss>
'''


def build_og_images(cols):
    """OG 이미지 1200×630 생성 (Pretendard OTF 필요)"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print('  · Pillow 없음 — OG 이미지 건너뜀'); return 0
    font_dirs = [
        os.environ.get('PRETENDARD_DIR', ''),
        '/tmp/shot/node_modules/pretendard/dist/public/static',
    ]
    fp = None
    for d in font_dirs:
        if d and os.path.exists(os.path.join(d, 'Pretendard-Bold.otf')):
            fp = d; break
    if not fp:
        print('  · Pretendard OTF 없음 — OG 이미지 건너뜀 (PRETENDARD_DIR 지정)'); return 0

    os.makedirs(OG_DIR, exist_ok=True)
    f_title = ImageFont.truetype(os.path.join(fp, 'Pretendard-Bold.otf'), 62)
    f_cat = ImageFont.truetype(os.path.join(fp, 'Pretendard-Bold.otf'), 26)
    f_brand = ImageFont.truetype(os.path.join(fp, 'Pretendard-SemiBold.otf'), 28)

    for a in cols:
        img = Image.new('RGB', (1200, 630), '#0B0C0F')
        d = ImageDraw.Draw(img)
        # 상단 브랜드 그라디언트 바
        for x in range(1200):
            t = x / 1200
            d.line([(x, 0), (x, 7)], fill=(int(255 + (201 - 255) * t),
                                           int(98 + (255 - 98) * t),
                                           int(61 + (74 - 61) * t)))
        d.text((72, 78), CLUSTERS[a['cluster']]['name'].upper(), font=f_cat, fill='#C9FF4A')
        # 제목 줄바꿈 (어절 단위)
        words, lines, cur = a['title'].split(' '), [], ''
        for w in words:
            test = (cur + ' ' + w).strip()
            if d.textlength(test, font=f_title) > 1050 and cur:
                lines.append(cur); cur = w
            else:
                cur = test
        if cur: lines.append(cur)
        y = 175
        for ln in lines[:4]:
            d.text((72, y), ln, font=f_title, fill='#F2F0E9'); y += 82
        d.line([(72, 540), (1128, 540)], fill='#2A2C31', width=1)
        d.text((72, 562), 'NOAH · 노아홈페이지', font=f_brand, fill='#8A8880')
        url = 'noahhomepage.co.kr'
        d.text((1128 - d.textlength(url, font=f_brand), 562), url, font=f_brand, fill='#5A5852')
        img.save(os.path.join(OG_DIR, a['slug'] + '.png'), optimize=True)
    return len(cols)


def update_sitemap(cols):
    p = os.path.join(ROOT, 'sitemap.xml')
    sm = open(p, encoding='utf-8').read()
    sm = re.sub(r'\s*<url><loc>https://noahhomepage\.co\.kr/columns[^<]*</loc>.*?</url>', '', sm)
    today = cols[0]['date'] if cols else date.today().isoformat()
    add = [f'  <url><loc>{SITE}/columns/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>']
    for cl in CLUSTERS:
        add.append(f'  <url><loc>{SITE}/columns/topic/{cl}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    for a in cols:
        add.append(f'  <url><loc>{SITE}/columns/{a["slug"]}</loc><lastmod>{a["date"]}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>')
    sm = sm.replace('</urlset>', '\n'.join(add) + '\n</urlset>')
    open(p, 'w', encoding='utf-8').write(sm)
    return sm.count('<url>')


def main():
    cols = load_all()
    slugset = {a['slug'] for a in cols}
    by_cluster = {}
    for a in cols:
        by_cluster.setdefault(a['cluster'], []).append(a)

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(HUB_DIR, exist_ok=True)

    for a in cols:
        with open(os.path.join(OUT_DIR, a['slug'] + '.html'), 'w', encoding='utf-8') as f:
            f.write(build_article(a, cols, slugset, by_cluster))

    for cl, arts in by_cluster.items():
        with open(os.path.join(HUB_DIR, cl + '.html'), 'w', encoding='utf-8') as f:
            f.write(build_hub(cl, arts, cols))

    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(build_index(cols))
    with open(os.path.join(OUT_DIR, 'feed.xml'), 'w', encoding='utf-8') as f:
        f.write(build_rss(cols))

    n_url = update_sitemap(cols)
    print(f'✓ 칼럼 {len(cols)}편 · 토픽 허브 {len(by_cluster)}개 · 목록 · RSS')
    print(f'✓ sitemap {n_url} URL (lastmod 포함)')

    if '--og' in sys.argv:
        n = build_og_images(cols)
        print(f'✓ OG 이미지 {n}장')
    return cols


if __name__ == '__main__':
    main()
