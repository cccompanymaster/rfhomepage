"""
차트 HTML 생성기 — content/charts.json 의 정의를 정적 HTML로 바꿉니다.
build_charts.py(루트 페이지)와 build_columns.py(칼럼 본문)가 함께 씁니다.

원칙 (dataviz 스킬)
  - 강조형: 이야기의 주인공 한 줄만 브랜드 오렌지, 나머지는 회색
  - 막대 12px, 기준선 쪽은 각지고 값 쪽 끝만 4px 둥글게, 조각 사이 2px 틈
  - 격자선은 1px 실선, 눈에 덜 띄게
  - 값은 항상 글자로도 보임(툴팁은 보조) — 툴팁 내용은 data-vz-* 속성에 담고 JS가 textContent로 넣음
  - 끝이 열린 범위(…이상)는 화살표 끝, 경계가 흐린 범위(수일~수주)는 끝을 흐리게
색 검증: dataviz/scripts/validate_palette.js — 회색 #7a8394 + 오렌지 #e8431a (흰 배경),
         회색 #7d879b + 오렌지 #ee6430 (다크 카드 #131b2c). 회색이 채도 기준 미달인 건
         '나머지'를 뜻하는 강조형 회색이라 의도된 결과입니다.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_PATH = os.path.join(ROOT, 'content', 'charts.json')


def esc(s):
    return html.escape(str(s), quote=True)


def load_specs():
    with open(SPEC_PATH, encoding='utf-8') as f:
        return json.load(f)


def pct(v, mx):
    return round(min(max(v, 0) / mx * 100, 100), 3)


def tip_attrs(value, key, note=''):
    a = f' data-vz-v="{esc(value)}" data-vz-k="{esc(key)}"'
    if note:
        a += f' data-vz-n="{esc(note)}"'
    return a


def fig_attrs(spec, cid):
    a = f' id="{esc(cid)}"' if cid else ''
    if spec.get('label'):
        a += f' aria-label="{esc(spec["label"])}"'
    return a


def range_chart(spec, theme='light', cid=''):
    """막대 범위 차트: 진한 조각 = 시작값, 흐린 조각 = 범위 끝까지."""
    mx = spec['max']
    ticks = spec['ticks']                       # [[값, '라벨'], ...]
    grid = ', '.join(
        f'linear-gradient(var(--vz-grid), var(--vz-grid)) {pct(v, mx)}% 0 / 1px 100% no-repeat'
        for v, _ in ticks if 0 < v)
    cls = 'vz vz-range' + (' vz-dark' if theme == 'dark' else '')
    out = [f'<figure class="{cls}" data-vz-grow style="--vz-gridbg: {grid}"{fig_attrs(spec, cid)}>']
    if spec.get('title'):
        out.append(f'  <figcaption class="vz-title">{esc(spec["title"])}</figcaption>')
    lg = spec.get('legend')
    if lg:
        out.append('  <p class="vz-legend" aria-hidden="true">'
                   f'<span><i class="vz-key vz-key-lo"></i>{esc(lg[0])}</span>'
                   f'<span><i class="vz-key vz-key-hi"></i>{esc(lg[1])}</span></p>')
    out.append('  <ul class="vz-rows">')
    for r in spec['rows']:
        lo, hi = r['lo'], r.get('hi')
        em = r.get('em')
        segs = []
        a, b = pct(lo, mx), pct(hi, mx) if hi is not None else None
        has_hi = b is not None and b > a
        end_lo = '' if has_hi else (' is-clip' if r.get('open') else ' is-end')
        segs.append(f'<span class="vz-seg vz-lo{end_lo}" style="--a:0%;--b:{a}%"></span>')
        if has_hi:
            end_hi = ' is-clip' if r.get('open') else (' is-fuzzy' if r.get('fuzzy') else ' is-end')
            segs.append(f'<span class="vz-seg vz-hi{end_hi}" style="--a:{a}%;--b:{b}%"></span>')
        row_cls = 'vz-row' + (' is-em' if em else '')
        tip = tip_attrs(r['value'], r['name'], r.get('tip', ''))
        out.append(f'    <li class="{row_cls}"{tip}>')
        out.append(f'      <div class="vz-head"><span class="vz-name">{esc(r["name"])}</span>'
                   f'<span class="vz-val">{esc(r["value"])}</span></div>')
        out.append(f'      <div class="vz-track" aria-hidden="true">{"".join(segs)}</div>')
        if r.get('note'):
            out.append(f'      <p class="vz-note">{esc(r["note"])}</p>')
        out.append('    </li>')
    out.append('  </ul>')
    out.append('  <div class="vz-axis" aria-hidden="true">' + ''.join(
        f'<span style="--x:{pct(v, mx)}%">{esc(t)}</span>' for v, t in ticks) + '</div>')
    if spec.get('foot'):
        out.append(f'  <p class="vz-foot">{esc(spec["foot"])}</p>')
    out.append('</figure>')
    return '\n'.join(out)


def gantt(spec, theme='light', cid=''):
    """일정 차트: 가로 = 날짜, 줄 = 누가 하는 일인지. 강조 줄은 오렌지."""
    days = spec['days']
    cls = 'vz vz-gantt' + (' vz-dark' if theme == 'dark' else '')
    out = [f'<figure class="{cls}" data-vz-grow style="--vz-days:{days}"{fig_attrs(spec, cid)}>']
    if spec.get('title'):
        out.append(f'  <figcaption class="vz-title">{esc(spec["title"])}</figcaption>')
    out.append('  <div class="vz-g" aria-hidden="true">')
    out.append('    <span class="vz-g-corner"></span>' + ''.join(
        f'<span class="vz-g-day" style="grid-column:{d + 1}">{esc(spec["dayLabel"].format(d=d))}</span>'
        for d in range(1, days + 1)))
    for row, lane in enumerate(spec['lanes'], start=2):
        lc = 'vz-g-lane' + (' is-em' if lane.get('em') else '')
        out.append(f'    <span class="vz-g-label" style="grid-row:{row}">{esc(lane["label"])}</span>')
        out.append(f'    <span class="vz-g-bg" style="grid-row:{row}"></span>')
        for s in lane['segs']:
            span = f'Day {s["s"]}' + (f'–{s["e"]}' if s['e'] != s['s'] else '')
            tip = tip_attrs(s['tip'], f'{span} · {lane["label"]}')
            out.append(f'    <span class="{lc} vz-g-seg" style="grid-row:{row};grid-column:{s["s"] + 1} / {s["e"] + 2}"{tip}>'
                       f'<b>{esc(s["text"])}</b></span>')
    out.append('  </div>')
    if spec.get('foot'):
        out.append(f'  <p class="vz-foot">{esc(spec["foot"])}</p>')
    out.append('</figure>')
    return '\n'.join(out)


RENDER = {'range': range_chart, 'gantt': gantt}


def render(name, theme='light', specs=None):
    specs = specs or load_specs()
    spec = specs[name]
    return RENDER[spec['type']](spec, theme)
