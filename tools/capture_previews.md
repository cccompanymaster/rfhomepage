# 쇼룸 프리뷰 스크린샷 재생성

쇼룸 카드의 목업 이미지(`assets/images/previews/*.webp`)를 다시 만드는 방법입니다.
템플릿 디자인을 고친 뒤에만 실행하면 됩니다.

## 왜 이미지인가

예전에는 카드마다 실제 템플릿을 iframe으로 띄웠습니다(18개 × 2 = 36개).
카드 하나가 뜰 때마다 Tailwind·폰트를 새로 받아서 쇼룸 로딩이 크게 느려졌습니다.
지금은 미리 캡처한 WebP 36장(합계 약 780KB)을 씁니다.

## 준비

```bash
mkdir -p /tmp/shot && cd /tmp/shot && npm init -y
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i -D playwright tailwindcss@3 pretendard
```

## 1) Tailwind 로컬 빌드

템플릿은 Tailwind CDN을 쓰는데, 캡처 환경에서는 CDN을 못 받을 수 있어 미리 CSS로 뽑습니다.

```bash
cat > tw.config.js <<'X'
module.exports = { content: ['/home/user/rfhomepage/**/*.html'] }
X
echo '@tailwind base;@tailwind components;@tailwind utilities;' > in.css
npx tailwindcss -c tw.config.js -i in.css -o tw.css --minify
```

## 2) 템플릿 사본 만들기 (CDN → 로컬 치환)

`templates/`, `assets/`를 `site/`로 복사한 뒤 각 HTML에서
- `cdn.tailwindcss.com` 스크립트 → `../assets/tw.css`
- Pretendard jsdelivr → `../assets/pretendard/pretendardvariable.css`
로 바꿉니다.

## 3) 캡처

```bash
SD=/tmp/shot node /home/user/rfhomepage/tools/capture_previews.js
```

데스크톱 1440×900, 모바일 390×844, 2배 해상도로 `raw/`에 PNG가 생성됩니다.
등장 애니메이션은 스크립트가 강제로 완료 처리하고 카운트업 숫자도 최종값으로 고정합니다.

## 4) WebP 변환

```python
from PIL import Image; import glob, os
OUT='/home/user/rfhomepage/assets/images/previews'
for f in sorted(glob.glob('/tmp/shot/raw/*.png')):
    n=os.path.basename(f)[:-4]
    im=Image.open(f).convert('RGB')
    w=880 if 'desktop' in n else 300
    im.resize((w, round(im.height*w/im.width)), Image.LANCZOS).save(f'{OUT}/{n}.webp','WEBP',quality=80,method=6)
```

## 새 템플릿을 추가했다면

`templates/<이름>.html`을 만들고 위 과정을 다시 돌리면 `<이름>-desktop.webp`,
`<이름>-mobile.webp`가 생깁니다. `index.html` 카드에서 그 경로를 참조하세요.
