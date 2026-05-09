# 상담 신청 + 소개서 자동 발송 — 셋업 가이드

NOAH 메인의 두 가지 폼을 **하나의 Apps Script로** 처리합니다.

1. **상담 신청 폼** (하단 `#consult`) → 구글 시트의 `NOAH 상담` 탭에 저장
2. **소개서 다운로드 폼** (헤더 모달) → `NOAH 소개서` 탭에 저장 + **소개서 PDF 자동 메일 발송**

소요 시간: **약 15분**

---

## 1단계 — 구글 시트 두 탭 만들기

기존 시트에 새 탭 두 개를 추가합니다 (또는 새 시트를 만들어도 OK).

### 탭 1: `NOAH 상담`

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| timestamp | name | phone | email | industry | reference | message | referrer |

### 탭 2: `NOAH 소개서`

| A | B | C | D | E |
|---|---|---|---|---|
| timestamp | name | email | phone | industry |

---

## 2단계 — 소개서 PDF를 구글 드라이브에 업로드

1. https://drive.google.com 접속
2. **새로 만들기 → 파일 업로드** → `NOAH_소개서.pdf` 업로드
3. 업로드한 파일 우클릭 → **링크 가져오기** 또는 파일을 열고 URL 확인
4. URL에서 **파일 ID** 추출:
   ```
   https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUv_FILE_ID/view
                                   ↑ 이 부분이 파일 ID
   ```
5. 파일 ID 메모해두기 (예: `1AbCdEfGhIjKlMnOpQrStUv`)

> ⚠️ **공유 권한**: Apps Script가 본인 계정에서 실행되므로 별도 공유 설정 불필요. 본인이 소유한 파일이면 OK.

---

## 3단계 — Apps Script 코드 붙여넣기

1. 시트에서 **확장 프로그램 → Apps Script** 클릭
2. 기본 코드 모두 지우고 아래 코드 붙여넣기:

```javascript
// =============================================================
// NOAH — 상담 신청 + 소개서 자동 발송 통합 스크립트
// =============================================================

const CONSULT_SHEET = 'NOAH 상담';            // 상담 신청 탭 이름
const BROCHURE_SHEET = 'NOAH 소개서';          // 소개서 신청 탭 이름
const BROCHURE_FILE_ID = 'PASTE_YOUR_FILE_ID'; // ← 2단계에서 메모한 PDF 파일 ID
const NOTIFY_EMAIL = 'noahmaster@gmail.com';   // 운영자 알림 메일

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    if (data.type === 'brochure') {
      handleBrochure(data);
    } else {
      handleConsult(data);
    }

    return ContentService.createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// -------------------- 상담 신청 처리 --------------------
function handleConsult(data) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONSULT_SHEET);
  if (!sheet) throw new Error('Sheet not found: ' + CONSULT_SHEET);

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

  // 운영자 알림 메일
  MailApp.sendEmail({
    to: NOTIFY_EMAIL,
    subject: `[NOAH] 새 상담 신청 — ${data.name}`,
    htmlBody: `
      <div style="font-family:-apple-system,sans-serif;line-height:1.6;">
        <h3>새 상담 신청이 도착했습니다.</h3>
        <p><strong>성함</strong>: ${data.name}<br/>
        <strong>연락처</strong>: ${data.phone}<br/>
        <strong>이메일</strong>: ${data.email || '미기입'}<br/>
        <strong>업종</strong>: ${data.industry}<br/>
        <strong>관심 디자인</strong>: ${data.reference || '미정'}<br/>
        <strong>문의</strong>: ${data.message || '없음'}</p>
        <p style="color:#888;font-size:12px;">시간: ${data.timestamp}</p>
      </div>
    `,
  });
}

// -------------------- 소개서 자동 발송 처리 --------------------
function handleBrochure(data) {
  // 1) 시트에 신청 기록
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(BROCHURE_SHEET);
  if (!sheet) throw new Error('Sheet not found: ' + BROCHURE_SHEET);

  sheet.appendRow([
    data.timestamp || new Date().toISOString(),
    data.name      || '',
    data.email     || '',
    data.phone     || '',
    data.industry  || '',
  ]);

  // 2) 소개서 PDF를 신청자 이메일로 발송
  if (!data.email) throw new Error('email required for brochure');

  const file = DriveApp.getFileById(BROCHURE_FILE_ID);
  const blob = file.getBlob();

  MailApp.sendEmail({
    to: data.email,
    subject: '[NOAH] 요청하신 소개서를 보내드립니다',
    htmlBody: `
      <div style="font-family:-apple-system,'Apple SD Gothic Neo',sans-serif; max-width:560px; padding:24px; color:#222;">
        <h2 style="background:linear-gradient(135deg,#7c5cff,#ff7ac6); -webkit-background-clip:text; background-clip:text; color:transparent; font-size:28px; margin:0 0 16px;">NOAH 소개서</h2>
        <p style="font-size:15px;">${data.name}님 안녕하세요,</p>
        <p style="font-size:15px;">요청하신 NOAH 홈페이지 제작 소개서를 첨부해 드립니다.<br/>
        12개 업종 레퍼런스, 7일 제작 과정, ₩199,000 패키지 안내가 한 권에 담겨 있습니다.</p>
        <p style="font-size:15px;">궁금하신 점이 있으시면 언제든 답장 주세요.</p>
        <hr style="border:0; border-top:1px solid #eee; margin:24px 0;" />
        <p style="font-size:13px; color:#666;">
          <strong style="color:#222;">NOAH · 노아홈페이지</strong><br/>
          010-6658-6482<br/>
          noahmaster@gmail.com
        </p>
      </div>
    `,
    attachments: [blob],
    name: 'NOAH',
  });

  // 3) 운영자 알림
  MailApp.sendEmail({
    to: NOTIFY_EMAIL,
    subject: `[NOAH] 새 소개서 요청 — ${data.name}`,
    body: `이름: ${data.name}\n이메일: ${data.email}\n연락처: ${data.phone || '미기입'}\n업종: ${data.industry || '미기입'}\n시간: ${data.timestamp}\n\n→ 소개서가 신청자에게 자동 발송되었습니다.`,
  });
}

// -------------------- 테스트 함수 --------------------
function testConsult() {
  handleConsult({
    timestamp: new Date().toISOString(),
    name: '테스트 상담', phone: '010-0000-0000', email: 'test@example.com',
    industry: '카페·베이커리', reference: '03 오월의 다정',
    message: '테스트 문의입니다', referrer: '테스트',
  });
}
function testBrochure() {
  handleBrochure({
    timestamp: new Date().toISOString(),
    name: '테스트 소개서', email: 'YOUR_EMAIL@gmail.com',  // ← 본인 이메일로 변경
    phone: '010-0000-0000', industry: '카페·베이커리',
  });
}
```

3. **저장 (Ctrl+S)**, 프로젝트 이름은 `NOAH 통합 폼`

---

## 4단계 — 권한 부여 (1회)

1. 상단 함수 드롭다운에서 **`testBrochure`** 선택
2. ⚠️ 위 코드의 `testBrochure` 함수에서 `YOUR_EMAIL@gmail.com`을 본인 이메일로 변경 후 저장
3. **▶ 실행** 클릭 → 권한 검토 → 본인 계정 선택 → "고급" → "안전하지 않음" → 허용
4. 본인 이메일 받은편지함 확인 — NOAH 소개서가 첨부된 메일이 도착하면 ✅

---

## 5단계 — Web App 배포

1. 우측 상단 **배포 → 새 배포**
2. ⚙️ → **웹 앱**
3. 설정:
   - 설명: `NOAH 통합 폼 v1`
   - 다음 사용자로 실행: **나**
   - 액세스 권한: **모든 사용자** ⚠️ 꼭!
4. **배포** → **웹 앱 URL 복사** (`https://script.google.com/macros/s/.../exec`)

---

## 6단계 — 홈페이지에 URL 붙여넣기

`index.html`에서 다음 줄 찾기:

```javascript
const GAS_URL = 'https://script.google.com/macros/s/PASTE_YOUR_DEPLOYMENT_ID/exec';
```

위에서 복사한 URL로 교체.

---

## 7단계 — 테스트

배포된 사이트에서:

1. 우상단 **"소개서 받기"** 버튼 클릭
2. 본인 이메일 입력 후 제출
3. 1~5분 안에 소개서 메일 수신 ✓
4. 시트 `NOAH 소개서` 탭에 행 추가 확인 ✓
5. 운영자 알림 메일 수신 확인 ✓

상담 신청 폼도 동일하게 테스트 (시트 `NOAH 상담` 탭 + 운영자 알림).

---

## 📌 코드 수정 후 재배포 필수

Apps Script 코드를 바꿨으면 반드시:
- **배포 → 배포 관리 → 편집(연필) → 새 버전 → 배포**

단순 저장만으로는 Web App에 반영 안 됩니다.

---

## 🔧 자주 묻는 문제

### 메일 발송 한도
- Gmail 일반 계정: **하루 100통** 발송 한도
- Workspace 계정: **하루 1,500통**
- 한도 초과 시 다음 날 자동 리셋

### 첨부 파일 크기
- 메일 첨부 가능 PDF: **최대 25MB**
- NOAH 소개서가 25MB 초과면, 구글 드라이브 공유 링크를 본문에 넣는 방식으로 변경

### 신청자에게 메일이 안 가요
- `BROCHURE_FILE_ID`가 정확한지 확인
- Apps Script 실행 사용자(=본인)가 해당 파일 소유자/편집자인지 확인
- 받는 사람 메일 주소 오타 확인

### 스팸으로 분류돼요
- Gmail로 발송하므로 대부분 정상 인박스 도착
- 첫 발송 시 받는 사람이 "스팸 아님" 표시 한 번 해두면 이후 안전

---

## 🎁 (선택) 더 발전시키기

- **PDF 자동 생성**: Google Slides/Docs를 PDF로 변환해 매번 최신 소개서 첨부
- **A/B 테스트**: 두 가지 소개서 PDF를 번갈아 발송 (홀짝 시간으로 분기)
- **신청자 추적**: 소개서 첨부 PDF에 신청자별 UTM 파라미터 페이지 링크 삽입
- **Slack 알림**: 운영자 메일 대신/병행해 Slack 채널로 알림

이상입니다. 막히는 부분 있으면 알려주세요.
