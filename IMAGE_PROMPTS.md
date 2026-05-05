# 이미지 생성 프롬프트 전체 (12 업종 × 4장)

촬영 디렉터 시점에서 카메라·렌즈·조명·컬러그레이딩·구도까지 명세한 프롬프트 모음.

## 🎬 사용 가이드

- 프롬프트는 모두 **영문** — Midjourney / DALL·E 3 / Imagen / Flux / Stable Diffusion 등 대다수 이미지 생성 모델에서 영문 입력이 가장 안정적
- 각 프롬프트는 **3블록**으로 구성:
  1. **Prompt** — 모델에 그대로 입력
  2. **Negative** — 피해야 할 요소 (Midjourney `--no`, SD/Flux `negative prompt`)
  3. **Director's note** — 무드/레퍼런스 컨텍스트 (한국어, 참고용)
- **Aspect ratio**는 모델별 옵션으로 명시
  - Midjourney: `--ar 4:5`
  - DALL·E 3: 자동 (1024×1792 = 9:16, 1792×1024 = 16:9)
- **각 업종 4장은 한 세트** — 같은 카메라/렌즈/그레이딩 어휘를 반복해 톤 일관성 유지

---

## 📐 촬영 디렉터 공통 원칙

이번 프롬프트 세트의 전제

1. **인물은 가능한 한 얼굴 정면 회피** — 측면, 손, 실루엣, 뒷모습 위주 (초상권·사실성 리스크 최소화)
2. **깊이 있는 자연광 우선** — 인공 광원 명시할 때만 사용
3. **클리셰 금지** — 정의의 여신상, 라떼아트 하트, 기도 손, 풍선, 컬러풀 캔디 컷
4. **색감은 브랜드 토큰과 매칭** — 각 업종의 디자인 컬러를 프롬프트에 명시
5. **35mm·50mm·85mm 프라임 렌즈** 위주 (자연스러운 원근)
6. **Editorial photography / quiet documentary** 톤 (광고 컷 X)

---

# 01. 치과 — 라온치과의원

**브랜드 톤**: 따뜻한 화이트 + 민트 (#0f5d4a / #d6f0e6). 신중·정성.

### 1-1. 진료실 한 켠 (Hero)
- **File**: `dental/01-hero-room.jpg` · **Ratio**: 4:5

**Prompt**
```
A quiet corner of a modern dental clinic, late afternoon natural light streaming through a large window onto pale oak floor, a single soft mint upholstered chair, a small potted snake plant, a rolled white linen towel on a wooden side table, no medical equipment visible, shot on Sony A7IV with 50mm f/1.8 prime lens, soft natural daylight, warm whites and muted mint tones, shallow depth of field, editorial calmness, Kinfolk magazine aesthetic, clean composition with negative space
```
**Negative**: people, faces, drills, syringes, dental tools, harsh fluorescent light, clinical white, plastic textures, stock photo look

**Director's note**: 라온의 첫 화면. 의료기관이지만 카페처럼 따뜻해야 함. Kinfolk 잡지의 '진료실' 화보가 있다면 이런 느낌.

---

### 1-2. 손 위의 작은 모형 (Detail)
- **File**: `dental/02-hands-model.jpg` · **Ratio**: 1:1

**Prompt**
```
Close-up macro shot of a person's hands gently holding a tiny ceramic tooth model, soft hands of a young Korean woman in her thirties wearing a light beige sweater, photographed from above on a textured cream linen surface, golden hour side light from the left creating gentle shadows, shot on Canon R5 with 100mm macro lens at f/4, warm natural tones with subtle mint accent, shallow depth of field on the model, editorial still life, hands only no face
```
**Negative**: face, full body, jewelry, nail polish, harsh light, cold blue tones, multiple people

**Director's note**: 신중함의 시각화. 모형은 작아도 정성스럽게 다뤄지는 표정.

---

### 1-3. 환자가 떠난 진료의자 (Wide)
- **File**: `dental/03-room-empty.jpg` · **Ratio**: 16:10

**Prompt**
```
A modern minimalist dental treatment room, completely empty after work hours, single dental chair in muted sage and cream upholstery, large window with sheer linen curtain casting soft afternoon light onto white wood floor, a small wooden stool, plants in the background out of focus, no equipment visible on counters, shot on Fujifilm GFX with 35mm lens at f/4, cinematic quiet documentary style, warm white balance, soft shadows, architectural digest aesthetic
```
**Negative**: medical equipment, drills, lights overhead, monitors, harsh lighting, people

**Director's note**: 환자가 떠난 후의 고요. 진료실인데 거의 호텔 객실 같은 느낌이어야 함.

---

### 1-4. 식물과 빛 (Atmospheric)
- **File**: `dental/04-plant-light.jpg` · **Ratio**: 4:5

**Prompt**
```
A single olive green pothos plant in a matte ceramic pot on a pale oak wood shelf, dappled morning sunlight casting plant leaf shadows on a textured plaster wall, the wall painted in muted soft white with subtle warm undertone, a folded white linen cloth on the shelf below, shot on Leica Q2 with 28mm at f/2.8, natural light only, warm muted color palette, fine art photography, painterly quality, breathing space
```
**Negative**: artificial flowers, bright colors, cluttered shelves, plastic pots, harsh contrast

**Director's note**: '식물 한 점'으로 진료실의 인간미를 시각화. 어떤 페이지에든 끼울 수 있는 만능 컷.

---

# 02. 법무 — 정평 법무법인

**브랜드 톤**: 네이비 + 골드 (#0e1a2b / #c9a961). 묵직·정직.

### 2-1. 다크 우드 책상의 만년필 (Hero)
- **File**: `law/01-pen-paper.jpg` · **Ratio**: 4:5

**Prompt**
```
An overhead view of an antique dark walnut desk, a single Montblanc-style fountain pen lying on heavy cream-colored handmade paper with subtle texture, a vintage brass desk lamp turned off in the corner, late afternoon golden hour light streaming from the right, deep shadows pooling on the left, shot on Hasselblad X2D with 80mm lens at f/2.8, moody editorial photography, deep navy and gold tones, rich blacks, warm highlights, gravitas atmosphere
```
**Negative**: laptops, modern items, plastic, bright daylight, cold tones, multiple people

**Director's note**: 변호인의 정직성. 화려한 골드는 피하고, 새겨진 시간만 보이도록.

---

### 2-2. 책장 측면 라이브러리 (Detail)
- **File**: `law/02-book-spines.jpg` · **Ratio**: 4:5

**Prompt**
```
Close-up of a tall mahogany bookshelf filled with leather-bound legal books, focus on the worn gold-foil spines reading uneven typography, dust illuminated by a single ray of warm window light from the left, deep shadows in the bottom shelves, shot on Nikon Z9 with 85mm f/1.4 lens, cinematic chiaroscuro, rich amber and deep navy tones, fine art photography, archival quality, vintage but cared for
```
**Negative**: modern books, paperbacks, colorful covers, cluttered shelves, fluorescent lighting

**Director's note**: 법무법인의 권위는 '쌓인 시간'에서 온다. 책장은 손때가 묻어 있어야 함.

---

### 2-3. 코너 오피스의 도시 (Wide)
- **File**: `law/03-office-window.jpg` · **Ratio**: 16:10

**Prompt**
```
A high-rise corner law office at dusk, large floor-to-ceiling windows showing Seoul skyline at golden hour blue hour transition, a single dark leather Eames chair facing the window, a heavy walnut desk in silhouette on the right, the office mostly in shadow with only the city lights and last sun rays providing illumination, shot on Sony A1 with 24mm wide lens at f/4, moody architectural photography, navy and warm gold palette, contemplative mood
```
**Negative**: bright office lights, busy desk, multiple chairs, posters, artwork on walls, daytime brightness

**Director's note**: '늦게까지 남은 변호사'의 자리. 사람은 없지만 누군가 막 떠난 듯한 흔적.

---

### 2-4. 변호사 측면 인물 (Portrait — face partially hidden)
- **File**: `law/04-lawyer-side.jpg` · **Ratio**: 4:5

**Prompt**
```
Editorial side profile of a Korean man in his late forties wearing a charcoal suit and white shirt, no tie, looking down at a document, half of his face obscured by shadow, soft window light from the left rim-lighting his temple and shoulder, dark navy painted wall in deep background, shot on Leica SL2 with 75mm f/1.4 lens, shot from behind glass for soft diffusion, Vogue Hommes editorial style, deep navy gold black palette, gravitas
```
**Negative**: smiling, looking at camera, full face visible, gestures, cluttered background, bright lighting

**Director's note**: 신뢰는 '말하는 자'보다 '듣는 자'에서 온다. 측면+그림자가 핵심.

---

# 03. 카페 — 오월의 다정

**브랜드 톤**: 우드 + 크림 (#5a3e1f / #f5e6d3). 따뜻·동네·일상.

### 3-1. 우드 카운터의 한 잔 (Hero)
- **File**: `cafe/01-counter-latte.jpg` · **Ratio**: 16:10

**Prompt**
```
A single white ceramic latte cup on a warm walnut wood bar counter, gentle steam rising in the late morning side light coming from a window on the left, a small dish of butter cookies blurred in the background, soft cream linen napkin folded beside, no people, an empty stool slightly out of focus, shot on Fujifilm X-T5 with 35mm f/1.4 lens at f/2, warm natural daylight, golden cream tones, hand-crafted neighborhood cafe atmosphere, Kinfolk meets Cereal magazine aesthetic
```
**Negative**: latte art hearts, multiple drinks, plastic cups, branded merchandise, harsh light, busy background

**Director's note**: 화려한 라떼아트 X. 단정한 한 잔이 핵심. 조명은 9-10시 아침 햇빛.

---

### 3-2. 손이 잔을 내려놓는 순간 (Detail)
- **File**: `cafe/02-hands-cup.jpg` · **Ratio**: 1:1

**Prompt**
```
Close-up of a young woman's hands gently placing a hand-thrown ceramic latte cup onto a wooden counter, only forearms in soft cream knit sweater visible, the cup is matte cream with small imperfections from handcrafting, golden afternoon light from the right creating soft hand shadows, shot on Canon R5 with 50mm at f/1.8, warm natural light only, cream and walnut palette, intimate documentary moment, hands only no face
```
**Negative**: rings, manicured nails, jewelry, multiple cups, branded napkins, harsh light

**Director's note**: '내려놓는 손'이 카페의 다정함을 시각화. 잔은 도자기 핸드메이드.

---

### 3-3. 늦은 오후의 빈 자리 (Wide)
- **File**: `cafe/03-empty-seat.jpg` · **Ratio**: 16:10

**Prompt**
```
An empty corner seat of a small neighborhood cafe in late afternoon, a single bentwood Thonet chair tucked under a small round walnut table, a half-finished cup and a folded newspaper left on the table, dappled afternoon sunlight through partially closed wooden blinds creating warm stripes on the cream wall and table, no people, shot on Sony A7IV with 35mm f/2 lens, golden hour, warm cream wood beige palette, quiet documentary style, Wes Anderson framing
```
**Negative**: crowded cafe, modern minimalist furniture, fluorescent light, neon signs, brand logos visible

**Director's note**: '방금 누군가 떠난 자리'. 인기척이 있되 사람은 없는 컷.

---

### 3-4. 베이커리 클로즈업 (Detail 2)
- **File**: `cafe/04-pastry.jpg` · **Ratio**: 1:1

**Prompt**
```
Top-down macro shot of three small handmade financiers and one freshly cracked open croissant on a white linen cloth, scattered crumbs, a tiny cream ceramic plate, soft morning light from the left side, shot on Hasselblad X2D with 65mm at f/4, warm natural light, golden brown cream tones, food editorial style, Saveur magazine aesthetic, hand-baked imperfection visible
```
**Negative**: perfectly arranged display, plastic packaging, multiple types crammed, sprinkles, frosting heavy decoration

**Director's note**: 제과점의 '아침에 갓 만든' 정직함.

---

# 04. 다이닝 — 화월

**브랜드 톤**: 블랙 + 골드 (#0a0a0a / #d4af37). 럭셔리·고즈넉.

### 4-1. 다크 배경의 한 그릇 (Hero)
- **File**: `restaurant/01-dish-dark.jpg` · **Ratio**: 16:9

**Prompt**
```
A single Korean modern fine dining dish on a dark slate plate placed on a black walnut table, the plate features delicately arranged baby bamboo shoots, charred sea bream slices, and a tiny dollop of foam, deep black background fading to absolute darkness, single warm rim light from the upper right creating gold highlights on the food and ceramics, shot on Phase One IQ4 with 80mm at f/5.6, chiaroscuro food photography, deep blacks rich golds amber tones, Michelin guide editorial, refined and contemplative
```
**Negative**: bright daylight, casual dining, plastic plates, white background, multiple dishes, cutlery scattered, restaurant clutter

**Director's note**: 미슐랭 화보. 하나의 코스만 인물 없이 깊은 어둠 속에 떠 있게.

---

### 4-2. 셰프의 손이 플레이팅 (Detail)
- **File**: `restaurant/02-plating-hands.jpg` · **Ratio**: 4:5

**Prompt**
```
Close-up overhead view of a chef's hands carefully placing a single delicate herb on a plated dish using long tweezers, only forearms in dark navy chef coat sleeves visible, the dish features Korean modern cuisine with bamboo shoots and edible flowers, deep black wood table beneath, single warm focused spotlight from above, shot on Sony A1 with 90mm macro at f/4, dramatic chiaroscuro, deep blacks and warm gold rim, Tartine Bakery cookbook aesthetic, intense focus
```
**Negative**: face, full body, casual handling, plastic gloves, bright lighting, busy kitchen, multiple chefs

**Director's note**: 코스의 마지막 1mm. 정성의 끝자리.

---

### 4-3. 14석 카운터 다이닝 (Wide)
- **File**: `restaurant/03-counter-seats.jpg` · **Ratio**: 16:10

**Prompt**
```
A intimate 14-seat omakase-style fine dining counter shot from the customer side, a long polished black walnut counter stretching to the right, ceramic Korean tableware set at each empty seat, low pendant warm-toned brass lights hanging above creating golden pools, dark moody background with hints of indigo wall texture, no people, shot on Leica SL2 with 24mm at f/4, architectural editorial photography, deep moody atmosphere, jet black gold amber palette, before-service quiet
```
**Negative**: bright lighting, casual restaurant, white tablecloths, multiple tables crowded, neon signs

**Director's note**: '서비스 시작 30분 전' 의 자리. 모든 것이 준비된 정적.

---

### 4-4. 셰프 측면 인물 (Portrait)
- **File**: `restaurant/04-chef-portrait.jpg` · **Ratio**: 4:5

**Prompt**
```
Editorial side profile of a Korean man in his early forties wearing a black chef coat, no hat, focused expression looking down at his work surface, half of his face in deep shadow, single warm tungsten light from the left rim-lighting his cheek and shoulder, dark moody black kitchen behind, shot on Hasselblad X2D with 80mm at f/2, magazine editorial, deep blacks and warm amber palette, Magnum Photos style, focused contemplation
```
**Negative**: smiling, looking at camera, multiple chefs, busy kitchen, bright fluorescent light, casual posing

**Director's note**: 셰프는 작품의 일부. 도구도 사람도 모두 어둠 속에서 빛난다.

---

# 05. 인테리어 — 여백 스튜디오

**브랜드 톤**: 그레이 + 우드 (#1f2426 / #fafaf9). 미니멀·여백.

### 5-1. 텅 빈 거실 (Hero)
- **File**: `interior/01-empty-living.jpg` · **Ratio**: 16:10

**Prompt**
```
An almost-empty modern minimalist Korean apartment living room, white plaster walls, oak parquet floor with subtle grain, a single low-profile linen sofa in muted beige, one olive tree plant in a stone pot in the corner, large floor-to-ceiling window with sheer linen curtain casting soft afternoon light, vast empty wall space, shot on Fujifilm GFX 100S with 23mm at f/8, architectural digest editorial, neutral beige gray oak palette, perfectly composed negative space, calm natural light, Vincent Van Duysen aesthetic
```
**Negative**: cluttered furniture, decorative items, art frames on walls, bright colors, harsh lighting, multiple textures competing

**Director's note**: '비어 있어야 머물 수 있다'를 시각화. 가구는 1점만.

---

### 5-2. 우드 바닥의 빛 (Detail)
- **File**: `interior/02-floor-light.jpg` · **Ratio**: 4:5

**Prompt**
```
A close-up of pale oak hardwood floor receiving morning light through an unseen window, the light forming a clean rectangular pattern across the wood grain, a small portion of a stone gray rug visible at the corner, no objects, just light and texture, shot on Phase One IQ4 with 50mm at f/8, fine art architecture photography, calm neutral palette of bone oak gray, subtle warm white balance, John Pawson minimalist aesthetic
```
**Negative**: furniture, people, decorative objects, bright sunlight, vivid colors, dust visible

**Director's note**: 빛만으로 채워진 컷. 인테리어의 '비물질적' 본질.

---

### 5-3. 단정한 복도 (Wide)
- **File**: `interior/03-corridor.jpg` · **Ratio**: 4:5

**Prompt**
```
A serene minimalist Korean apartment hallway leading to a doorway, walls painted in warm bone white, oak parquet floor, a single dark wood bench with a folded linen throw at the far end, soft daylight from a side window, vanishing point composition, shot on Sony A7R V with 35mm at f/5.6, architectural photography, neutral palette, calm symmetry, Tadao Ando inspired, monochromatic warmth
```
**Negative**: doors open showing rooms, art on walls, multiple objects, modern lighting fixtures, cold tones

**Director's note**: 동선의 미학. 비어 있어 더 명료한 공간.

---

### 5-4. 돌 카운터의 디테일 (Detail 2)
- **File**: `interior/04-stone-detail.jpg` · **Ratio**: 1:1

**Prompt**
```
A close-up of the corner of a honed travertine kitchen island countertop meeting a matte oak cabinet, water glass with single drop of condensation, a small linen cloth, soft afternoon light grazing the stone surface revealing its subtle veining, shot on Hasselblad X2D with 80mm macro at f/4, fine craftsmanship detail photography, warm beige and oak palette, material textures emphasized, Axel Vervoordt aesthetic
```
**Negative**: shiny polished surfaces, marble veins dramatic, kitchen clutter, multiple appliances, branded items

**Director's note**: 마감재가 주연. 사용감이 살짝 있어야 진짜처럼.

---

# 06. 필라테스 — 루티드

**브랜드 톤**: 세이지 + 크림 (#2d4a3a / #f6f3ec). 자세·차분·뿌리.

### 6-1. 리포머의 측면 (Hero)
- **File**: `pilates/01-reformer.jpg` · **Ratio**: 4:5

**Prompt**
```
A single Balanced Body classical reformer pilates machine in a serene studio, side angle view, polished light maple wood frame and cream upholstery, a small potted snake plant on the floor beside it, soft natural daylight from a tall window casting gentle shadows on the white oak floor, sage green plaster wall in the background, no people, shot on Fujifilm GFX with 45mm at f/4, calm wellness editorial, sage cream maple palette, Goop magazine aesthetic
```
**Negative**: gym equipment, mirrors heavy, fluorescent light, branded gear, cluttered studio, weights

**Director's note**: 헬스장이 아닌 '연구소'의 분위기. 기구 하나만 정성껏.

---

### 6-2. 등 라인의 실루엣 (Body form)
- **File**: `pilates/02-back-silhouette.jpg` · **Ratio**: 4:5

**Prompt**
```
A side silhouette of a young Korean woman in her late twenties performing a pilates plank position on a reformer, only her body and back visible from the side, low ponytail, neutral gray pilates clothing, lit from a tall window on the right creating a clean rim light along her spine and arm, sage colored studio wall behind, face not visible, shot on Sony A1 with 85mm at f/2, sports editorial Vogue style, sage cream amber palette, study of the body's lines
```
**Negative**: face visible, gym setting, full body shot, tight workout clothes, motivational posing

**Director's note**: 핵심은 '척추 라인'. 얼굴은 의도적으로 안 보이게.

---

### 6-3. 빈 스튜디오 와이드 (Wide)
- **File**: `pilates/03-studio-wide.jpg` · **Ratio**: 16:10

**Prompt**
```
An empty modern pilates studio interior, three reformer machines aligned facing a tall arched window, white oak floor, sage green plaster wall, sheer linen curtains diffusing morning light, two olive trees in stone pots, no people, no mirrors visible, shot on Hasselblad X2D with 30mm at f/8, architectural wellness photography, sage cream warm white palette, calm before opening, perfectly composed
```
**Negative**: gym aesthetic, mirrors covering walls, motivational posters, harsh lighting, multiple equipment cluttered

**Director's note**: '아무도 없는 시간'의 스튜디오가 가장 신뢰감 있다.

---

### 6-4. 손과 폼롤러 (Detail)
- **File**: `pilates/04-prop-detail.jpg` · **Ratio**: 1:1

**Prompt**
```
A close-up of a young woman's hands holding a sage green foam roller on a cream pilates mat, only forearms visible in soft cream long-sleeve top, soft morning light from above creating gentle shadows, shot on Canon R5 with 100mm macro at f/4, wellness editorial detail, sage cream palette, calm focus, hands and props only
```
**Negative**: face, full body, multiple props piled, harsh lighting, branded equipment visible

**Director's note**: 도구는 단순할수록 좋다. 한 가지만.

---

# 07. 에스테틱 — 단정 에스테틱

**브랜드 톤**: 핑크 + 로즈골드 (#9b3a4e / #fde4e8). 단정·우아.

### 7-1. 도자기 위 앰플 (Hero)
- **File**: `beauty/01-ampoule.jpg` · **Ratio**: 4:5

**Prompt**
```
A still life of two minimalist amber glass cosmetic ampoule bottles standing on a small white artisanal ceramic dish, the ampoules unbranded with simple cream labels, placed on a textured pale dusty rose linen cloth, soft diffused morning light from the left, dried baby's breath flower beside, shot on Hasselblad X2D with 100mm macro at f/4, beauty editorial still life, dusty rose amber cream palette, Aesop magazine aesthetic, refined craftsmanship
```
**Negative**: branded cosmetics, neon labels, multiple bottles, glittery products, harsh studio lighting

**Director's note**: 약방이나 향수 가게의 분위기. 화려함 X, 정직함 O.

---

### 7-2. 손목 위의 디테일 (Detail)
- **File**: `beauty/02-skin-detail.jpg` · **Ratio**: 4:5

**Prompt**
```
A close-up of a young Korean woman's inner forearm and wrist resting on a cream linen cloth, a single small drop of clear serum on her skin reflecting soft window light, only forearm visible no face, natural unmade-up skin, shot on Sony A1 with 90mm macro at f/2.8, beauty editorial detail, cream warm palette with subtle pink undertone, Allure magazine fine art beauty, intimate quiet moment
```
**Negative**: face, makeup heavy, jewelry, perfect porcelain skin retouch, harsh studio light

**Director's note**: 자연스러운 피부의 한 점. 광고 컷 X, 다큐멘터리 O.

---

### 7-3. 시술실 한 켠 (Wide)
- **File**: `beauty/03-treatment-room.jpg` · **Ratio**: 4:5

**Prompt**
```
A peaceful corner of an esthetician's treatment room, a single white linen-covered massage bed with cream cotton blanket folded at the foot, dried pampas grass in a tall ceramic vase, soft morning light through sheer linen curtains, oak side table with a single white towel rolled neatly, no people, shot on Fujifilm GFX with 35mm at f/4, wellness editorial, dusty pink cream beige palette, Goop magazine spa aesthetic, serene before treatment
```
**Negative**: clinical bright lighting, medical equipment visible, multiple beds, busy spa, branded products

**Director's note**: 시술 직전의 정적. 환자의 긴장이 풀어지는 순간을 시각화.

---

### 7-4. 손이 만지는 작은 병 (Detail 2)
- **File**: `beauty/04-hand-bottle.jpg` · **Ratio**: 1:1

**Prompt**
```
Close-up of a woman's hand gently lifting a small unbranded amber glass dropper bottle from a cream marble surface, only fingers and palm visible, natural unpainted nails, soft morning light from the left, blurred dried flower in background, shot on Canon R5 with 85mm at f/2, beauty editorial, dusty rose amber cream palette, intimate care gesture, hands only
```
**Negative**: multiple products, full body, painted nails bright, jewelry, harsh studio light

**Director's note**: '집에서 이어가는 루틴'을 손짓으로 보여줌.

---

# 08. SaaS — Stackline

**브랜드 톤**: 보라 + 블랙 (#7c5cff / #08070d). 테크·트렌디.

> **참고**: SaaS는 사진이 아닌 **UI 모킹 이미지**가 적합. Figma·Photoshop 합성으로 만드는 가짜 프로덕트 스크린샷.

### 8-1. 다크 모드 대시보드 (Hero UI)
- **File**: `saas/01-dashboard.png` · **Ratio**: 16:9

**Prompt**
```
A modern SaaS product dashboard UI mockup screenshot, dark mode interface with deep black background and purple accent (#7c5cff), centered hero shows a unified workspace with a Slack-style left sidebar showing channels, a main panel with a glowing line chart in soft purple gradients, a Notion-style document preview in the right panel, sans-serif Inter font, sharp pixel-perfect UI design, subtle purple to pink gradient accents on key metrics, shot as a screenshot at retina resolution, Linear and Vercel design language inspired
```
**Negative**: photo realism, real photographs, people, generic stock UI templates, light mode, busy charts

**Director's note**: Linear / Vercel / Stripe 같은 SaaS의 톤. 디자이너가 만들면 가장 자연스러움.

---

### 8-2. 슬랙 명령어 통합 (Feature 1)
- **File**: `saas/02-feature-track.png` · **Ratio**: 16:10

**Prompt**
```
A UI mockup of a Slack-style chat interface in dark mode, showing a conversation where a user types `/track campaign-q2-launch` and a beautifully formatted card appears below showing automatic tracking metadata, deep black background with subtle purple accent on the active card, Inter typography, clean spacing, the card has small chart sparkline preview in purple gradient, sharp screenshot fidelity, dark mode SaaS product design, Linear inspired
```
**Negative**: photo realism, real users, busy interfaces, light mode, generic templates

**Director's note**: '명령어 한 번으로 통합'을 실제 동작 캡처처럼.

---

### 8-3. 단일 소스 오브 트루스 (Feature 2)
- **File**: `saas/03-feature-truth.png` · **Ratio**: 16:10

**Prompt**
```
A UI mockup of three connected document panels showing real-time sync, central panel shows a clean Notion-style decision document with glowing edit indicators, left panel a smaller spreadsheet, right panel a chat thread, all connected by subtle animated purple sync lines, dark mode interface, deep black with #7c5cff accents, Inter font, screenshot quality with retina pixel sharpness, modern SaaS design
```
**Negative**: photo realism, real photographs, busy charts, multiple windows cluttered, light mode

**Director's note**: '하나의 소스'를 시각적으로 — 세 문서가 연결되어 빛나는 모습.

---

### 8-4. 결정 로그 타임라인 (Feature 3)
- **File**: `saas/04-feature-log.png` · **Ratio**: 16:10

**Prompt**
```
A UI mockup of a decision log timeline interface, vertical timeline with each entry showing a decision title, timestamp in monospace font, contributors as avatar dots, the active row has a glowing purple left border, deep black background, soft purple gradient highlights on key entries, clean Inter typography, JetBrains Mono for timestamps, retina sharp screenshot quality, Linear product design
```
**Negative**: photo realism, real photographs, illustrations cartoon, light mode, busy decoration

**Director's note**: '왜 그렇게 결정했는지' 가 남는 자리. 깊이 있고 시간 순서대로.

---

# 09. 풀빌라 — 산일호

**브랜드 톤**: 우드 + 세이지 그린 (#3a4a3a / #f7f3eb). 휴양·산속.

### 9-1. 산자락 외관 (Hero)
- **File**: `pension/01-villa-exterior.jpg` · **Ratio**: 16:9

**Prompt**
```
A modern minimalist single-story Korean pool villa nestled in a pine and birch forest at the foot of a mountain in Inje, Gangwon, Korea, wide angle showing the wooden cedar exterior with floor-to-ceiling glass, a small private infinity pool reflecting the trees, golden hour late summer light, mountain ridge visible behind tall trees, no people, shot on Sony A7R V with 24mm at f/8, architectural travel editorial, sage green wood gold palette, Cabin Porn aesthetic meets Aman Resorts, serene
```
**Negative**: tropical resort, bright daylight, palm trees, crowds, theme park, neon signs

**Director's note**: 강원도 인제 자작나무숲 자락의 한 채. 단지가 아닌 단독.

---

### 9-2. 큰 창에서 보이는 산 (Wide)
- **File**: `pension/02-window-mountain.jpg` · **Ratio**: 16:10

**Prompt**
```
Interior view from a Korean pool villa living room looking out through a massive floor-to-ceiling window framing a quiet pine forest mountain ridge, foreground shows a low linen sofa in muted oatmeal, a wood coffee table with a single ceramic teacup, soft afternoon light, no people, shot on Phase One IQ4 with 28mm at f/8, architectural digest editorial, sage cream wood palette, Japandi aesthetic, contemplative
```
**Negative**: bright tropical light, multiple people, busy interior, urban skyline, modern minimalism without warmth

**Director's note**: '거실의 큰 창에서 산이 정면으로'. 바깥이 주연.

---

### 9-3. 자작나무숲 사잇길 (Atmospheric)
- **File**: `pension/03-birch-forest.jpg` · **Ratio**: 4:5

**Prompt**
```
A serene path winding through a dense white birch forest in Korea's Inje region, soft morning mist between the slender white trunks, a single small figure walking far in the distance with a simple long beige coat, mostly back view almost silhouette, autumn leaves on the forest floor, shot on Leica SL2 with 50mm at f/2.8, fine art landscape photography, muted forest green cream beige palette, Andrei Tarkovsky cinematography style, atmospheric calm
```
**Negative**: bright tourist crowds, autumn brilliant red colors, harsh sunlight, urban elements, signage

**Director's note**: 사람은 점처럼만 — 풍경의 일부.

---

### 9-4. 노천탕 디테일 (Detail)
- **File**: `pension/04-bath-detail.jpg` · **Ratio**: 4:5

**Prompt**
```
A close-up of a private outdoor stone bathing pool surrounded by trees, steam rising in cool morning air, a single white linen towel folded on the wooden deck edge, a small ceramic cup with green tea, no people, soft early morning light filtered through pine branches, shot on Hasselblad X2D with 65mm at f/4, travel editorial, mossy stone wood cream palette, Cereal magazine retreat aesthetic, intimate solitude
```
**Negative**: people in pool, bright pool lights, plastic loungers, beach umbrellas, vacation tropical look

**Director's note**: '노천탕에서 보이는 별'의 새벽 버전. 사람은 막 떠난 흔적.

---

# 10. 스튜디오 — 무드그래프

**브랜드 톤**: 블랙 + 화이트 (#0a0a0a / #f5f5f5). 시네마틱·에디토리얼.

### 10-1. 인물 클로즈업 (Hero — Series Frame 01)
- **File**: `studio/01-portrait-close.jpg` · **Ratio**: 3:4

**Prompt**
```
A close-up cinematic portrait of a young Korean woman in her late twenties looking off to the side away from camera, soft window light from the left side highlighting her cheekbone and ear with the rest of her face in shadow, simple black wool turtleneck, dark gray painted background, no makeup or natural minimal makeup, slightly out of focus, shot on Leica M11 with 50mm Summilux at f/1.4, black and white photography with subtle warm tone, fine grain Kodak Tri-X 400 film aesthetic, fashion editorial Vogue Italia, contemplative
```
**Negative**: smiling at camera, full color saturation, harsh studio strobe, glamour shot retouch, multiple people

**Director's note**: '결정적 한 컷'의 정반대. 분위기가 주연.

---

### 10-2. 빛에 비치는 손 (Series Frame 02)
- **File**: `studio/02-hand-light.jpg` · **Ratio**: 4:3

**Prompt**
```
A young woman's hand reaching toward a beam of dust-illuminated window light, only the hand and forearm visible, soft pale skin against deep dark background, slight motion blur on the fingers, shot on Leica SL2 with 75mm at f/1.4, black and white with warm tone, Kodak Tri-X grain, fine art photography, Saul Leiter inspired, intimate gesture
```
**Negative**: jewelry, painted nails, multiple hands, harsh contrast clipping, color saturation

**Director's note**: 시리즈 한 컷 — 추상적이지만 이야기가 있는.

---

### 10-3. 신부 디테일 (Bridal series)
- **File**: `studio/03-bridal-detail.jpg` · **Ratio**: 4:5

**Prompt**
```
A close-up of a bride's hand resting in a groom's palm, only hands visible, simple gold wedding band on her finger, white silk fabric of her dress in the background out of focus, soft natural daylight, shot on Leica M11 with 50mm at f/2, black and white with warm sepia tone, fine art wedding photography, Tartan Photography style, intimate quiet moment, no faces
```
**Negative**: multiple poses, full body, traditional wedding props, bright lighting, posed studio look

**Director's note**: 결혼식의 가장 작은 순간을 큰 화면에.

---

### 10-4. 풍경의 한 점 (Atmospheric)
- **File**: `studio/04-landscape.jpg` · **Ratio**: 4:5

**Prompt**
```
A minimalist black and white landscape, fog rolling over a single bare tree on a hill, deep grays and blacks with a single highlight of soft sky, no people, shot on Hasselblad X2D with 100mm at f/8, fine art landscape, monochrome with warm tone, Michael Kenna inspired, contemplative quiet
```
**Negative**: bright sunny landscape, vivid colors, vacation tourist look, multiple subjects, urban scene

**Director's note**: 시그니처 시리즈의 한 점. 인물·웨딩·풍경을 한 결로 묶음.

---

# 11. 학원 — 메리트 입시컨설팅

**브랜드 톤**: 네이비 + 옐로우 (#1e3a5f / #f0b429). 신중·학구.

### 11-1. 빈 강의실 (Hero)
- **File**: `academy/01-classroom.jpg` · **Ratio**: 4:5

**Prompt**
```
An empty modern small-scale Korean academy classroom, six wooden desks neatly arranged in two rows facing a clean white board, late afternoon golden light streaming through large windows on the right, dust visible in the light beams, dark navy painted accent wall, oak parquet floor, no people, no clutter, shot on Sony A7R V with 35mm at f/5.6, architectural editorial photography, navy oak gold palette, contemplative quiet, before-class atmosphere
```
**Negative**: large lecture hall, fluorescent overhead lights, motivational posters, multiple boards, students visible

**Director's note**: '수업이 막 끝난 뒤'. 정성스러운 학습의 자리.

---

### 11-2. 펜과 노트 (Detail)
- **File**: `academy/02-notebook-pen.jpg` · **Ratio**: 1:1

**Prompt**
```
A top-down close-up of a navy leather hardcover notebook open to a blank cream page, a single black ballpoint pen lying diagonally across, a small amber glass paperweight, an old wristwatch beside, on a warm walnut wood desk with subtle paper texture, soft late afternoon light from the right, shot on Canon R5 with 50mm macro at f/4, editorial detail photography, navy amber walnut palette, intentional study aesthetic
```
**Negative**: laptop, modern devices, branded items, cluttered desk, harsh lighting, colorful highlighters

**Director's note**: '한 자루의 펜과 한 권의 노트'로 학습의 본질.

---

### 11-3. 책 더미 (Atmospheric)
- **File**: `academy/03-books-stack.jpg` · **Ratio**: 4:5

**Prompt**
```
A tall stack of well-used Korean academic textbooks and reference books on a wooden side table, the books are slightly worn with bookmark tabs sticking out, soft window light from the left side casting shadows, a small green plant beside, navy painted wall background, shot on Fujifilm X-T5 with 50mm at f/4, editorial still life, navy yellow ochre palette, intellectual warmth, used books with care
```
**Negative**: brand new books, polished display, plastic covers, harsh light, multiple stacks competing

**Director's note**: '쌓아온 시간'이 보이는 책들. 새 책 X.

---

### 11-4. 컨설턴트 측면 인물 (Portrait)
- **File**: `academy/04-mentor-side.jpg` · **Ratio**: 4:5

**Prompt**
```
Editorial side profile of a Korean man in his early forties wearing a navy v-neck sweater over a white shirt, looking down at an open notebook, half of his face in soft shadow, warm window light from the left rim-lighting his temple, navy painted wall behind, shot on Leica SL2 with 75mm at f/2, editorial portrait, navy amber gold palette, contemplative listening posture
```
**Negative**: smiling at camera, gestures, full face, classroom busy background, multiple people

**Director's note**: '말하기보다 듣기'가 컨설턴트의 본질.

---

# 12. 제조 — 한울정밀

**브랜드 톤**: 스틸 + 블루 (#1a2733 / #006fb5). 정밀·산업.

### 12-1. 5축 가공기 클로즈업 (Hero)
- **File**: `manufacture/01-machine.jpg` · **Ratio**: 16:10

**Prompt**
```
A close-up of a precision 5-axis CNC milling machine in operation, polished steel spindle and blue precision guides illuminated by clean overhead industrial lighting, a metal precision part being machined with fine cooling mist visible, sharp focus on the cutting surface, shallow depth of field on the machine details, dark gunmetal background, shot on Sony A1 with 90mm macro at f/4, industrial editorial photography, steel blue gunmetal palette, Wallpaper magazine industrial aesthetic, technical precision
```
**Negative**: dirty oily workshop, rust, casual factory, fluorescent flicker, multiple machines, workers in shot

**Director's note**: 정밀의 시각화. 깨끗한 공장이 신뢰감의 출발.

---

### 12-2. 부품 매크로 (Detail)
- **File**: `manufacture/02-part-macro.jpg` · **Ratio**: 1:1

**Prompt**
```
An ultra macro shot of a precision-machined automotive metal component, polished aluminum surface with circular tool marks, micrometer-precision dimensions visible, set on a black anodized base plate with a small ruler showing micron scale, soft directional studio lighting from above-left, shot on Phase One IQ4 with 120mm macro at f/8, industrial product photography, cool steel blue palette, Bauhaus precision aesthetic, technical clarity
```
**Negative**: dirty parts, casual handling, multiple parts cluttered, warm lighting, organic objects

**Director's note**: 부품 자체가 주연. ±2㎛의 신뢰를 보여줄 정도의 디테일.

---

### 12-3. 측정실 CMM (Wide)
- **File**: `manufacture/03-cmm-room.jpg` · **Ratio**: 16:10

**Prompt**
```
An immaculate quality control measurement room with a 3D CMM coordinate measuring machine in the center, polished granite measurement table with a precision part placed on it, blue LED indicators, clean white walls, polished concrete floor, the room has the cleanliness of a semiconductor lab, no people, shot on Fujifilm GFX with 30mm at f/8, industrial architectural photography, cool steel white blue palette, IBM industrial design aesthetic, controlled environment
```
**Negative**: messy workshop, oil stains, casual lighting, multiple machines competing, workers visible

**Director's note**: 반도체 클린룸 수준의 정돈된 측정실.

---

### 12-4. 정돈된 가공 라인 (Wide 2)
- **File**: `manufacture/04-line-clean.jpg` · **Ratio**: 16:10

**Prompt**
```
A clean modern Korean precision parts factory production line, six identical CNC machines aligned in a row receding into the distance, polished concrete floor with painted blue safety lines, overhead industrial LED lighting, no people, the entire space immaculately clean, shot on Sony A7R V with 24mm at f/8, industrial architectural photography, steel blue concrete white palette, Toyota production aesthetic, precision workspace
```
**Negative**: dirty factory floor, oil leaks, casual workers, fluorescent yellow lighting, cluttered tools

**Director's note**: '월 8만 EA' 의 정돈. 한국 대기업 1차 협력사 수준의 청결.

---

## 📦 요약 표

| # | 업종 | 1번 | 2번 | 3번 | 4번 |
|---|---|---|---|---|---|
| 01 | 치과 | 진료실 한 켠 | 손과 모형 | 빈 진료의자 | 식물과 빛 |
| 02 | 법무 | 만년필과 종이 | 책장 디테일 | 코너 오피스 | 변호사 측면 |
| 03 | 카페 | 카운터의 잔 | 손과 잔 | 빈 자리 | 베이커리 |
| 04 | 다이닝 | 다크 한 그릇 | 플레이팅 손 | 14석 카운터 | 셰프 측면 |
| 05 | 인테리어 | 빈 거실 | 바닥의 빛 | 단정한 복도 | 돌 카운터 |
| 06 | 필라테스 | 리포머 | 등 실루엣 | 빈 스튜디오 | 손과 폼롤러 |
| 07 | 에스테틱 | 도자기 앰플 | 손목 디테일 | 시술실 한 켠 | 손과 병 |
| 08 | SaaS | 다크 대시보드 | 슬랙 통합 | 단일 소스 | 결정 로그 |
| 09 | 풀빌라 | 외관 | 큰 창의 산 | 자작나무숲 | 노천탕 |
| 10 | 스튜디오 | 인물 클로즈업 | 빛에 손 | 신부 디테일 | 풍경 |
| 11 | 학원 | 빈 강의실 | 펜과 노트 | 책 더미 | 컨설턴트 측면 |
| 12 | 제조 | 5축 가공기 | 부품 매크로 | CMM 측정실 | 가공 라인 |

총 **48장**.

---

## 🛠️ 추가 팁

- **Midjourney v6**에서 가장 시네마틱 결과: 프롬프트 끝에 `--style raw --ar 4:5 --s 250` 추가
- **DALL·E 3**: 자연스러운 결과를 원하면 "natural lighting" / "documentary photography" 키워드 강조
- **Flux 1.1 Pro**: 텍스트 정확성·디테일이 강점. 위 프롬프트 그대로 입력
- **인물 사진**: 같은 모델로 일관성을 원하면 Midjourney의 `--cref [이미지URL]` 사용

생성 후 컬러 그레이딩이 너무 강하면 채도를 -10~-20% 낮춰 주시면 브랜드 톤과 조화롭습니다.
