# 상담 신청 → 구글 시트 연동 셋업 가이드

NOAH 메인 페이지의 상담 신청 폼을 **구글 시트에 자동 저장**하기 위한 Google Apps Script 셋업 방법입니다. 코딩 지식 없어도 따라 할 수 있도록 구성했습니다.

소요 시간: **약 10분**

---

## 1단계 — 구글 시트 만들기

1. https://sheets.google.com 접속
2. **새 스프레드시트** 클릭
3. 시트 이름을 `NOAH 상담 신청` 으로 변경
4. **첫 번째 행(1행)에 헤더** 입력 (정확히 이 순서대로):

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| timestamp | name | phone | email | industry | reference | message | referrer |

> **중요**: 이 컬럼명은 폼의 `name` 속성과 정확히 일치해야 합니다. 추가/삭제는 가급적 피하세요.

---

## 2단계 — Apps Script 코드 붙여넣기

1. 만든 시트에서 상단 메뉴 → **확장 프로그램** → **Apps Script** 클릭
2. 새로 열린 창에서 기본 `function myFunction() { ... }` 코드를 모두 지우고 아래 코드를 붙여넣으세요:

```javascript
// =============================================================
// NOAH 상담 신청 — Google Sheets 자동 저장 스크립트
// =============================================================

// 시트가 1개뿐이면 그대로, 여러 개면 정확한 시트 이름으로 변경
const SHEET_NAME = '시트1';

function doPost(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);

    // 폼에서 보낸 JSON 파싱
    const data = JSON.parse(e.postData.contents);

    // 헤더 순서대로 한 행에 저장
    sheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.name      || '',
      data.phone     || '',
      data.email     || '',
      data.industry  || '',
      data.reference || '',
      data.message   || '',
      data.referrer  || '',
    ]);

    // (선택) 알림 메일 받고 싶으면 아래 두 줄 주석 해제 + 본인 이메일 입력
    // const NOTIFY_EMAIL = 'hello@noah.kr';
    // MailApp.sendEmail(NOTIFY_EMAIL, '[NOAH] 새 상담 신청', JSON.stringify(data, null, 2));

    return ContentService.createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// 테스트용 — 이걸 한 번 실행해서 권한 부여
function testInsert() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  sheet.appendRow([
    new Date().toISOString(),
    '테스트 신청',
    '010-0000-0000',
    'test@example.com',
    '카페·베이커리',
    '03 오월의 다정 (카페)',
    '테스트 메시지입니다',
    '테스트 환경',
  ]);
}
```

3. 좌측 상단 **저장 버튼**(💾) 클릭 후 프로젝트 이름은 `NOAH 상담 폼`으로 입력

---

## 3단계 — 권한 부여 (1회만)

1. 상단 함수 선택 드롭다운에서 **`testInsert`** 선택
2. **▶ 실행** 클릭
3. "권한 검토" 팝업 → **권한 검토** 클릭
4. 본인 구글 계정 선택
5. "Google에서 확인하지 않은 앱" 경고 → 아래 작은 글씨 **고급** → **'NOAH 상담 폼'(안전하지 않음)으로 이동** 클릭
6. **허용** 클릭

> ⚠️ "안전하지 않음" 경고는 본인이 만든 스크립트라 정상입니다. 보안 우려 없습니다.

7. 시트로 돌아가 보면 테스트 행 하나가 추가되어 있을 거예요. ✓

---

## 4단계 — Web App으로 배포

1. Apps Script 화면 우측 상단 **배포** → **새 배포** 클릭
2. ⚙️ 톱니바퀴 → **웹 앱** 선택
3. 다음과 같이 설정:

| 항목 | 값 |
|---|---|
| 설명 | `NOAH 상담 폼 v1` |
| 다음 사용자로 실행 | **나** |
| 액세스 권한 | **모든 사용자** ⚠️ 꼭 이 옵션! |

4. **배포** 클릭
5. **웹 앱 URL** 복사 (`https://script.google.com/macros/s/AKfyc.../exec` 형식)

---

## 5단계 — 홈페이지에 URL 붙여넣기

1. `index.html` 파일을 텍스트 에디터로 열기
2. 다음 줄 찾기 (페이지 맨 아래쪽):

```javascript
const GAS_URL = 'https://script.google.com/macros/s/PASTE_YOUR_DEPLOYMENT_ID/exec';
```

3. 위 4단계에서 복사한 URL로 교체:

```javascript
const GAS_URL = 'https://script.google.com/macros/s/AKfyc...실제URL.../exec';
```

4. 저장하고 GitHub에 푸시 (또는 호스팅 서버에 업로드)

---

## 6단계 — 테스트

1. 배포된 사이트 접속
2. 상담 신청 폼에 테스트 데이터 입력 후 제출
3. 구글 시트에 행이 추가되는지 확인

> 보통 1~3초 안에 시트에 들어옵니다. 안 들어온다면 아래 문제 해결 참고.

---

## 🔔 (선택) 새 신청 메일 알림 받기

위 코드에서 다음 두 줄의 `//`를 지우면 새 신청마다 본인 이메일로 알림이 옵니다:

```javascript
const NOTIFY_EMAIL = 'hello@noah.kr';  // ← 본인 이메일로 변경
MailApp.sendEmail(NOTIFY_EMAIL, '[NOAH] 새 상담 신청', JSON.stringify(data, null, 2));
```

알림 메일을 더 예쁘게 받고 싶으면 `JSON.stringify(...)` 부분을 다음으로 교체:

```javascript
`성함: ${data.name}\n연락처: ${data.phone}\n이메일: ${data.email}\n업종: ${data.industry}\n관심 결: ${data.reference}\n문의: ${data.message}\n시간: ${data.timestamp}`
```

---

## 🚨 카카오 알림톡으로 받고 싶다면

알림톡은 비즈톡/알리고 등 별도 API 발급이 필요합니다. 가장 쉬운 우회 방법:

1. **IFTTT** 또는 **Zapier**로 구글 시트 → 카카오톡 알림 자동화
2. 또는 **솔라피(Solapi)·알리고** API + Apps Script `UrlFetchApp` 사용

이 부분은 운영 들어간 뒤 별도로 셋업 권장 — 우선은 **이메일 알림**으로 충분합니다.

---

## 🔧 문제 해결

### 신청 후 시트에 아무것도 안 들어옴
- 4단계 **액세스 권한**이 "모든 사용자" 가 맞는지 확인
- 5단계 URL이 정확한지 (마지막 `/exec` 확인)
- 브라우저 개발자도구(F12) → Network 탭 → 폼 제출 → 응답 확인 (CORS 에러여도 정상, no-cors 모드라 응답 못 봄)

### "권한이 거부됨" 에러
- 3단계 권한 부여를 다시 진행 (스크립트 처음 실행 시 한 번 필요)

### 코드 수정 후 반영 안 됨
- Apps Script에서 코드 수정 → **저장** → **배포 → 배포 관리 → 편집(연필)** → **새 버전** → **배포** 순서로 갱신해야 적용됨
- ⚠️ 단순 저장만으로는 배포된 Web App에 반영되지 않음

### 한국어 깨짐
- 위 코드는 UTF-8로 잘 처리되나, 시트에서 깨지면 **파일 → 다운로드 → CSV** 시 BOM 옵션 켜기

---

## 📊 시트를 더 똑똑하게 (선택)

- **조건부 서식**: 신청일 24시간 이내 행 강조 (`=NOW() - A2 < 1`)
- **빠른 답장 컬럼 추가**: I열에 "회신함" 체크박스
- **Looker Studio 연동**: 시트 데이터로 대시보드 자동 생성
- **WhatsApp/Slack 알림**: Apps Script `UrlFetchApp`으로 외부 서비스 연동

---

이상입니다. 막히는 부분 있으면 알려주세요.
