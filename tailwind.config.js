/**
 * Tailwind 빌드 설정 — CDN 런타임(cdn.tailwindcss.com) 대신 미리 빌드한 CSS를 씁니다.
 * 빌드: python3 tools/build_assets.py   (클래스를 새로 쓴 뒤에는 꼭 다시 빌드)
 */
module.exports = {
  content: [
    './*.html',
    './templates/*.html',
    './columns/**/*.html',
    './assets/js/*.js',
    './tools/build_columns.py',
  ],
  theme: { extend: {} },
  plugins: [],
};
