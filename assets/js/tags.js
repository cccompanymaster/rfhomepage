/* 노아홈페이지 측정 허브 — 광고 픽셀·Clarity는 아래 TAG_IDS에 ID만 넣으면 켜짐 (빈 값 = 꺼짐, 아무것도 불러오지 않음).
   ID를 바꾼 뒤: python3 tools/sync_tags.py → 보안 설정(_headers CSP)·개인정보처리방침 8항·캐시 버전(?v=)이 같이 바뀜.
   (주간 'SEO 측정' 워크플로가 --check 로 확인)
   GA4는 각 페이지 <head>의 gtag가 그대로 담당하고, 페이지의 gtag('event', …) 중 아래 표에 있는 이벤트는
   켜진 광고 도구에도 그 도구의 이벤트 이름으로 같이 보냄. 이름·연락처·문의 내용은 어떤 도구로도 보내지 않음. */
(function () {
  'use strict';
  var TAG_IDS = {
    naver: '', // 네이버 공통키 wa: 검색광고 프리미엄 로그분석 AccountId 또는 네이버 애널리틱스 ID — 둘 중 하나만
    meta: '', // Meta 픽셀 ID
    kakao: '', // 카카오 픽셀 & SDK Track ID
    karrot: '', // 당근 전환 추적 코드 ID
    clarity: 'wrzc98zj2h' // Microsoft Clarity 프로젝트 ID (예전에 태그 관리자 GTM-WZWCZTKJ 안에 있던 것)
  };
  // A public ID enables the choice, never consent. Reload after a choice so
  // third-party scripts from the previous page cannot continue after withdrawal.
  var adConsentKey = 'cc_ad_measure_v1', adChoice = '', adNames = ['naver', 'meta', 'kakao', 'karrot'];
  try { adChoice = localStorage.getItem(adConsentKey) || ''; } catch (_) {}
  var hasAdProvider = adNames.some(function(k) { return Boolean(TAG_IDS[k]); });
  if (adChoice !== 'yes') adNames.forEach(function(k) { TAG_IDS[k] = ''; });
  function showAdChoice() {
    var privacy = /\/privacy(?:\.html|\/)?$/.test(location.pathname);
    if ((!hasAdProvider || adChoice) && !privacy) return;
    if (document.getElementById('cc-ad-choice')) return;
    var panel = document.createElement('section'); panel.id = 'cc-ad-choice';
    panel.setAttribute('aria-label', '선택 광고 측정');
    var p = document.createElement('p');
    p.textContent = !hasAdProvider ? '현재 연결된 선택 광고 픽셀이 없습니다.' : '선택 광고 측정: '+(adChoice === 'yes' ? '허용 중' : '허용 안 함')+'. 거절해도 서비스를 이용할 수 있습니다. 개인정보처리방침에서 언제든 변경할 수 있습니다.';
    panel.appendChild(p);
    if (hasAdProvider) [['yes','광고 측정 허용'],['no','광고 측정 거절']].forEach(function(item) {
      var b = document.createElement('button'); b.type='button'; b.textContent=item[1]; b.disabled=adChoice===item[0];
      b.onclick=function(){ try {localStorage.setItem(adConsentKey,item[0]); location.reload();} catch (_) {p.textContent='선택을 저장하지 못했습니다. 광고 측정은 기본적으로 꺼져 있습니다.';} };
      panel.appendChild(b);
    });
    (document.querySelector('main') || document.body).appendChild(panel);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',showAdChoice,{once:true}); else showAdChoice();

  var CONTACT = { naver: 'custom001', meta: 'Contact' };
  var MAP = {
    generate_lead: { naver: 'lead', meta: 'Lead', kakao: 'participation', karrot: 'Lead' },
    purchase: { naver: 'purchase', meta: 'Purchase', kakao: 'purchase', karrot: 'Purchase' },
    contact_call: CONTACT, contact_kakao: CONTACT, contact_naver_talk: CONTACT
  };

  function load(src, onload) {
    var s = document.createElement('script');
    s.async = true; s.src = src;
    if (onload) s.onload = onload;
    document.head.appendChild(s);
  }
  function safely(run) { try { run(); } catch (e) { /* 태그 오류가 페이지를 멈추면 안 됨 */ } }

  var naverReady = false, naverQueue = [], kakaoQueue = [], karrotQueue = [];
  if (TAG_IDS.naver) load('https://wcs.naver.net/wcslog.js', function () {
    window.wcs_add = window.wcs_add || {};
    window.wcs_add.wa = TAG_IDS.naver;
    if (!window.wcs) return;
    window.wcs.inflow('noahhomepage.co.kr');
    window.wcs_do();
    naverReady = true;
    while (naverQueue.length) window.wcs.trans(naverQueue.shift());
  });
  if (TAG_IDS.meta) {
    var fbq = window.fbq = function () { fbq.callMethod ? fbq.callMethod.apply(fbq, arguments) : fbq.queue.push(arguments); };
    if (!window._fbq) window._fbq = fbq;
    fbq.push = fbq; fbq.loaded = true; fbq.version = '2.0'; fbq.queue = [];
    fbq('init', TAG_IDS.meta);
    fbq('track', 'PageView');
    load('https://connect.facebook.net/en_US/fbevents.js');
  }
  if (TAG_IDS.kakao) load('https://t1.daumcdn.net/kas/static/kp.js', function () {
    if (!window.kakaoPixel) return;
    window.kakaoPixel(TAG_IDS.kakao).pageView();
    while (kakaoQueue.length) kakaoQueue.shift()();
  });
  if (TAG_IDS.karrot) load('https://karrot-pixel.business.daangn.com/0.2/karrot-pixel.umd.js', function () {
    if (!window.karrotPixel) return;
    window.karrotPixel.init(TAG_IDS.karrot);
    window.karrotPixel.track('ViewPage');
    while (karrotQueue.length) karrotQueue.shift()();
  });
  if (TAG_IDS.clarity) {
    window.clarity = window.clarity || function () { (window.clarity.q = window.clarity.q || []).push(arguments); };
    load('https://www.clarity.ms/tag/' + encodeURIComponent(TAG_IDS.clarity));
  }

  function fanOut(name, params) {
    var map = MAP[name];
    params = params || {};
    var value = Number(params.value) || 0;
    if (TAG_IDS.clarity && window.clarity) safely(function () { window.clarity('event', name); });
    if (!map) return;
    if (TAG_IDS.naver && map.naver) {
      var conv = { type: map.naver };
      if (value) conv.value = String(value);
      safely(function () { naverReady ? window.wcs.trans(conv) : naverQueue.push(conv); });
    }
    if (TAG_IDS.meta && map.meta) safely(function () { window.fbq('track', map.meta, value ? { value: value, currency: 'KRW' } : {}); });
    if (TAG_IDS.kakao && map.kakao) {
      var k = function () { var px = window.kakaoPixel(TAG_IDS.kakao); if (map.kakao === 'purchase') px.purchase({ total_price: String(value), currency: 'KRW' }); else px[map.kakao](); };
      safely(function () { window.kakaoPixel ? k() : kakaoQueue.push(k); });
    }
    if (TAG_IDS.karrot && map.karrot) {
      var c = function () { window.karrotPixel.track(map.karrot, map.karrot === 'Purchase' ? { total_price: String(value) } : undefined); };
      safely(function () { window.karrotPixel ? c() : karrotQueue.push(c); });
    }
  }

  // 페이지의 gtag('event', 이름, 값)을 감싸서, GA4로 보내는 그대로 광고 도구에도 전달
  var original = window.gtag;
  window.gtag = function () {
    if (typeof original === 'function') original.apply(this, arguments);
    if (arguments[0] === 'event') fanOut(arguments[1], arguments[2]);
  };
  window.noahTrack = function (name, params) { window.gtag('event', name, params || {}); };
})();

