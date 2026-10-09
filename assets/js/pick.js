/* ============================================================
   pick.js — 첫 화면 쇼케이스에서 "이게 좋겠어요!"로 고른 디자인을 이어받기
   - 저장: assets/showcase/intro.js 가 localStorage 'noah_pick' 에 { slug, nameKo, ts } 저장
   - 여기서: 상담 신청서·결제 메모·사전정보 시트에 미리 채우고, 채웠다는 사실을 화면에 표시
   - 개인정보 없음(디자인 이름만), 14일 지나면 무시
   ============================================================ */
(() => {
  const KEY = 'noah_pick';
  const MAX_AGE = 14 * 24 * 60 * 60 * 1000;

  function get() {
    try {
      const p = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (!p || !p.slug || !p.nameKo) return null;
      if (Date.now() - (p.ts || 0) > MAX_AGE) { localStorage.removeItem(KEY); return null; }
      return p;
    } catch (_) { return null; }
  }
  function clear() { try { localStorage.removeItem(KEY); } catch (_) {} }

  const pick = get();
  window.NOAH_PICK = { get, clear, current: pick };
  if (!pick) return;

  // "첫 화면에서 고르신 디자인" 안내 — 선택 칸 바로 아래
  function note(afterEl, text) {
    if (!afterEl || afterEl.parentElement.querySelector('.pick-note')) return;
    const p = document.createElement('p');
    p.className = 'pick-note';
    p.style.cssText = 'margin-top:8px;font-size:13px;line-height:1.6;color:var(--text-dim,#56606F)';
    p.innerHTML = `<span style="display:inline-block;padding:2px 8px;border-radius:999px;background:var(--accent-soft,#FFF1EC);color:var(--accent-deep,#E8431A);font-weight:700;margin-right:6px">✓</span>첫 화면에서 고르신 <strong style="color:var(--text,#111821)"></strong> ${text} `;
    p.querySelector('strong').textContent = pick.nameKo;
    const undo = document.createElement('button');
    undo.type = 'button';
    undo.textContent = '선택 해제';
    undo.style.cssText = 'font:inherit;font-size:12.5px;text-decoration:underline;text-underline-offset:3px;color:var(--text-quiet,#8C94A2);background:none;border:0;padding:0;cursor:pointer';
    undo.addEventListener('click', () => {
      clear();
      if (afterEl.tagName === 'SELECT') afterEl.selectedIndex = 0;
      if (afterEl.tagName === 'INPUT' || afterEl.tagName === 'TEXTAREA') {
        if (afterEl.value === afterEl.dataset.pickText) afterEl.value = '';
      }
      afterEl.dispatchEvent(new Event('change', { bubbles: true }));
      p.remove();
    });
    p.appendChild(undo);
    afterEl.insertAdjacentElement('afterend', p);
  }

  function selectBySlug(select) {
    if (!select) return false;
    const opt = select.querySelector(`option[data-slug="${CSS.escape(pick.slug)}"]`);
    if (!opt) return false;
    if (select.value && select.value !== opt.value) return false;   // 이미 직접 고른 값은 존중
    select.value = opt.value;
    return true;
  }

  function run() {
    // 상담 신청서 (/contact): "관심 있는 디자인"
    const ref = document.querySelector('#consult-form select[name="reference"]');
    if (selectBySlug(ref)) note(ref, '디자인을 미리 넣어 두었어요.');

    // 사전정보 시트 (/intake): "1순위 디자인"
    const first = document.querySelector('select[name="C_1순위"]');
    if (selectBySlug(first)) note(first, '디자인을 1순위로 넣어 두었어요.');

    // 결제 (/checkout): 요청 메모
    const memo = document.getElementById('b-memo');
    if (memo && !memo.value.trim()) {
      memo.value = `희망 디자인: ${pick.nameKo}`;
      memo.dataset.pickText = memo.value;
      memo.dispatchEvent(new Event('input', { bubbles: true }));
      note(memo, '디자인을 메모에 넣어 두었어요.');
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
})();
