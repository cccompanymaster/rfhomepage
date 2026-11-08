# 상담 신청 + 소개서 자동 발송 — 셋업 가이드

NOAH의 세 가지 폼을 **하나의 Apps Script로** 처리합니다.

1. **상담 신청 폼** (하단 `#consult`) → 구글 시트의 `NOAH 상담` 탭에 저장 + 운영자 알림 메일
2. **소개서 다운로드 폼** (헤더 모달) → `NOAH 소개서` 탭에 저장 + (선택) 신청자에게 확인 메일
3. **사전 정보 시트** (`/intake.html`, 계약 고객 전달용) → `NOAH 사전정보` 탭에 한 줄 기록 + 전체 항목을 운영자에게 메일 발송 + (선택) 고객 확인 메일 (`type: 'intake'`)

> **PDF는 더 이상 메일에 첨부하지 않습니다.**
> 소개서 PDF는 사이트 리포지토리(`/assets/brochure/NOAH-brochure.pdf`)에 호스팅되며, 폼 제출 즉시 사용자 브라우저에서 다운로드가 시작됩니다. Apps Script는 **리드(lead) 기록과 백업 이메일 발송**만 담당합니다.

소요 시간: **약 10분** (기본 모드 기준)

---

## 🔒 보안 강화판으로 바꾸기 (2026-11) — 이미 쓰고 계신 분은 이것만 하세요

**왜 바꾸나요?** 웹 앱 주소는 사이트 코드에 들어 있어서 누구나 볼 수 있어요. 예전 코드는 이 주소로 아무 요청이나 보내면 사장님 Gmail로 **남에게 메일을 대신 보내 줬어요.** 입력값에 링크나 HTML을 넣으면 그대로 메일 본문에 들어갔고요. 이렇게 되면 스팸 발송에 악용되고, 하루 100통 한도가 바닥나서 진짜 상담 알림도 못 받게 돼요.

**새 코드에서 달라진 점**
- 입력값의 HTML·링크는 메일에 글자 그대로만 보여요.
- 같은 주소로는 10분에 한 통만 보내요. 신청자 메일은 하루 40통, 운영자 알림은 하루 50통까지만 보내요.
- 봇이 채우는 숨은 칸(`website`)이 채워진 요청은 무시해요.
- 시트에 `=`로 시작하는 값은 수식이 아니라 글자로 저장해요.

**바꾸는 순서 (5분)**
1. 구글 시트 → **확장 프로그램 → Apps Script**를 여세요.
2. 지금 코드 맨 위의 `NOTIFY_EMAIL` 값을 메모하세요. 알림을 받는 메일 주소예요.
3. 코드를 **전부 지우고** 아래 2단계 코드를 통째로 붙여 넣으세요.
4. 맨 위 `NOTIFY_EMAIL`을 2번에서 메모한 값으로 되돌리고 **저장(Ctrl+S)**을 누르세요.
5. 함수 목록에서 `testSecurity`를 고르고 **▶ 실행**하세요. 권한 창이 뜨면 허용하세요.
   - 운영자 메일에 `<b>굵게</b>`가 **글자 그대로** 보이면 정상이에요.
   - 시트 `NOAH 상담` 탭에 `=1+1`이 **글자로** 들어가 있으면 정상이에요.
   - 확인한 뒤 테스트 행은 지워도 돼요.
6. **배포 → 배포 관리 → 연필(편집) → 버전: 새 버전 → 배포**를 누르세요.
   - ⚠️ **새 배포**를 누르면 안 돼요. 웹 앱 주소가 바뀌어서 사이트 폼이 끊겨요. 반드시 **배포 관리**에서 기존 배포를 편집하세요.
7. 사이트에서 소개서 받기를 한 번 해서 메일이 오는지 확인하세요.

---

## 1단계 — 구글 시트 두 탭 만들기

기존 시트에 새 탭 두 개를 추가합니다 (또는 새 시트를 만들어도 OK).

### 탭 1: `NOAH 상담`

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| timestamp | name | phone | email | industry | reference | message | referrer |

### 탭 2: `NOAH 소개서`

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| timestamp | name | email | phone | industry | referrer |

### 탭 3: `NOAH 사전정보`

> **만들 필요 없습니다.** 첫 사전정보 시트가 제출되면 `handleIntake`가 탭을 자동 생성하고 헤더(timestamp · 회신이메일 · 상호 · A~H 전 항목 · referrer)까지 깔아줍니다.

---

## 2단계 — Apps Script 코드 붙여넣기 (기본 모드)

1. 시트에서 **확장 프로그램 → Apps Script** 클릭
2. 기본 코드 모두 지우고 아래 코드 붙여넣기:

```javascript
// =============================================================
// NOAH — 상담·소개서·사전정보·주문 접수 통합 스크립트 (보안 강화판 v2 · 2026-11)
// PDF는 사이트에서 바로 내려받으므로 메일에 첨부하지 않습니다.
//
// v2에서 막은 것
//  - 메일 본문에 들어가는 입력값을 모두 이스케이프 → 남의 링크·HTML을 끼워 넣은 스팸 메일 차단
//  - 시트에 = + - @ 로 시작하는 값은 글자로 저장 → 수식 실행(외부로 시트 내용 빼돌리기) 차단
//  - 사람 눈에 안 보이는 칸(website)이 채워진 요청은 봇으로 보고 무시
//  - 발송 한도: 같은 주소로 10분에 1통, 신청자 메일 하루 40통, 운영자 알림 하루 50통
//    → 누가 이 주소로 요청을 퍼부어도 Gmail 하루 100통 한도를 다 써 버리지 못함
//  - 칸마다 글자 수 제한, 이메일 형식이 아니면 신청자 메일을 보내지 않음
//  - 오류 내용은 밖으로 돌려주지 않고 실행 로그에만 남김
// =============================================================

// ▼ 이 네 줄은 지금 쓰시는 값을 그대로 두세요
const NOTIFY_EMAIL    = 'noahmaster@gmail.com';          // 운영자 알림을 받을 메일
const SITE_URL        = 'https://noahhomepage.co.kr';    // 사이트 주소 (메일 속 링크)
const SEND_USER_EMAIL = true;                            // 신청자 확인 메일 (false면 시트 기록 + 운영자 알림만)
const CONTACT_LINE    = '010-6658-6482 · cccompanymaster@gmail.com'; // 메일 서명

const CONSULT_SHEET  = 'NOAH 상담';
const BROCHURE_SHEET = 'NOAH 소개서';
const INTAKE_SHEET   = 'NOAH 사전정보';

// ▼ 발송·기록 한도 (필요하면 숫자만 조정)
const LIMIT_USER_MAIL_PER_DAY   = 40;   // 신청자에게 가는 메일 하루 최대
const LIMIT_NOTIFY_PER_DAY      = 50;   // 운영자 알림 하루 최대 (넘으면 시트에만 기록)
const LIMIT_ROWS_PER_DAY        = 300;  // 시트 기록 하루 최대 (넘으면 버림)
const SAME_ADDRESS_COOLDOWN_SEC = 600;  // 같은 주소로 다시 보내기까지 기다리는 시간(초)
const KEEP_QUOTA_FOR_NOTIFY     = 10;   // Gmail 남은 한도가 이보다 적으면 신청자 메일은 보내지 않음

// -------------------- 진입점 --------------------
function doPost(e) {
  try {
    const raw = (e && e.postData && e.postData.contents) || '';
    if (!raw || raw.length > 60000) return reply_(true);          // 비었거나 비정상적으로 큰 요청
    const data = JSON.parse(raw);
    if (!data || typeof data !== 'object' || Array.isArray(data)) return reply_(true);
    if (data.website) return reply_(true);                         // 허니팟 칸이 채워짐 → 봇

    const lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      if (!takeQuota_('rows', LIMIT_ROWS_PER_DAY)) return reply_(true);
      if (data.type === 'brochure') handleBrochure(data, false);
      else if (data.type === 'intake') handleIntake(data);
      else handleConsult(data);                                    // 상담 · 결제 페이지 주문(kind: order) · payment
    } finally {
      lock.releaseLock();
    }
    return reply_(true);
  } catch (err) {
    console.error(err);
    return reply_(false);
  }
}

// -------------------- 상담 신청 · 주문 접수 --------------------
function handleConsult(data) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONSULT_SHEET);
  if (!sheet) throw new Error('Sheet not found: ' + CONSULT_SHEET);

  sheet.appendRow([
    cell_(data.timestamp || new Date().toISOString(), 40),
    cell_(data.name, 60),
    cell_(data.phone, 40),
    cell_(data.email, 254),
    cell_(data.industry, 200),
    cell_(data.reference, 200),
    cell_(data.message, 5000),
    cell_(data.referrer, 500),
  ]);

  const what = data.kind === 'order' ? '새 주문 접수' : data.type === 'payment' ? '결제 확인 필요' : '새 상담 신청';
  const headline = data.kind === 'order' ? '새 주문이 접수되었습니다.' : data.type === 'payment' ? '결제 확인이 필요한 주문이 있습니다.' : '새 상담 신청이 도착했습니다.';
  notify_({
    subject: `[NOAH] ${what} — ${line_(data.name, 30) || '(이름 없음)'}`,
    replyTo: email_(data.email),
    htmlBody: `
      <div style="font-family:-apple-system,sans-serif;line-height:1.6;">
        <h3>${headline}</h3>
        <p><strong>성함</strong>: ${html_(data.name, 60)}<br/>
        <strong>연락처</strong>: ${html_(data.phone, 40)}<br/>
        <strong>이메일</strong>: ${html_(data.email, 254) || '미기입'}<br/>
        <strong>업종</strong>: ${html_(data.industry, 200)}<br/>
        <strong>관심 디자인</strong>: ${html_(data.reference || data.design_pick, 200) || '미정'}<br/>
        <strong>문의</strong>: ${html_(data.message, 5000).replace(/\n/g, '<br/>') || '없음'}</p>
        <p style="color:#888;font-size:12px;">시간: ${html_(data.timestamp, 40)} · 유입: ${html_(data.referrer, 300) || '직접'}</p>
      </div>`,
  });

  // 상담 신청자에게 접수 안내 + 소개서 링크 (사이트가 sendBrochure: true를 보내고 이메일이 있을 때만)
  if (data.sendBrochure === true && data.email) {
    handleBrochure({
      timestamp: data.timestamp, name: data.name, email: data.email,
      phone: data.phone, industry: data.industry, referrer: '상담 신청 폼에서 자동 발송',
    }, true);
  }
}

// -------------------- 소개서 신청 (PDF 첨부 없음) --------------------
// fromConsult는 서버 안에서만 정합니다 (요청에 실린 값은 쓰지 않음)
function handleBrochure(data, fromConsult) {
  // 1) 시트 기록 (상담에서 넘어온 경우는 상담 시트에 이미 기록됨)
  if (!fromConsult) {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(BROCHURE_SHEET);
    if (!sheet) throw new Error('Sheet not found: ' + BROCHURE_SHEET);
    sheet.appendRow([
      cell_(data.timestamp || new Date().toISOString(), 40),
      cell_(data.name, 60),
      cell_(data.email, 254),
      cell_(data.phone, 40),
      cell_(data.industry, 200),
      cell_(data.referrer, 500),
    ]);
  }

  // 2) 신청자에게 소개서 안내 메일
  const subject = fromConsult
    ? '[NOAH] 상담 신청이 접수되었습니다 — 소개서 함께 보내드려요'
    : '[NOAH] 소개서 다운로드 안내';
  const leadLine = fromConsult
    ? '방금 보내주신 상담 신청은 잘 접수되었습니다. 영업일 기준 1일 안에 회신드릴게요.<br/>회신 전에 천천히 살펴보실 수 있도록 소개서를 함께 보내드립니다.'
    : '방금 신청하신 NOAH 소개서는 사이트에서 자동 다운로드가 시작되었을 거예요.<br/>혹시 다운로드가 안 되셨다면 아래 버튼으로 다시 받으실 수 있습니다.';
  sendToApplicant_(data.email, {
    subject: subject,
    htmlBody: `
      <div style="font-family:-apple-system,'Apple SD Gothic Neo',sans-serif; max-width:560px; padding:24px; color:#222;">
        <h2 style="font-size:26px; margin:0 0 16px;">NOAH 소개서</h2>
        <p style="font-size:15px;">${html_(greetName_(data.name, '고객'))}님 안녕하세요,</p>
        <p style="font-size:15px;">${leadLine}</p>
        <p style="margin:24px 0;">
          <a href="${SITE_URL}/assets/brochure/NOAH-brochure.pdf"
             style="display:inline-block; padding:14px 28px; background:#0a0a0b; color:#fff; border-radius:9999px; text-decoration:none; font-weight:500;">
            📄 소개서 다운로드
          </a>
        </p>
        <p style="font-size:15px;">레퍼런스 디자인, 7일 제작 과정, 패키지와 옵션 가격을 한 권에 담았습니다.<br/>
        궁금하신 점은 이 메일에 그대로 답장 주시거나 전화로 편하게 연락 주세요.</p>
        <hr style="border:0; border-top:1px solid #eee; margin:24px 0;" />
        <p style="font-size:13px; color:#666;">
          <strong style="color:#222;">NOAH · 노아홈페이지</strong><br/>
          ${CONTACT_LINE}<br/>
          <a href="${SITE_URL}" style="color:#7c5cff;">${SITE_URL}</a>
        </p>
      </div>`,
  });

  // 3) 운영자 알림 (상담에서 넘어온 경우는 상담 알림이 이미 감)
  if (!fromConsult) {
    notify_({
      subject: `[NOAH] 새 소개서 다운로드 — ${line_(data.name, 30) || '(이름 없음)'}`,
      body: `이름: ${line_(data.name, 60)}\n이메일: ${line_(data.email, 254)}\n연락처: ${line_(data.phone, 40) || '미기입'}\n업종: ${line_(data.industry, 200) || '미기입'}\n유입: ${line_(data.referrer, 300) || '직접'}\n시간: ${line_(data.timestamp, 40)}\n\n→ 사용자는 사이트에서 PDF를 직접 다운로드했습니다.`,
    });
  }
}

// -------------------- 사전 정보 시트(intake) --------------------
// 운영자에게 전체 항목 메일 + (선택) 고객 확인 메일. 아래 목록에 없는 칸은 기록하지 않습니다.
function handleIntake(data) {
  const groups = [
    ['A · 사장님과 가게', [
      ['A_상호_한글', '상호(한글)'], ['A_상호_영문', '상호(영문)'],
      ['A_도메인', '도메인'], ['A_도메인_주소', '도메인 주소'],
      ['A_업종설명', '업종 한 줄'], ['A_주소', '사업장 주소'],
      ['A_사업자번호', '사업자등록번호'], ['A_통신판매업', '통신판매업'],
      ['A_대표자', '대표자'],
    ]],
    ['B · 연락드릴 길', [
      ['B_전화', '대표 전화'], ['B_이메일', '추가 이메일'],
      ['B_영업시간', '영업시간'], ['B_카카오', '카카오 채널'],
      ['B_블로그', '네이버 블로그'], ['B_인스타', '인스타그램'],
      ['B_톡톡', '네이버 톡톡'], ['B_기타채널', '기타 채널'],
    ]],
    ['C · 디자인 선택', [
      ['C_1순위', '1순위'], ['C_2순위', '2순위'],
      ['C_이유', '마음에 든 이유'], ['C_다른점', '내 가게와 다른 점'],
    ]],
    ['D · 사장님 브랜드', [
      ['D_톤', '브랜드 톤'], ['D_메인컬러', '메인 컬러'], ['D_보조컬러', '보조 컬러'],
      ['D_로고', '로고'], ['D_파비콘', '파비콘'], ['D_슬로건', '슬로건'], ['D_금지표현', '금지 표현'],
    ]],
    ['E · 페이지 이야기', [
      ['E_소개', '가게 소개'], ['E_서비스', '핵심 서비스/메뉴'], ['E_가격정책', '가격 표기'],
      ['E_숫자', '자랑할 숫자'], ['E_FAQ', '자주 받는 질문'], ['E_후기', '고객 후기'],
      ['E_사진', '사진 자료'], ['E_영상', '영상 자료'], ['E_레퍼런스', '레퍼런스 사이트'],
    ]],
    ['F · 추가 옵션', [
      ['F_디자인', '디자인·콘텐츠'], ['F_기능', '기능'], ['F_운영', '운영·마케팅'],
    ]],
    ['G · 오픈 후 운영', [
      ['G_업데이트주체', '업데이트 주체'], ['G_빈도', '빈도'], ['G_자주바꿀것', '자주 바꿀 것'],
      ['G_검색등록', '검색엔진 등록'], ['G_GA4', 'GA4'], ['G_인계', '인계 방식'],
    ]],
    ['H · 첨부(보유 자료 체크)', [
      ['H_자료', '보유 자료'],
    ]],
  ];

  const storeName = line_(data['A_상호_한글'], 60) || '(상호 미기입)';
  const clientEmail = email_(data.respondent_email) || email_(data['B_이메일']) || email_(data.email);

  // 0) 시트에 한 줄 기록 (탭이 없으면 만들고 헤더까지)
  const ORDER = [];
  for (const [, fields] of groups) for (const [key] of fields) ORDER.push(key);
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(INTAKE_SHEET);
  if (!sheet) {
    sheet = ss.insertSheet(INTAKE_SHEET);
    sheet.appendRow(['timestamp', '회신이메일', '상호', ...ORDER, 'referrer']);
  }
  sheet.appendRow([
    cell_(data.timestamp || new Date().toISOString(), 40),
    cell_(clientEmail, 254), cell_(storeName, 60),
    ...ORDER.map((k) => cell_(data[k], 3000)),
    cell_(data.referrer, 500),
  ]);

  // 1) 운영자 알림 (작성된 항목만 섹션별 표로)
  let body = `<div style="font-family:-apple-system,'Apple SD Gothic Neo',sans-serif;line-height:1.7;max-width:640px;color:#222;">`;
  body += `<h2 style="margin:0 0 4px;">📋 새 사전 정보 시트 — ${html_(storeName)}</h2>`;
  body += `<p style="color:#888;font-size:13px;margin:0 0 20px;">회신 이메일: ${html_(clientEmail) || '미기입'} · 접수: ${html_(data.timestamp, 40)} · 유입: ${html_(data.referrer, 300) || '직접'}</p>`;
  for (const [sectionTitle, fields] of groups) {
    const rows = fields
      .filter(([key]) => text_(data[key], 3000).trim() !== '')
      .map(([key, label]) =>
        `<tr><td style="padding:6px 12px 6px 0;color:#666;vertical-align:top;white-space:nowrap;">${label}</td>` +
        `<td style="padding:6px 0;color:#111;">${html_(data[key], 3000).replace(/\n/g, '<br/>')}</td></tr>`
      );
    if (rows.length === 0) continue;
    body += `<h3 style="margin:18px 0 6px;padding-bottom:6px;border-bottom:1px solid #eee;font-size:15px;">${sectionTitle}</h3>`;
    body += `<table style="border-collapse:collapse;font-size:14px;width:100%;">${rows.join('')}</table>`;
  }
  body += `</div>`;
  notify_({ subject: `[NOAH] 사전 정보 시트 — ${line_(storeName, 30)}`, htmlBody: body, replyTo: clientEmail });

  // 2) 고객 확인 메일 (선택)
  const storeGreet = greetName_(data['A_상호_한글'], '');
  sendToApplicant_(clientEmail, {
    subject: '[NOAH] 사전 정보 시트가 접수되었습니다',
    htmlBody: `
      <div style="font-family:-apple-system,'Apple SD Gothic Neo',sans-serif;max-width:560px;padding:24px;color:#222;line-height:1.7;">
        <h2 style="font-size:26px;margin:0 0 16px;">NOAH</h2>
        <p style="font-size:15px;">${storeGreet ? html_(storeGreet) + ' ' : ''}사장님, 사전 정보 시트가 잘 접수되었습니다.</p>
        <p style="font-size:15px;">영업일 기준 1일 안에 검토 회신을 드린 뒤, Day 1 상담 일정을 잡아드릴게요.<br/>
        추가로 보내주실 파일(로고·사진·사업자등록증 등)은 이 메일에 그대로 답장해 첨부해주시면 됩니다.</p>
        <hr style="border:0;border-top:1px solid #eee;margin:24px 0;" />
        <p style="font-size:13px;color:#666;">
          <strong style="color:#222;">NOAH · 노아홈페이지</strong><br/>
          ${CONTACT_LINE}<br/>
          <a href="${SITE_URL}" style="color:#7c5cff;">${SITE_URL}</a>
        </p>
      </div>`,
  });
}

// -------------------- 메일 보내기 (한도 확인) --------------------
function notify_(opts) {
  if (!takeQuota_('notify', LIMIT_NOTIFY_PER_DAY) || MailApp.getRemainingDailyQuota() < 1) {
    console.warn('운영자 알림 한도 초과 — 시트에만 기록: ' + opts.subject);
    return;
  }
  const mail = { to: NOTIFY_EMAIL, subject: opts.subject };
  if (opts.htmlBody) mail.htmlBody = opts.htmlBody;
  if (opts.body) mail.body = opts.body;
  if (opts.replyTo) mail.replyTo = opts.replyTo;
  MailApp.sendEmail(mail);
}

function sendToApplicant_(address, opts) {
  const to = email_(address);
  if (!SEND_USER_EMAIL || !to) return;
  if (MailApp.getRemainingDailyQuota() <= KEEP_QUOTA_FOR_NOTIFY) return;   // 운영자 알림 몫은 남겨 둠
  if (!cooldownOk_(to)) return;                                          // 같은 주소로 연달아 보내지 않음
  if (!takeQuota_('user', LIMIT_USER_MAIL_PER_DAY)) return;
  const mail = { to: to, subject: opts.subject, htmlBody: opts.htmlBody, name: 'NOAH' };
  if (opts.attachments) mail.attachments = opts.attachments;   // (선택) PDF 첨부 모드에서 사용
  MailApp.sendEmail(mail);
}

// 오늘(한국 시간) 카운터가 한도 안이면 1 올리고 true
function takeQuota_(kind, limit) {
  const day = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyyMMdd');
  const props = PropertiesService.getScriptProperties();
  const key = 'q_' + kind + '_' + day;
  const current = props.getProperty(key);
  if (current === null) {   // 그날 첫 요청이면 지난 날짜 카운터 정리
    const all = props.getProperties();
    Object.keys(all).forEach((k) => { if (k.indexOf('q_' + kind + '_') === 0 && k !== key) props.deleteProperty(k); });
  }
  const n = Number(current || 0);
  if (n >= limit) return false;
  props.setProperty(key, String(n + 1));
  return true;
}

function cooldownOk_(address) {
  const cache = CacheService.getScriptCache();
  const key = 'cd_' + address.toLowerCase().slice(0, 200);
  if (cache.get(key)) return false;
  cache.put(key, '1', SAME_ADDRESS_COOLDOWN_SEC);
  return true;
}

// -------------------- 입력값 다듬기 --------------------
function text_(v, max) {                       // 문자열로 바꾸고 길이 자르기
  if (v === null || v === undefined) return '';
  if (typeof v === 'object') v = JSON.stringify(v);
  return String(v).slice(0, max || 500);
}
function line_(v, max) {                       // 한 줄로 (메일 제목·일반 텍스트용)
  return text_(v, max).replace(/[\r\n\t]+/g, ' ').trim();
}
function html_(v, max) {                       // 메일 HTML에 넣을 때
  return text_(v, max)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
function cell_(v, max) {                       // 시트에 넣을 때: 수식으로 실행되지 않게
  const t = text_(v, max || 5000);
  return /^[=+\-@\t\r]/.test(t) ? "'" + t : t;
}
function email_(v) {                           // 이메일 형식일 때만 돌려줌
  const t = line_(v, 254);
  return /^[^\s@<>()\[\]",;:\\]+@[^\s@<>()\[\]",;:\\]+\.[A-Za-z]{2,}$/.test(t) ? t : '';
}
function greetName_(v, fallback) {             // 신청자 메일 인사말: 짧게, 링크처럼 보이면 fallback
  const t = line_(v, 20);
  if (!t || /(https?:|\/\/|www\.|@|[a-z0-9-]+\.(com|net|org|kr|io|co|me|xyz|top|ly|link|site|shop|info|biz|app)\b)/i.test(t)) return fallback;
  return t;
}
function reply_(ok) {
  return ContentService.createTextOutput(JSON.stringify({ ok: ok }))
    .setMimeType(ContentService.MimeType.JSON);
}

// -------------------- 테스트 함수 (▶ 실행으로 확인) --------------------
function testIntake() {
  handleIntake({
    type: 'intake',
    respondent_email: 'YOUR_EMAIL@gmail.com', // ← 본인 이메일로 변경
    A_상호_한글: '테스트 상호', A_업종설명: '강남 1층 치과', A_주소: '서울시 강남구 ...',
    A_도메인: '신규 구매 필요',
    B_전화: '010-0000-0000', B_이메일: 'test@example.com', B_영업시간: '평일 10-19시',
    C_1순위: '01 DENTAL — 라온치과의원', C_이유: '여백이 좋아서',
    D_톤: '정중함, 단정함', E_소개: '동네에서 가장 친절한 치과입니다.',
    F_운영: '유지보수 1년 (200,000원)',
    timestamp: new Date().toISOString(), referrer: '테스트',
  });
}
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
    phone: '010-0000-0000', industry: '카페·베이커리', referrer: '테스트',
  }, false);
}
// 보안 확인용: 아래를 실행하면 메일 본문에 <b> 태그가 글자 그대로 보이고, 시트에는 '=1+1 이 글자로 들어가야 정상
function testSecurity() {
  handleConsult({
    timestamp: new Date().toISOString(),
    name: '<b>굵게</b> 테스트', phone: '=1+1', email: 'not-an-email',
    industry: '<a href="https://example.com">링크</a>', message: '줄1\n줄2', referrer: '테스트',
  });
}
```

3. 코드 상단의 설정 네 줄을 본인 값으로 수정:
   - `NOTIFY_EMAIL` — 운영자 알림을 받을 메일
   - `SITE_URL` — 사이트 주소 (예: `https://noahhomepage.co.kr`)
   - `SEND_USER_EMAIL` — 신청자 확인 메일 보낼지 여부
   - `CONTACT_LINE` — 메일 맨 아래 서명 (전화 · 이메일)
4. **저장 (Ctrl+S)**, 프로젝트 이름은 `NOAH 통합 폼`

---

## 3단계 — 권한 부여 (1회)

1. `testBrochure` 함수 안의 `YOUR_EMAIL@gmail.com`을 본인 이메일로 변경 후 저장
2. 상단 함수 드롭다운에서 **`testBrochure`** 선택
3. **▶ 실행** 클릭 → 권한 검토 → 본인 계정 선택 → "고급" → "안전하지 않음" → 허용
4. 본인 이메일 받은편지함 확인 — `[NOAH] 소개서 다운로드 안내` 메일이 도착하면 ✅

---

## 4단계 — Web App 배포

1. 우측 상단 **배포 → 새 배포**
2. ⚙️ → **웹 앱**
3. 설정:
   - 설명: `NOAH 통합 폼 v1`
   - 다음 사용자로 실행: **나**
   - 액세스 권한: **모든 사용자** ⚠️ 꼭!
4. **배포** → **웹 앱 URL 복사** (`https://script.google.com/macros/s/.../exec`)

---

## 5단계 — 홈페이지에 URL 붙여넣기

**네 파일** 모두에서 다음 줄을 찾아 교체합니다 (보통은 할 일 없음 — 위 6번처럼 기존 배포를 편집하면 주소가 그대로입니다):

- `assets/js/site.js` (모든 페이지의 소개서 받기 모달)
- `contact.html` (상담 신청 폼)
- `intake.html` (사전 정보 시트)
- `checkout.html` (결제 페이지 주문 접수)

```javascript
const GAS_URL = 'https://script.google.com/macros/s/PASTE_YOUR_DEPLOYMENT_ID/exec';
```

위에서 복사한 URL로 교체. (네 파일이 같은 배포 URL을 공유합니다.)

---

## 6단계 — 테스트

### A. 헤더 「소개서 받기」 버튼 (단순 다운로드 흐름)

1. 배포된 사이트 우상단 **"소개서 받기"** 버튼 클릭
2. 본인 이메일 입력 후 제출
3. **즉시** 브라우저에서 PDF 다운로드 시작 ✓
4. 1~5분 안에 `[NOAH] 소개서 다운로드 안내` 메일 수신 ✓ (백업 링크 포함)
5. 시트 `NOAH 소개서` 탭에 행 추가 확인 ✓
6. 운영자 알림 메일 수신 확인 ✓

### B. 하단 「상담 신청 보내기」 (상담 + 소개서 자동 발송 결합)

1. `#consult` 섹션에서 이름·연락처·이메일·업종 입력 후 **상담 신청 보내기** 클릭
2. **즉시** 브라우저에서 PDF 다운로드 시작 ✓
3. 1~5분 안에 `[NOAH] 상담 신청이 접수되었습니다 — 소개서 함께 보내드려요` 메일 수신 ✓
4. 시트 `NOAH 상담` 탭에 행 추가 확인 ✓ (소개서 탭에는 중복 기록 안 됨)
5. 운영자 알림 `[NOAH] 새 상담 신청` 메일 1통 수신 ✓ (소개서 알림은 중복 발송 안 됨)

### C. 사전 정보 시트 (`/intake.html`)

1. `testIntake` 함수의 `YOUR_EMAIL@gmail.com`을 본인 이메일로 바꾸고 ▶ 실행 → 전체 항목이 표로 정리된 메일 수신 확인 ✓
2. 실제 페이지(`https://<도메인>/intake.html` 또는 단축 `/intake`)에서 폼 작성 후 제출
3. `NOAH 사전정보` 탭이 자동 생성되고 한 줄 기록됨 ✓ (헤더 포함)
4. 운영자에게 `[NOAH] 사전 정보 시트 — {상호}` 메일 수신 ✓ (섹션 A~H 중 작성된 항목만 표시)
5. 고객에게 `[NOAH] 사전 정보 시트가 접수되었습니다` 확인 메일 수신 ✓
6. 운영자가 메일에서 **답장**하면 고객 이메일로 바로 회신됨 (replyTo 설정)

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
- 한도가 부담스러우면 `SEND_USER_EMAIL = false`로 두고 운영자 알림만 받기

### 신청자에게 메일이 안 가요
- `SEND_USER_EMAIL`이 `true`인지 확인
- 받는 사람 메일 주소 오타 확인
- Apps Script **실행 로그** 확인 (좌측 ⌚ 아이콘)

### 스팸으로 분류돼요
- Gmail로 발송하므로 대부분 정상 인박스 도착
- 첫 발송 시 받는 사람이 "스팸 아님" 표시 한 번 해두면 이후 안전
- 도메인 평판이 우려되면 **운영자 알림만** 유지하고 신청자 메일은 끄기

### PDF 다운로드가 안 됩니다
- Apps Script 문제가 아닙니다. `/assets/brochure/NOAH-brochure.pdf`가 실제 리포지토리에 업로드되었는지 확인하세요.
- Cloudflare Pages 배포가 완료되었는지 확인 (`https://<도메인>/assets/brochure/NOAH-brochure.pdf` 직접 접속 테스트).

---

## 🎁 (선택) PDF 메일 첨부 모드로 전환

리포지토리 호스팅이 어려운 환경이거나 메일에 PDF를 첨부하고 싶다면 아래처럼 `handleBrochure`를 교체할 수 있습니다.

<details>
<summary>PDF 첨부 버전 코드 펼치기</summary>

### 추가 사전 작업

1. https://drive.google.com 접속 → `NOAH-brochure.pdf` 업로드
2. 업로드한 파일 URL에서 **파일 ID** 추출:
   ```
   https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUv_FILE_ID/view
                                   ↑ 이 부분이 파일 ID
   ```

### 코드 상단 상수 추가

```javascript
const BROCHURE_FILE_ID = 'PASTE_YOUR_FILE_ID'; // 위에서 메모한 파일 ID
```

### `handleBrochure` 안의 `sendToApplicant_(data.email, { ... })` 부분에 첨부 한 줄 추가

```javascript
sendToApplicant_(data.email, {
  subject: '[NOAH] 요청하신 소개서를 첨부해 드립니다',
  htmlBody: `<!-- 본문은 동일, 다운로드 버튼 대신 첨부 안내 문구 -->`,
  attachments: [DriveApp.getFileById(BROCHURE_FILE_ID).getBlob()],
});
```

### 주의

- 첨부 PDF 최대 25MB
- 첨부 모드에서도 사이트 폼은 **PDF 즉시 다운로드 + 백업 메일** 흐름은 동일하게 작동 (이중 안전망)
- PDF가 바뀌면 Drive에 새 파일 올리고 `BROCHURE_FILE_ID` 갱신 + Apps Script 재배포 필요

</details>

---

## 🎁 더 발전시키기 (참고)

- **PDF 자동 생성**: Google Slides/Docs를 PDF로 변환해 매번 최신 소개서 사용
- **A/B 테스트**: 두 가지 메일 본문을 번갈아 발송 (홀짝 시간으로 분기)
- **신청자 추적**: 다운로드 링크에 신청자별 UTM 파라미터 삽입
- **Slack 알림**: 운영자 메일 대신/병행해 Slack 채널로 알림

이상입니다. 막히는 부분 있으면 알려주세요.
