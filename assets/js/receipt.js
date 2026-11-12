// Keep only a fingerprint and a random key for the most recent submission.
// Reusing a key lets the backend return the saved row after a lost response.
window.noahReceipt = async function (endpoint, payload) {
  const fields = Object.keys(payload).filter(key => !['timestamp', 'referrer', 'page', 'orderId'].includes(key)).sort();
  const bytes = new TextEncoder().encode(JSON.stringify(fields.map(key => [key, payload[key]])));
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), b => b.toString(16).padStart(2, '0')).join('');
  const key = 'noah_receipt_' + (payload.kind || payload.type);
  const memory = window.noahReceipt.pending ||= {};
  let pending = memory[key];
  try { pending ||= JSON.parse(sessionStorage.getItem(key)); } catch (_) {}
  if (!pending || pending.hash !== hash) pending = { hash, id: crypto.randomUUID() };
  memory[key] = pending;
  try { sessionStorage.setItem(key, JSON.stringify(pending)); } catch (_) {}
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);
  try {
    const response = await fetch(endpoint, {
      method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify({ ...payload, requestId: pending.id }), signal: controller.signal,
    });
    if (!response.ok) throw new Error('unconfirmed');
    const result = await response.json();
    if (result.ok !== true || result.receiptId !== pending.id) throw new Error('unconfirmed');
    return result;
  } finally { clearTimeout(timer); }
};
