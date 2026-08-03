# NOAH 레퍼런스 17종 — 사진 생성 프롬프트 마스터

> 생성 후 표기된 경로·파일명 그대로 저장하면 **코드 수정 없이 자동 반영**됩니다.
> (13·15~17번은 저장 후 알려주세요 — 코드의 임시 경로를 새 파일로 교체해 드립니다)

## 공통 규칙

**모든 프롬프트 뒤에 붙이는 공통 수식어**
```
photorealistic, professional photography, natural Korean people when people appear, soft realistic lighting, no text no logo no watermark, 8k --style raw --ar 3:2
```
(세로 슬롯은 `--ar 4:5`, 히어로 와이드는 `--ar 16:9` 로 교체)

**공통 네거티브**
```
low quality, blurry, distorted face, deformed hands, extra fingers, plastic skin, watermark, text, logo, collage, oversaturated, stock-photo cliche pose
```

**저장 규격**: 가로 1600px 이상 → WebP 또는 JPG(85%) 압축 권장.

---

## 13 · 온재무설계 (보험 스토리텔링) — 신규 6장
저장 위치: `assets/images/insurance/`
톤 수식어: `warm amber and deep forest green tones, cinematic quiet mood, Korean drama film still aesthetic`

| 파일명 | 비율 | 프롬프트 |
|---|---|---|
| 01-portrait.jpg | 4:5 | Korean woman in her 40s, insurance advisor, navy cardigan, warm confident smile, seated at wooden desk with documents, window morning light |
| 02-call.jpg | 3:2 | dimly lit desk at 2am, smartphone glowing on wooden table next to reading glasses and worn notebook, single warm lamp, cinematic |
| 03-listening.jpg | 3:2 | two people talking across a cafe table, focus on hands and warm teacups, one person listening attentively, shallow depth of field |
| 04-hospital.jpg | 3:2 | Korean woman walking through bright hospital corridor carrying leather document bag, seen from behind, hopeful morning light |
| 05-family.jpg | 3:2 | three generations of a Korean family laughing at a dinner table, warm evening home lighting, candid documentary style |
| 06-handshake.jpg | 3:2 | warm handshake over signed documents on desk, amber afternoon light through blinds, close-up, trust and relief mood |

## 14 · 본연 클리닉 (성형외과·피부과)
👉 **별도 문서 참조: `IMAGE_PROMPTS_CLINIC.md`** (히어로 6 · 공간 7 · 의료진 6 · 분야 11 · 후기 프레임 · 배너 8 · 썸네일 3 — 전용 스타일·네거티브 포함)
저장 위치: `assets/images/clinic/`

## 15 · 위즈웍스 (전환·견적형 에이전시) — 신규 14장
저장 위치: `assets/images/agency/`
톤 수식어: `clean bright modern office, cobalt blue and teal accents, tech startup atmosphere, crisp daylight`

**서비스 탭 6장 (3:2)**

| 파일명 | 프롬프트 |
|---|---|
| wiz-svc-corp.jpg | modern corporate website displayed on iMac in bright meeting room, two Korean professionals reviewing it |
| wiz-svc-commerce.jpg | online shopping concept, laptop showing product grid, credit card and small parcel boxes on white desk |
| wiz-svc-landing.jpg | marketer pointing at conversion funnel chart on large monitor, sticky notes on glass wall |
| wiz-svc-platform.jpg | developer workspace with dual monitors full of dashboard UI and code, blue ambient light |
| wiz-svc-mobile.jpg | hands holding smartphone showing clean app interface, blurred bright office background |
| wiz-svc-maint.jpg | calm workspace with laptop showing analytics graph, coffee cup, organized cable tray, morning light |

**포트폴리오 8장 (3:2)** — 산업별 프로젝트 무드

| 파일명 | 프롬프트 |
|---|---|
| wiz-pf-01.jpg | precision factory floor with modern CNC machines, engineer with tablet, cool industrial light |
| wiz-pf-02.jpg | bright modern clinic reception with staff at counter, clean white and wood interior |
| wiz-pf-03.jpg | contemporary lecture room, instructor at whiteboard, engaged students, natural light |
| wiz-pf-04.jpg | stylish retail store interior, curated product shelves, warm spotlights |
| wiz-pf-05.jpg | SaaS dashboard close-up on monitor, colorful charts, dark IDE in background |
| wiz-pf-06.jpg | professional consulting meeting, documents and laptop on walnut table, city view window |
| wiz-pf-07.jpg | interior design studio with material samples and blueprints spread on table |
| wiz-pf-08.jpg | photography studio with softbox lighting and camera on tripod, minimal backdrop |

## 16 · 논픽셀 (다크 에디토리얼 스튜디오) — 신규 15장
저장 위치: `assets/images/studio-dark/`
톤 수식어: `dark moody editorial photography, desaturated with single warm highlight, film grain, Kinfolk magazine aesthetic, dramatic shadows`

**포트폴리오 9장** (비율 혼합: 01·04·07=4:5, 02·05·08=16:10, 03·06·09=1:1)

| 파일명 | 프롬프트 |
|---|---|
| non-work-01.jpg | designer's hands sketching logo concepts under single desk lamp in dark studio |
| non-work-02.jpg | ultra-wide monitor with brand guideline layout, silhouetted designer, night office |
| non-work-03.jpg | stack of printed brand books with embossed covers, dramatic side light on black table |
| non-work-04.jpg | fashion e-commerce photoshoot behind the scenes, model silhouette, studio strobes |
| non-work-05.jpg | close-up of typography specimen prints pinned on dark wall, spotlighted |
| non-work-06.jpg | ceramic products arranged for product photography, black backdrop, single beam light |
| non-work-07.jpg | architect reviewing large printed floor plans by window at dusk, city bokeh |
| non-work-08.jpg | vinyl record packaging design mockups scattered on concrete floor, top view |
| non-work-09.jpg | hands adjusting color grading on video editing timeline, glowing screen in dark room |
| non-feat.jpg (16:7) | wide cinematic shot of creative studio at night — long wooden table, mood lamps, two designers deep in discussion over prototypes |

**서비스 hover 프리뷰 6장 (4:5)**

| 파일명 | 프롬프트 |
|---|---|
| non-svc-web.jpg | elegant website mockup on floating screen in dark space, orange accent glow |
| non-svc-commerce.jpg | minimal product packaging with barcode detail, dramatic shadow play |
| non-svc-brand.jpg | letterpress business cards and wax seal on black linen |
| non-svc-product.jpg | wireframe sketches and mobile prototype on dark desk, lime green sticky tabs |
| non-svc-marketing.jpg | analytics projected on wall in dark room, silhouette pointing |
| non-svc-maint.jpg | server rack LEDs in dark room, shallow focus, teal and amber dots |

## 17 · 플럭스랩 (인터랙티브 AI 스튜디오) — 신규 14장 + 미니 6장
저장 위치: `assets/images/fluxlab/`
톤 수식어: `bright airy tech office, cobalt blue and acid yellow-green accents, energetic modern atmosphere`

**히어로 스토리 패널 3장 (16:9)**

| 파일명 | 프롬프트 |
|---|---|
| flux-hero-system.jpg | abstract visualization of connected workflow — glowing nodes and lines over dark desk with keyboard, cobalt blue light |
| flux-hero-web.jpg | Korean team celebrating website launch in bright office, confetti of sticky notes, laptops open |
| flux-hero-ai.jpg | futuristic but realistic AI dashboard on curved monitor, engineer's silhouette, yellow-green accent lighting |

**가로 갤러리 5장 (16:10)**

| 파일명 | 프롬프트 |
|---|---|
| flux-g-01.jpg | responsive website shown across desktop, tablet and phone aligned on white desk |
| flux-g-02.jpg | e-commerce fulfillment scene — neat parcel boxes and barcode scanner, bright warehouse |
| flux-g-03.jpg | data pipeline diagram drawn on glass wall, engineer explaining, daylight |
| flux-g-04.jpg | brand style guide spread open next to Pantone chips on light oak table |
| flux-g-05.jpg | mobile app testing rig — multiple phones on stands running same interface |

**분야별 미니카드 6장 (4:5 — 각 카테고리 대표 1장, 3칸에 크롭 변형 사용)**

| 파일명 | 카테고리 | 프롬프트 |
|---|---|---|
| flux-cat-a.jpg | Responsive Web | corporate website on laptop in minimal bright office, plant shadow |
| flux-cat-b.jpg | Commerce | flat-lay of shopping cart icon sketches, product photos and price tags |
| flux-cat-c.jpg | Mobile | thumb tapping smooth mobile UI, macro shot, soft bokeh |
| flux-cat-d.jpg | Brand & Design | logo variations printed and pinned on cork board, daylight |
| flux-cat-e.jpg | Landing | single bold landing page on monitor with stopwatch beside — speed and focus mood |
| flux-cat-f.jpg | Platform & AI | terminal window and node graph on dual monitors, blue-green glow |

---

# 원본 12종 — 리제너레이션 세트 (기존 파일명 그대로 덮어쓰기)

> 이미 사진이 있는 템플릿입니다. 톤을 높이고 싶을 때 같은 파일명으로 교체하세요. (신규) 표시는 현재 없는 보강 슬롯.

## 01 · 라온치과 `assets/images/dental/` — `calm mint and white clinic, gentle morning light`
- 01-consult.jpg — Korean dentist in white coat showing tablet to relaxed patient, warm consultation room
- 02-prep.jpg — dental hygienist arranging sterilized tools on tray, shallow focus, clean mint room
- 03-farewell.jpg — dentist bowing farewell to smiling elderly patient at clinic entrance
- 04-room-active.jpg — bright treatment room with modern dental chair, window plants, no patient

## 02 · 정평 법무법인 `assets/images/law/` — `deep navy and brass, classic law office, dignified`
- 01-pen-paper.jpg — fountain pen signing legal document, brass desk lamp glow, close-up
- 02-late-work.jpg — lawyer working late among case files, single desk lamp, city night window
- 03-handshake.jpg — firm handshake between lawyer and client over walnut desk
- 04-bookshelf.jpg — floor-to-ceiling legal bookshelf with ladder, moody side light

## 03 · 오월의 다정 (카페) `assets/images/cafe/` — `warm cream and wood tones, cozy afternoon`
- 01-counter-latte.jpg — barista finishing latte art at wooden counter, steam rising, warm light
- 02-handover.jpg — barista handing coffee cup to customer, both hands close-up, smile blurred behind
- 03-empty-seat.jpg — empty window seat with sunlight stripes on wooden table and a book
- 04-pastry.jpg — fresh croissants and pound cake on ceramic plates, top-down, linen cloth

## 04 · 화월 (다이닝) `assets/images/restaurant/` — `dark elegant fine dining, gold accent, chiaroscuro`
- 01-chef.jpg (신규) — Korean chef plating with tweezers under focused spotlight, dark kitchen
- 02-dish.jpg — seasonal Korean fine-dining course dish on black ceramic, dramatic top light
- 03-service.jpg — server pouring tea for guests in dim elegant dining room, motion grace
- 04-tasting.jpg — chef tasting sauce from small spoon, concentrated expression, kitchen flames bokeh

## 05 · 여백 스튜디오 (인테리어) `assets/images/interior/` — `bright minimal, beige and light wood, negative space`
- 01-meeting.jpg — designer showing material board to couple at white table, airy studio
- 02-site.jpg — designer in helmet checking construction site with blueprint, sunbeam through window frame
- 03-detail.jpg (신규) — hand running over smooth oak cabinet edge, macro, soft daylight
- 04-samples.jpg — wood, stone and fabric samples arranged in gradient on white surface, top view

## 06 · 루티드 (필라테스) `assets/images/pilates/` — `sage green and warm wood studio, morning calm`
- 01-correction.jpg — instructor gently correcting client's posture on reformer, natural light studio
- 02-focus.jpg — close-up of aligned spine posture during exercise, calm breathing mood
- 03-studio.jpg (신규) — empty pilates studio at dawn, reformers in row, long soft shadows
- 04-greeting.jpg — instructor welcoming member at door with towel and warm smile

## 07 · 단정 (에스테틱) `assets/images/beauty/` — `blush pink and ivory, serene spa light`
- 01-treatment.jpg — esthetician performing facial treatment, client deeply relaxed, soft towel wrap
- 02-relaxed.jpg — client resting with eyes closed under warm blanket, candle bokeh
- 03-products.jpg (신규) — minimal skincare bottles on marble tray with eucalyptus sprig
- 04-prep.jpg — therapist preparing warm towels and oils, ritual-like arrangement

## 08 · Stackline (SaaS) `assets/images/saas/` — `violet and indigo tech, dark UI aesthetic`
- 01-dashboard.jpg — analytics dashboard with colorful charts on widescreen monitor, dark mode UI
- 02-team.jpg (신규) — young Korean dev team at standup meeting before kanban wall, bright loft office
- 03-code.jpg (신규) — macro of code editor with glowing syntax colors, shallow depth
- 04-growth.jpg (신규) — upward graph projected on wall, silhouettes watching, celebratory mood

## 09 · 산일호 (풀빌라) `assets/images/pension/` — `mountain serenity, warm timber, blue hour`
- 01-pool.jpg (신규) — private infinity pool steaming at blue hour, mountain silhouette beyond
- 02-bath-coffee.jpg — coffee tray beside outdoor bath with forest view, steam, morning
- 03-walk.jpg — couple walking forest path from behind, dappled light
- 04-view.jpg — floor-to-ceiling window framing mountain range from cozy bedroom

## 10 · 무드그래프 (스튜디오) `assets/images/studio/` — `black and white with warm skin tones, editorial portrait`
- 01-photographer.jpg — photographer adjusting camera on tripod under softbox, dark studio
- 02-bride.jpg — bride's veil floating mid-motion, backlit, monochrome elegance
- 03-family.jpg — candid laughing family portrait session, warm strobes
- 04-review.jpg — photographer and client reviewing photos on tethered monitor

## 11 · 메리트 입시 `assets/images/academy/` — `trust navy and warm yellow, focused study light`
- 01-consult.jpg — consultant explaining roadmap chart to parent and student, warm office
- 02-student.jpg — high-schooler studying intently at desk lamp, notes spread
- 03-parent.jpg — reassured parent listening in consultation, soft focus
- 04-teaching.jpg — instructor at whiteboard with strategy diagram, evening classroom

## 12 · 한울정밀 (제조) `assets/images/manufacture/` — `steel blue industrial, precise and clean`
- 01-monitor.jpg — engineer monitoring CNC machining data on industrial display
- 02-calipers.jpg — digital calipers measuring metal part, macro, micron precision mood
- 03-meeting.jpg — engineers reviewing technical drawings at factory meeting table
- 04-cmm.jpg — coordinate measuring machine probing polished component, blue LED

---

### 생성 우선순위 추천
1. **15~17 에이전시 3종** (현재 타 업종 사진 차용 중 — 교체 효과 최대)
2. **13 온재무설계** (현재 사진 0장)
3. 14 클리닉 (별도 문서, 분량 큼)
4. 원본 12종 리제너레이션 (선택)

생성 완료 → 해당 경로에 저장 → 커밋해 주시면, 13·15~17의 코드 참조 경로를 새 파일로 교체해 드립니다.
