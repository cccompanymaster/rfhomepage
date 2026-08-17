#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOAH 칼럼 정적 생성기
- content/columns/batch-*.json (칼럼 본문) + content/keywords-100.json (메타)
- 출력: columns/<slug>.html (개별), columns/index.html (목록), sitemap 갱신
사용: python3 scripts/build-columns.py
"""
import json, glob, os, re, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "columns")
SITE = "https://noahhomepage.co.kr"
TODAY = "2026-08-17"

CLUSTERS = {
    "cost": "비용·견적", "guide": "제작 가이드", "industry": "업종별 제작",
    "seo": "SEO·검색노출", "compare": "제작 방식 비교", "ops": "운영·유지보수",
    "design": "디자인·기획", "local": "지역별 제작",
}

GTM = """<!-- Google Tag Manager -->
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
    </script>"""

GTM_NOSCRIPT = """<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WZWCZTKJ"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>"""

HEAD_COMMON = """<link rel="icon" href="/favicon.ico" sizes="any" />
    <link rel="icon" type="image/png" sizes="512x512" href="/favicon.png" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" />
    <link rel="stylesheet" href="/assets/css/common.css" />
    <meta name="theme-color" content="#0B0C0F" />"""

ARTICLE_CSS = """
      body { background: var(--bg); color: var(--text); }
      .disp { font-family: 'Space Grotesk', 'Pretendard Variable', sans-serif; letter-spacing: -0.03em; font-weight: 700; }
      .container-x { max-width: 760px; margin: 0 auto; padding: 0 20px; }
      .wide { max-width: 1100px; }
      .crumb { font-size: 12.5px; color: var(--text-quiet); }
      .crumb a { color: var(--text-dim); }
      .crumb a:hover { color: var(--text); }
      .chip { display:inline-block; padding: 5px 13px; border-radius: 999px; font-size: 12px; font-weight: 700; background: rgba(255,98,61,.14); color: #ffb39d; }
      article.prose { font-size: 16.5px; line-height: 1.9; color: var(--text-dim); }
      article.prose > p:first-of-type { font-size: 17.5px; color: var(--text); }
      article.prose h2 { font-size: 24px; font-weight: 800; letter-spacing: -0.02em; color: var(--text); margin: 44px 0 14px; padding-top: 22px; border-top: 1px solid var(--line-soft); }
      article.prose h3 { font-size: 19px; font-weight: 700; color: var(--text); margin: 30px 0 10px; }
      article.prose p { margin: 0 0 16px; }
      article.prose ul, article.prose ol { margin: 0 0 18px; padding-left: 22px; }
      article.prose ul { list-style: disc; } article.prose ol { list-style: decimal; }
      article.prose li { margin: 6px 0; }
      article.prose li::marker { color: var(--accent-deep); }
      article.prose strong { color: var(--text); font-weight: 700; }
      article.prose blockquote { border-left: 3px solid var(--accent-deep); padding: 4px 0 4px 18px; margin: 20px 0; color: var(--text); background: rgba(255,98,61,.05); border-radius: 0 10px 10px 0; }
      article.prose code { background: rgba(255,255,255,.08); padding: 2px 7px; border-radius: 6px; font-size: 14px; }
      article.prose table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14.5px; display: block; overflow-x: auto; }
      article.prose th, article.prose td { border: 1px solid var(--line); padding: 10px 12px; text-align: left; }
      article.prose th { background: var(--bg-soft); color: var(--text); font-weight: 700; white-space: nowrap; }
      .rel-card { display: block; border: 1px solid var(--line); border-radius: 14px; padding: 18px; background: var(--bg-soft); transition: transform .2s, border-color .2s; }
      .rel-card:hover { transform: translateY(-3px); border-color: rgba(255,255,255,.25); }
      .cta-box { border: 1px solid rgba(201,255,74,.3); border-radius: 18px; padding: 30px 26px; background: linear-gradient(160deg, rgba(201,255,74,.07), rgba(255,255,255,.01)); text-align: center; }
      .btn-lime { display: inline-flex; align-items: center; gap: 8px; padding: 13px 26px; border-radius: 999px; background: var(--accent); color: #10130F; font-weight: 800; font-size: 14.5px; }
      .btn-line { display: inline-flex; align-items: center; gap: 8px; padding: 13px 24px; border-radius: 999px; border: 1px solid var(--line); color: var(--text); font-weight: 700; font-size: 14.5px; }
"""

HEADER_HTML = """<header class="container-x wide pt-7 pb-3" style="display:flex;align-items:center;justify-content:space-between">
      <a href="/" style="display:inline-flex;align-items:center;gap:8px;font-weight:700">
        <span style="width:26px;height:26px;border-radius:7px;background:linear-gradient(135deg,#FF623D,#C9FF4A);display:inline-block"></span>
        NOAH <span style="color:var(--text-quiet);font-weight:500;font-size:13px">· 칼럼</span>
      </a>
      <nav style="display:flex;gap:18px;font-size:13.5px;color:var(--text-dim)">
        <a href="/columns/" style="color:var(--text)">칼럼</a>
        <a href="/#showroom">레퍼런스</a>
        <a href="/options">옵션·가격</a>
        <a href="/#consult">상담</a>
      </nav>
    </header>"""

FOOTER_HTML = """<footer class="container-x wide" style="padding:40px 20px 60px;border-top:1px solid var(--line-soft);margin-top:60px">
      <p style="font-size:12px;color:var(--text-quiet);line-height:1.8">
        NOAH 노아홈페이지 · 씨씨컴퍼니(CC Company) · 대표 채희준 · 사업자등록번호 275-05-01613<br />
        본 칼럼은 일반적인 정보 제공 목적이며, 법률·세무 등 전문 분야는 반드시 해당 전문가와 확인하시기 바랍니다.
      </p>
    </footer>"""


def esc(s):
    return html.escape(str(s), quote=True)


def load_articles():
    arts = []
    for p in sorted(glob.glob(os.path.join(ROOT, "content/columns/batch-*.json"))):
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        for a in data:
            arts.append(a)
    # keywords-100 순서 기준 정렬
    with open(os.path.join(ROOT, "content/keywords-100.json"), encoding="utf-8") as f:
        order = {k["slug"]: k["n"] for k in json.load(f)["keywords"]}
    arts.sort(key=lambda a: order.get(a["slug"], 999))
    for a in arts:
        a["n"] = order.get(a["slug"], 0)
    return arts


def related(arts, art, count_same=3, count_other=1):
    same = [a for a in arts if a["cluster"] == art["cluster"] and a["slug"] != art["slug"]]
    other = [a for a in arts if a["cluster"] != art["cluster"]]
    i = art["n"]
    same_pick = [same[(i + k) % len(same)] for k in range(min(count_same, len(same)))] if same else []
    other_pick = [other[(i * 7) % len(other)]] if other else []
    # dedup
    seen, out = set(), []
    for a in same_pick + other_pick:
        if a["slug"] not in seen:
            seen.add(a["slug"]); out.append(a)
    return out


def sanitize_body(b):
    # 스크립트/이벤트 핸들러 방어적 제거
    b = re.sub(r"<script[\s\S]*?</script>", "", b, flags=re.I)
    b = re.sub(r"\son\w+\s*=\s*\"[^\"]*\"", "", b, flags=re.I)
    return b


def build_article(arts, a):
    rel = related(arts, a)
    rel_html = "\n".join(
        f'<a class="rel-card" href="/columns/{r["slug"]}">'
        f'<span class="chip" style="font-size:10.5px">{esc(CLUSTERS[r["cluster"]])}</span>'
        f'<p style="font-weight:700;margin-top:10px;font-size:15px;line-height:1.5">{esc(r["title"])}</p></a>'
        for r in rel
    )
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"], "description": a["desc"],
        "datePublished": TODAY, "dateModified": TODAY,
        "author": {"@type": "Organization", "name": "NOAH 노아홈페이지"},
        "publisher": {"@type": "Organization", "name": "NOAH 노아홈페이지"},
        "mainEntityOfPage": f"{SITE}/columns/{a['slug']}",
    }, ensure_ascii=False)
    breadcrumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "칼럼", "item": SITE + "/columns/"},
            {"@type": "ListItem", "position": 3, "name": a["title"]},
        ],
    }, ensure_ascii=False)
    tags = " · ".join(esc(t) for t in a.get("tags", []))
    return f"""<!doctype html>
<html lang="ko">
  <head>
    {GTM}
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(a["title"])} · NOAH 칼럼</title>
    <meta name="description" content="{esc(a["desc"])}" />
    <link rel="canonical" href="{SITE}/columns/{a["slug"]}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{esc(a["title"])}" />
    <meta property="og:description" content="{esc(a["desc"])}" />
    <meta property="og:url" content="{SITE}/columns/{a["slug"]}" />
    <meta property="og:locale" content="ko_KR" />
    <meta name="twitter:card" content="summary" />
    {HEAD_COMMON}
    <style>{ARTICLE_CSS}</style>
    <script type="application/ld+json">{jsonld}</script>
    <script type="application/ld+json">{breadcrumb}</script>
  </head>
  <body>
    {GTM_NOSCRIPT}
    {HEADER_HTML}
    <main class="container-x" style="padding-top:28px">
      <p class="crumb"><a href="/">홈</a> › <a href="/columns/">칼럼</a> › {esc(CLUSTERS[a["cluster"]])}</p>
      <div style="margin-top:22px"><span class="chip">{esc(CLUSTERS[a["cluster"]])}</span></div>
      <h1 class="disp" style="font-size:clamp(26px,5vw,38px);line-height:1.35;margin-top:14px">{esc(a["title"])}</h1>
      <p style="margin-top:14px;font-size:12.5px;color:var(--text-quiet)">NOAH 칼럼 · {TODAY} · 읽는 시간 약 {a.get("readMin", 5)}분{(" · " + tags) if tags else ""}</p>
      <article class="prose" style="margin-top:34px">
        {sanitize_body(a["body"])}
      </article>

      <div class="cta-box" style="margin-top:52px">
        <p class="disp" style="font-size:20px">홈페이지, 고민만 길어지고 있다면</p>
        <p style="font-size:14px;color:var(--text-dim);margin-top:8px">NOAH는 17개 업종 레퍼런스 중 골라 7일 안에 오픈합니다. 199,000원(부가세 별도).</p>
        <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:18px">
          <a class="btn-lime" href="/#consult">무료 상담 신청 →</a>
          <a class="btn-line" href="/#showroom">레퍼런스 구경하기</a>
        </div>
      </div>

      <section style="margin-top:52px">
        <h2 class="disp" style="font-size:19px;margin-bottom:16px">함께 읽으면 좋은 글</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">
          {rel_html}
        </div>
      </section>
    </main>
    {FOOTER_HTML}
  </body>
</html>
"""


def build_index(arts):
    cards = "\n".join(
        f'<a class="rel-card col-card" href="/columns/{a["slug"]}" data-cluster="{a["cluster"]}" data-text="{esc(a["title"])} {esc(a["kw"])}">'
        f'<span class="chip" style="font-size:10.5px">{esc(CLUSTERS[a["cluster"]])}</span>'
        f'<p style="font-weight:700;margin-top:10px;font-size:15.5px;line-height:1.5">{esc(a["title"])}</p>'
        f'<p style="margin-top:8px;font-size:13px;color:var(--text-quiet);line-height:1.6">{esc(a["desc"][:64])}…</p></a>'
        for a in arts
    )
    chips = '<button class="fchip" data-c="all" aria-pressed="true">전체</button>' + "".join(
        f'<button class="fchip" data-c="{k}" aria-pressed="false">{esc(v)}</button>' for k, v in CLUSTERS.items()
    )
    return f"""<!doctype html>
<html lang="ko">
  <head>
    {GTM}
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>홈페이지 제작 칼럼 {len(arts)}선 · NOAH</title>
    <meta name="description" content="홈페이지 제작 비용부터 업종별 가이드, SEO, 운영까지 — 사장님을 위한 홈페이지 제작 칼럼 {len(arts)}편. NOAH 노아홈페이지." />
    <link rel="canonical" href="{SITE}/columns/" />
    <meta property="og:title" content="홈페이지 제작 칼럼 · NOAH" />
    <meta property="og:description" content="비용·업종별·SEO·운영 — 사장님을 위한 실전 가이드 {len(arts)}편." />
    <meta property="og:locale" content="ko_KR" />
    {HEAD_COMMON}
    <style>{ARTICLE_CSS}
      .fchip {{ padding: 8px 16px; border-radius: 999px; border: 1px solid var(--line); font-size: 13px; font-weight: 600; color: var(--text-dim); background: none; transition: all .2s; white-space: nowrap; cursor: pointer; }}
      .fchip[aria-pressed="true"] {{ background: var(--text); color: #0B0C0F; border-color: var(--text); }}
      .search {{ width: 100%; max-width: 380px; padding: 13px 18px; border-radius: 999px; border: 1px solid var(--line); background: var(--bg-soft); color: var(--text); font-size: 14.5px; }}
      .search:focus {{ outline: none; border-color: var(--accent-deep); }}
    </style>
  </head>
  <body>
    {GTM_NOSCRIPT}
    {HEADER_HTML}
    <main class="container-x wide" style="padding-top:36px">
      <p style="font-size:11px;letter-spacing:.24em;color:var(--text-quiet)">NOAH COLUMNS</p>
      <h1 class="disp" style="font-size:clamp(28px,5vw,44px);margin-top:12px">홈페이지 제작,<br />궁금한 것부터 읽어보세요.</h1>
      <p style="margin-top:14px;color:var(--text-dim);font-size:15px">비용 · 업종별 가이드 · SEO · 운영까지 — 사장님 눈높이로 쓴 {len(arts)}편.</p>
      <div style="display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin-top:28px">
        <input class="search" id="q" type="search" placeholder="키워드 검색 — 예: 비용, 치과, SEO" aria-label="칼럼 검색" />
      </div>
      <div style="display:flex;gap:8px;overflow-x:auto;padding:18px 0 6px" id="chips">{chips}</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;margin-top:18px" id="grid">
        {cards}
      </div>
      <p id="empty" style="display:none;text-align:center;color:var(--text-quiet);padding:60px 0">검색 결과가 없습니다.</p>
    </main>
    {FOOTER_HTML}
    <script>
      const cards = [...document.querySelectorAll('.col-card')];
      const chips = [...document.querySelectorAll('.fchip')];
      const q = document.getElementById('q');
      let cluster = 'all';
      function apply() {{
        const term = q.value.trim().toLowerCase();
        let vis = 0;
        cards.forEach(c => {{
          const ok = (cluster === 'all' || c.dataset.cluster === cluster)
            && (!term || c.dataset.text.toLowerCase().includes(term));
          c.style.display = ok ? '' : 'none';
          if (ok) vis++;
        }});
        document.getElementById('empty').style.display = vis ? 'none' : '';
      }}
      chips.forEach(ch => ch.onclick = () => {{
        chips.forEach(x => x.setAttribute('aria-pressed', x === ch));
        cluster = ch.dataset.c; apply();
      }});
      q.addEventListener('input', apply);
    </script>
  </body>
</html>
"""


def update_sitemap(arts):
    p = os.path.join(ROOT, "sitemap.xml")
    with open(p, encoding="utf-8") as f:
        sm = f.read()
    # 기존 칼럼 항목 제거 후 재삽입 (멱등)
    sm = re.sub(r"  <url><loc>[^<]*/columns[^<]*</loc>.*?</url>\n", "", sm)
    entries = f'  <url><loc>{SITE}/columns/</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>\n'
    entries += "".join(
        f'  <url><loc>{SITE}/columns/{a["slug"]}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>\n'
        for a in arts
    )
    sm = sm.replace("</urlset>", entries + "</urlset>")
    with open(p, "w", encoding="utf-8") as f:
        f.write(sm)


def main():
    arts = load_articles()
    assert len(arts) == len({a["slug"] for a in arts}), "slug 중복!"
    os.makedirs(OUT, exist_ok=True)
    for a in arts:
        with open(os.path.join(OUT, a["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(build_article(arts, a))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_index(arts))
    update_sitemap(arts)
    print(f"생성 완료: 칼럼 {len(arts)}편 + 목록 1 + sitemap 갱신")
    # 분량 검증
    short = [(a["slug"], len(re.sub(r"<[^>]+>", "", a["body"]))) for a in arts if len(re.sub(r"<[^>]+>", "", a["body"])) < 900]
    if short:
        print("⚠ 분량 부족(<900자):", short)


if __name__ == "__main__":
    main()
