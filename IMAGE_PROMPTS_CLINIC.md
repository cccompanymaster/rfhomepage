# 본연 클리닉 (성형외과·피부과) — 이미지 생성 프롬프트 모음

> Midjourney / DALL-E / Stable Diffusion 용.
> 생성 후 `assets/images/clinic/` 에 저장하고 `templates/clinic.html` 의 플레이스홀더와 교체.
>
> **전 이미지 공통 스타일 수식어** (모든 프롬프트 뒤에 붙이기):
> `premium Korean medical luxury, black white ivory warm-gray palette, Swiss editorial design, cinematic soft lighting, consistent skin tone and lens mood, clean negative space for typography, photorealistic, 8k --style raw`
>
> **공통 네거티브 프롬프트**:
> `low quality, blurry, distorted face, asymmetrical eyes, deformed hands, extra fingers, plastic skin, over-retouched face, unrealistic surgery result, blood, wound, gore, scary medical scene, fake logo, fake text, watermark, duplicated person, collage, random typography, exaggerated body proportions, misleading before and after, identifiable real patient`

---

## 1. 메인 히어로 (각 비율: 21:9 / 16:9 / 4:5 / 9:16)

| 파일명 | 프롬프트 |
|---|---|
| `hero-face-light.jpg` | confident East Asian adult model, natural expression, front view, bright minimal studio, wide copy space on left |
| `hero-face-dark.jpg` | East Asian adult model, 45-degree angle, dark cinematic background, rim lighting, editorial fashion magazine mood |
| `hero-skin.jpg` | close-up of healthy natural skin texture on cheek and jawline, soft window light, no retouching artifacts |
| `hero-body.jpg` | elegant silhouette of adult figure in ivory fabric, abstract, tasteful, no exposed skin beyond shoulders |
| `hero-man.jpg` | East Asian adult male model, side profile, charcoal background, sharp jawline in natural proportion |
| `hero-building.jpg` | modern medical building exterior at dusk, glass and warm light, architectural photography |

## 2. 병원 소개

- `intro-lobby.jpg` — luxurious clinic lobby with reception desk, ivory marble, warm indirect lighting
- `intro-vip.jpg` — private VIP consultation room, two chairs, soft daylight
- `intro-or-corridor.jpg` — pristine surgical center corridor, frosted glass, cool clean light
- `intro-recovery.jpg` — calm recovery room, single bed, warm blanket, morning light
- `intro-checkup.jpg` — modern health screening center, orderly medical equipment
- `intro-derma-lounge.jpg` — dermatology lounge with lounge chairs and greenery
- `intro-round.jpg` — medical staff in navy scrubs walking corridor, backs to camera, anonymous

## 3. 의료진 프로필 (전원 동일 조명·구도)

- `dr-01.jpg` ~ `dr-06.jpg` — upper-body front portrait, East Asian doctor in white coat (or navy), pale gray seamless background, natural trustworthy smile, identical lighting setup across all portraits

## 4. 시술 분야별 (각 1장, 상담/분석 장면 위주 — 시술 장면 금지)

- `cat-breast.jpg` — consultation scene, doctor showing implant sample case to patient (hands only)
- `cat-contour.jpg` — 3D facial analysis on monitor, side view of patient face with grid overlay
- `cat-jaw.jpg` — doctor reviewing 3D CT skull render on dual monitors
- `cat-eye.jpg` — close-up of natural East Asian eyes, soft light, no makeup
- `cat-nose.jpg` — side profile of nose line, measuring calipers held nearby, clinical but calm
- `cat-lipo.jpg` — body composition analysis machine, patient standing, staff guiding
- `cat-lifting.jpg` — graceful East Asian middle-aged model, natural skin, warm light
- `cat-man.jpg` — East Asian male model front view, neutral expression, editorial
- `cat-derma.jpg` — dermatology laser equipment in treatment room, no procedure in progress
- `cat-hair.jpg` — scalp diagnosis camera device on desk, clean clinical setup
- `cat-stemcell.jpg` — healthy senior couple walking in park, wellness lifestyle

## 5. 전후사진 · 후기 프레임

> ⚠️ **전후 사진 자체를 생성하지 말 것.** 승인된 실제 자료로 교체할 **빈 프레임/배경만** 생성.

- `ba-frame-bg.jpg` — empty ivory photo frame pair on gallery wall, identical lighting both frames
- `selfie-style-01~03.jpg` — natural smartphone-style selfie of consented East Asian model, casual indoor light, believable everyday quality (no dramatic change implied)

## 6. 이벤트 배너 (텍스트 삽입 공간 확보, 문구 생성 금지)

- `event-pc-01~04.jpg` (가로 16:5) — black/ivory luxury banner background: face close-up crop / skin texture / clinic space / silhouette, 60% empty space for typography
- `event-mo-01~04.jpg` (세로 4:5) — 동일 콘셉트 모바일 버전

## 7. 유튜브·숏폼 썸네일

- `yt-interview.jpg` (16:9) — doctor seated for interview, softbox lighting, left third empty for title
- `yt-tour.jpg` (16:9) — wide shot of clinic lobby, top third empty
- `shorts-qna.jpg` (9:16) — doctor facing camera waist-up, bottom third empty for captions

---

### 교체 체크리스트
- [ ] 모든 인물은 허가된 가상 모델 — 실존 인물 유사성 확인
- [ ] 이미지 내 텍스트/로고/워터마크 없음
- [ ] 동일 색감·조명 톤 유지 (LUT 일괄 적용 권장)
- [ ] WebP 변환 + 1920px 리사이즈 후 업로드
