// The scout. Watches the match (Instagram's own traffic) from the stands and takes notes. Never touches the ball.
// Paste into the DevTools console of https://www.instagram.com/<profile>/ while logged in.
// It does NOT call any Instagram API itself: it only records the JSON the page already loads
// (its own /api/graphql responses and embedded initial data) while scrolling slowly like a person.
// Results accumulate in window.__ig2 (keyed by shortcode) and are snapshotted to localStorage.
// It stops on any non-200 response, or after 4 cooldowns (90 s each) with no new posts.
(() => {
  window.__ig2 = {};
  try { Object.assign(window.__ig2, JSON.parse(localStorage.getItem('__ig2') || '{}')); } catch (e) {}

  const harvest = (o, d = 0) => {
    if (!o || typeof o !== 'object' || d > 14) return;
    if (Array.isArray(o)) { o.forEach(x => harvest(x, d + 1)); return; }
    const ts = o.taken_at ?? o.taken_at_timestamp;
    if (typeof o.code === 'string' && ts) {            // only "full" post nodes carry a timestamp
      const cap = o.caption?.text ?? o.edge_media_to_caption?.edges?.[0]?.node?.text ?? '';
      const p = window.__ig2[o.code] || {};
      window.__ig2[o.code] = {
        code: o.code, ts,
        likes: o.like_count ?? o.edge_media_preview_like?.count ?? p.likes ?? null,
        comments: o.comment_count ?? o.edge_media_to_comment?.count ?? p.comments ?? null,
        type: o.media_type === 2 ? 'video' : o.media_type === 8 ? 'carousel' : o.media_type === 1 ? 'image' : (p.type ?? null),
        caption: cap || p.caption || '',                // never let an empty caption overwrite a real one
        owner: o.user?.username ?? o.owner?.username ?? p.owner ?? null,
      };
    }
    for (const k in o) harvest(o[k], d + 1);
  };

  // embedded initial data (the first posts are not fetched over the network)
  document.querySelectorAll('script[type="application/json"]').forEach(s => { try { harvest(JSON.parse(s.textContent)); } catch (e) {} });

  const f1 = window.fetch;
  window.fetch = async function (...a) {
    const r = await f1.apply(this, a);
    try {
      const u = (a[0]?.url || a[0]) + '';
      if (u.includes('graphql')) { window.__igStatus = r.status; r.clone().json().then(harvest).catch(() => {}); }
    } catch (e) {}
    return r;
  };
  const xo = XMLHttpRequest.prototype.open, xs = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (m, u, ...r) { this.__u = u + ''; return xo.call(this, m, u, ...r); };
  XMLHttpRequest.prototype.send = function (...a) {
    this.addEventListener('load', () => {
      try { if ((this.__u || '').includes('graphql')) { window.__igStatus = this.status; harvest(JSON.parse(this.responseText)); } } catch (e) {}
    });
    return xs.apply(this, a);
  };

  window.__scroll = async (maxMs) => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const cnt = () => Object.keys(window.__ig2).length;
    const t0 = Date.now(); let stop = null, cool = 0;
    while (Date.now() - t0 < maxMs) {
      const before = cnt();
      window.scrollTo(0, document.body.scrollHeight);
      await sleep(6000 + Math.random() * 5000);          // 6-11 s between scrolls
      if (window.__igStatus && window.__igStatus !== 200) { stop = 'status ' + window.__igStatus; break; }
      if (cnt() === before) {
        await sleep(6000);
        if (cnt() === before) {
          if (cool >= 4) { stop = 'no growth after 4 cooldowns'; break; }
          cool++; window.scrollBy(0, -1200); await sleep(90000);
        }
      } else cool = 0;
      if (cnt() % 100 < 12) { try { localStorage.setItem('__ig2', JSON.stringify(window.__ig2)); } catch (e) {} }
    }
    try { localStorage.setItem('__ig2', JSON.stringify(window.__ig2)); } catch (e) {}
    return { stop, n: cnt() };
  };

  window.__scroll(90 * 60 * 1000).then(r => { window.__res = r; console.log('capture finished', r); });
})();
