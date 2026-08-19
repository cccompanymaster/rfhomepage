#!/usr/bin/env python3
"""
칼럼 정적 페이지 빌더
  content/columns/batch-*.json  →  columns/<slug>.html (100편) + columns.html (목록)

실행: python3 tools/build_columns.py
"""
import json, glob, re, os, html
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'columns')
SITE = 'https://noahhomepage.co.kr'

CLUSTERS = {
    'cost':     '비용·견적',
    'guide':    '제작 가이드',
    'industry': '업종별 제작',
    'seo':      'SEO·검색노출',
    'compare':  '제작 방식 비교',
    'ops':      '운영·유지보수',
    'design':   '디자인·기획',
    'local':    '지역별 제작',
}

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

HEAD_COMMON = '''<link rel="icon" href="/favicon.ico" sizes="any" />
    <link rel="icon" type="image/png" sizes="512x512" href="/favicon.png" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <meta name="theme-color" content="#0B0C0F" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" />
    <script src="https://cdn.tailwindcss.com"></script>'''

STYLE = '''      body { background: var(--bg); color: var(--text); }
      .disp { font-family: 'Space Grotesk', 'Pretendard Variable', sans-serif; letter-spacing: -0.03em; font-weight: 700; }
      .col-head { border-bottom: 1px solid var(--line); }
      .chip { display:inline-flex; align-items:center; padding: 7px 15px; border-radius: 999px; border: 1px solid var(--line); font-size: 13px; font-weight: 600; color: var(--text-dim); background: transparent; transition: all .2s; white-space: nowrap; cursor: pointer; }
      .chip:hover { border-color: rgba(255,255,255,.3); color: var(--text); }
      .chip[aria-pressed="true"] { background: var(--accent); color: #10130F; border-color: var(--accent); }
      .card { display:block; border: 1px solid var(--line); border-radius: 16px; background: var(--bg-soft); padding: 22px; transition: transform .25s, border-color .25s; height: 100%; }
      .card:hover { transform: translateY(-3px); border-color: rgba(255,255,255,.26); }
      .card .cat { font-size: 11px; letter-spacing: .16em; color: var(--accent); font-weight: 700; text-transform: uppercase; }
      .card h3 { font-size: 17px; font-weight: 700; line-height: 1.4; margin: 10px 0 8px; }
      .card p { font-size: 13.5px; line-height: 1.7; color: var(--text-dim); }
      .card .meta { font-size: 12px; color: var(--text-quiet); margin-top: 14px; }
      .f-search { width: 100%; padding: 14px 18px; background: rgba(255,255,255,0.04); border: 1px solid var(--line); border-radius: 12px; color: var(--text); font-size: 15px; }
      .f-search:focus { outline: none; border-color: var(--accent-deep); box-shadow: 0 0 0 3px rgba(255,98,61,.18); }
      .pager button { min-width: 40px; height: 40px; border-radius: 10px; border: 1px solid var(--line); color: var(--text-dim); font-size: 14px; font-weight: 600; transition: all .2s; }
      .pager button:hover:not(:disabled) { border-color: rgba(255,255,255,.3); color: var(--text); }
      .pager button[aria-current="true"] { background: var(--accent); color: #10130F; border-color: var(--accent); }
      .pager button:disabled { opacity: .35; cursor: not-allowed; }

      /* 본문 타이포 */
      .prose { font-size: 16px; line-height: 1.95; color: var(--text-dim); }
      .prose h2 { font-family:'Space Grotesk','Pretendard Variable',sans-serif; font-size: clamp(21px, 3.4vw, 27px); font-weight: 700; letter-spacing: -0.02em; color: var(--text); margin: 46px 0 16px; padding-top: 22px; border-top: 1px solid var(--line-soft); }
      .prose h2:first-child { margin-top: 0; border-top: 0; padding-top: 0; }
      .prose h3 { font-size: 18px; font-weight: 700; color: var(--text); margin: 28px 0 10px; }
      .prose p { margin: 0 0 18px; }
      .prose strong { color: var(--text); font-weight: 700; }
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
      .cta-box { border: 1px solid rgba(201,255,74,.3); border-radius: 18px; background: linear-gradient(160deg, rgba(201,255,74,.06), rgba(255,255,255,0.01)); padding: 30px; }
      .rel a { display:block; border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; transition: border-color .2s, background .2s; }
      .rel a:hover { border-color: rgba(255,255,255,.28); background: var(--bg-soft); }'''

NAV = '''    <header class="container-x pt-8 pb-2 flex items-center justify-between gap-4">
      <a href="/" class="inline-flex items-center gap-2 text-sm shrink-0" style="color: var(--text-dim)">
        <span style="width:26px;height:26px;border-radius:7px;background:linear-gradient(135deg,#FF623D,#C9FF4A);display:inline-block"></span>
        <span class="font-semibold" style="color: var(--text)">NOAH</span>
        <span class="hidden sm:inline" style="color: var(--text-quiet)">· 칼럼</span>
      </a>
      <div class="flex items-center gap-2 shrink-0">
        <a href="/columns/" class="text-sm hidden sm:inline" style="color: var(--text-dim)">칼럼 목록</a>
        <a href="/#consult" class="text-sm font-bold px-5 py-2.5 rounded-full" style="background:var(--accent);color:#10130F">무료 상담</a>
      </div>
    </header>'''

FOOTER = '''    <footer class="container-x py-12 mt-16 text-center text-xs" style="border-top: 1px solid var(--line); color: var(--text-quiet)">
      <div class="flex gap-5 justify-center flex-wrap mb-4">
        <a href="/" class="hover:text-white">홈</a>
        <a href="/columns/" class="hover:text-white">칼럼</a>
        <a href="/options" class="hover:text-white">옵션 안내</a>
        <a href="/#consult" class="hover:text-white">상담 신청</a>
      </div>
      <p>NOAH · 노아홈페이지 — 씨씨컴퍼니(CC Company) · 대표: 채희준 · 사업자등록번호: 275-05-01613</p>
      <p class="mt-1">본 칼럼은 일반적인 정보 제공을 목적으로 하며, 법률·세무 등 전문 자문을 대체하지 않습니다.</p>
    </footer>'''


def esc(s):
    return html.escape(str(s), quote=True)


def load_all():
    cols = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'content/columns/batch-*.json'))):
        for a in json.load(open(f, encoding='utf-8')):
            cols[a['slug']] = a
    # 키워드 목록 순서대로 정렬 + 발행일 부여
    order = json.load(open(os.path.join(ROOT, 'content/keywords-100.json'), encoding='utf-8'))['keywords']
    base = date(2026, 8, 19)
    out = []
    for i, k in enumerate(order):
        a = cols.get(k['slug'])
        if not a:
            continue
        a['n'] = k['n']
        a['cluster'] = a.get('cluster') or k['cluster']
        # 최신 → 과거로 자연스럽게 분산 (2일 간격)
        a['date'] = (base - timedelta(days=i * 2)).isoformat()
        out.append(a)
    return out


def related(art, all_cols):
    """같은 클러스터 3편 + 다른 클러스터 1편"""
    same = [a for a in all_cols if a['cluster'] == art['cluster'] and a['slug'] != art['slug']]
    other = [a for a in all_cols if a['cluster'] != art['cluster']]
    idx = art['n']
    picks = [same[(idx + i) % len(same)] for i in range(min(3, len(same)))] if same else []
    if other:
        picks.append(other[(idx * 7) % len(other)])
    # 중복 제거
    seen, res = set(), []
    for p in picks:
        if p['slug'] not in seen:
            seen.add(p['slug']); res.append(p)
    return res[:4]


def build_article(art, all_cols):
    cat = CLUSTERS.get(art['cluster'], '칼럼')
    rels = related(art, all_cols)
    rel_html = '\n'.join(
        f'''        <a href="/columns/{r['slug']}">
          <span class="text-[11px] font-bold tracking-widest" style="color:var(--accent)">{esc(CLUSTERS.get(r['cluster'],''))}</span>
          <p class="text-sm font-bold mt-1.5 leading-6">{esc(r['title'])}</p>
        </a>''' for r in rels)

    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": art['title'],
        "description": art['desc'],
        "datePublished": art['date'],
        "dateModified": art['date'],
        "author": {"@type": "Organization", "name": "NOAH 노아홈페이지"},
        "publisher": {
            "@type": "Organization",
            "name": "NOAH 노아홈페이지",
            "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.png"}
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE}/columns/{art['slug']}"},
        "keywords": art['kw'],
    }
    crumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "칼럼", "item": f"{SITE}/columns/"},
            {"@type": "ListItem", "position": 3, "name": art['title'], "item": f"{SITE}/columns/{art['slug']}"},
        ],
    }

    tags = ' '.join(
        f'<span class="text-xs px-3 py-1.5 rounded-full" style="border:1px solid var(--line); color:var(--text-quiet)">#{esc(t)}</span>'
        for t in art.get('tags', []))

    return f'''<!doctype html>
<html lang="ko">
  <head>
    {GTM}
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(art['title'])} · NOAH 칼럼</title>
    <meta name="description" content="{esc(art['desc'])}" />
    <meta name="keywords" content="{esc(art['kw'])}, 홈페이지 제작, NOAH" />
    <link rel="canonical" href="{SITE}/columns/{art['slug']}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{esc(art['title'])}" />
    <meta property="og:description" content="{esc(art['desc'])}" />
    <meta property="og:url" content="{SITE}/columns/{art['slug']}" />
    <meta property="og:locale" content="ko_KR" />
    <meta name="twitter:card" content="summary_large_image" />
    {HEAD_COMMON}
    <link rel="stylesheet" href="/assets/css/common.css" />
    <style>
{STYLE}
    </style>
    <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
    <script type="application/ld+json">{json.dumps(crumb, ensure_ascii=False)}</script>
  </head>
  <body>
    {GTM_NOSCRIPT}
    <div class="bg-blobs" aria-hidden="true"></div>
{NAV}

    <main class="container-x py-10" style="max-width: 760px">
      <nav class="text-xs mb-7" style="color: var(--text-quiet)" aria-label="위치">
        <a href="/" class="hover:text-white">홈</a> ·
        <a href="/columns/" class="hover:text-white">칼럼</a> ·
        <span>{esc(cat)}</span>
      </nav>

      <p class="text-[11px] font-bold tracking-[0.2em] mb-4" style="color: var(--accent)">{esc(cat).upper()}</p>
      <h1 class="disp" style="font-size: clamp(28px, 5.6vw, 42px); line-height: 1.32">{esc(art['title'])}</h1>
      <p class="mt-5 text-[15px] leading-8" style="color: var(--text-dim)">{esc(art['desc'])}</p>
      <div class="flex items-center gap-3 mt-6 pb-8 text-xs col-head" style="color: var(--text-quiet)">
        <time datetime="{art['date']}">{art['date'].replace('-', '.')}</time>
        <span>·</span><span>약 {art.get('readMin', 5)}분</span>
        <span>·</span><span>NOAH 편집팀</span>
      </div>

      <article class="prose mt-10">
{art['body']}
      </article>

      <div class="flex gap-2 flex-wrap mt-10">{tags}</div>

      <section class="cta-box mt-14">
        <h2 class="disp text-xl">홈페이지, 7일이면 열립니다</h2>
        <p class="mt-3 text-sm leading-7" style="color: var(--text-dim)">
          17개 업종 레퍼런스 중 마음에 드는 디자인을 고르시면, 그 위에 사장님 브랜드를 옮겨 드립니다.
          199,000원(부가세 별도) · 1년 무료 호스팅 · 1년 무제한 텍스트 수정 포함.
        </p>
        <div class="flex gap-2.5 mt-6 flex-wrap">
          <a href="/#showroom" class="px-6 py-3 rounded-full font-bold text-sm" style="background:var(--accent); color:#10130F">레퍼런스 보기</a>
          <a href="/#consult" class="px-6 py-3 rounded-full font-bold text-sm" style="border:1px solid var(--line); color:var(--text)">무료 상담</a>
        </div>
      </section>

      <section class="mt-14">
        <h2 class="disp text-lg mb-4">함께 읽으면 좋은 글</h2>
        <div class="rel grid sm:grid-cols-2 gap-3">
{rel_html}
        </div>
      </section>

      <div class="mt-12 text-center">
        <a href="/columns/" class="text-sm underline underline-offset-4" style="color: var(--text-dim)">← 칼럼 전체 목록</a>
      </div>
    </main>
{FOOTER}
  </body>
</html>
'''


def build_index(cols):
    data = [{
        'slug': a['slug'], 'title': a['title'], 'desc': a['desc'],
        'cluster': a['cluster'], 'cat': CLUSTERS.get(a['cluster'], ''),
        'date': a['date'], 'readMin': a.get('readMin', 5),
        'kw': a['kw'], 'tags': a.get('tags', []),
    } for a in cols]

    by_cat = {}
    for a in cols:
        by_cat.setdefault(a['cluster'], []).append(a)
    static_list = '\n'.join(
        '        <section class="mb-8"><h2 class="disp text-base mb-3">' + esc(CLUSTERS[k]) + '</h2><ul class="grid sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">'
        + ''.join(f'<li><a href="/columns/{a["slug"]}" style="color:var(--text-dim)">{esc(a["title"])}</a></li>' for a in by_cat.get(k, []))
        + '</ul></section>'
        for k in CLUSTERS if by_cat.get(k))

    chips = '\n'.join(
        f'<button class="chip" data-c="{k}" aria-pressed="false">{esc(v)}</button>'
        for k, v in CLUSTERS.items())

    ld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "NOAH 홈페이지 제작 칼럼",
        "description": "홈페이지 제작 비용·업종별 제작·SEO·운영까지, 사장님이 실제로 궁금해하는 것들을 정리한 100편의 칼럼.",
        "url": f"{SITE}/columns/",
        "publisher": {"@type": "Organization", "name": "NOAH 노아홈페이지"},
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

      <!-- JS 미실행 환경 및 크롤러용 전체 목록 (JS 로드 시 숨김) -->
      <div id="static-list">
{static_list}
      </div>
      <div class="flex gap-2 justify-center mt-12 pager flex-wrap" id="pager"></div>
    </main>
{FOOTER}

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


def main():
    cols = load_all()
    os.makedirs(OUT_DIR, exist_ok=True)
    for a in cols:
        with open(os.path.join(OUT_DIR, a['slug'] + '.html'), 'w', encoding='utf-8') as f:
            f.write(build_article(a, cols))
    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(build_index(cols))
    print(f'✓ 칼럼 {len(cols)}편 + 목록 페이지 생성 완료')
    return cols


if __name__ == '__main__':
    main()
