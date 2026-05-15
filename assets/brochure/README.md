# NOAH 소개서 PDF

이 폴더에 소개서 PDF를 업로드해주세요.

## 파일 이름 (고정)

```
NOAH-brochure.pdf
```

> 한글 파일명도 동작하지만, 일부 모바일 브라우저에서 URL 인코딩이 깨지는 사례가 있어 영문 이름을 사용합니다. 다운로드 시 사용자에게는 `NOAH_소개서.pdf`로 표시됩니다 (`download` 속성).

## 업로드 후 확인

- 파일 경로: `/assets/brochure/NOAH-brochure.pdf`
- 사이트 접근 URL: `https://<도메인>/assets/brochure/NOAH-brochure.pdf`
- 사이트 우상단 "소개서 받기" 버튼 → 양식 제출 시 자동 다운로드 시작

## PDF 변경 시

같은 이름(`NOAH-brochure.pdf`)으로 덮어쓰기 + 커밋 + 푸시.
Cloudflare Pages가 자동 재배포하며 1년 캐시 헤더는 콘텐츠 해시 무관하게 갱신됩니다 (Cloudflare가 자동 무효화).

캐시 우려가 있으시면 파일명에 버전을 붙이고 (`NOAH-brochure-v2.pdf`) `index.html`의 `BROCHURE_URL` 상수를 수정하세요.
