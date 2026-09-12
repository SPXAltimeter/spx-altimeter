/**
 * SPX Altimeter — Telegram bot as a Cloudflare Worker.
 *
 * Free-tier only: Workers (100k req/day free), KV (100k reads + 1k writes/day
 * free), Telegram Bot API (no message-count limit, unlike LINE). No server,
 * no cost at the volumes this project is likely to see.
 *
 * Commands:
 *   /start        welcome + what this is
 *   /now          on-demand altitude reading (works for anyone, no state)
 *   /subscribe    opt in to one identical daily message (stored in KV)
 *   /unsubscribe  opt out
 *   /help         command list
 *
 * Design choices that matter for the "is this investment advice" question
 * (see DEPLOY.md for the fuller reasoning):
 *   - /now and the daily push send the SAME computed message to everyone.
 *     There is no per-user threshold, no personalized recommendation, and
 *     no evaluative language ("warning", "buy", "sell") anywhere in the
 *     reply text — only the numbers and a link to the methodology.
 *   - Subscribing costs nothing and requires no payment info, so there is
 *     no "advice for compensation" to speak of.
 *   - The bot never *pushes* /now data proactively except via /subscribe,
 *     and that push is identical for every subscriber.
 *
 * Bindings this Worker expects (set in the Cloudflare dashboard, see
 * DEPLOY.md):
 *   env.BOT_TOKEN        secret  — from @BotFather
 *   env.WEBHOOK_SECRET   secret  — random string, checked against the
 *                                  X-Telegram-Bot-Api-Secret-Token header
 *   env.DATA_URL         var     — e.g. https://you.github.io/spx-altimeter/data/latest.json
 *   env.SUBSCRIBERS      KV namespace binding
 */

const TG = (env) => `https://api.telegram.org/bot${env.BOT_TOKEN}`;

async function sendMessage(env, chatId, text, extra = {}) {
  const r = await fetch(`${TG(env)}/sendMessage`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      parse_mode: "HTML",
      disable_web_page_preview: true,
      ...extra,
    }),
  });
  if (!r.ok) console.log("sendMessage failed", r.status, await r.text());
  return r;
}

async function fetchLatest(env) {
  const r = await fetch(env.DATA_URL, { cf: { cacheTtl: 0 } });
  if (!r.ok) throw new Error(`data fetch HTTP ${r.status}`);
  return r.json();
}

function fmt(v) {
  return v >= 1000 ? Math.round(v).toLocaleString("en-US") : v.toFixed(2);
}

/** The one message shape used by both /now and the daily push. Deliberately
 * flat and factual — no "buy/sell/warning" language, same text for everyone. */
function renderReading(d) {
  const rest = (100 - d.alt_c).toFixed(1);
  const lines = [
    `<b>SPX Altimeter</b> — ${d.date}`,
    ``,
    `Altitude: <b>${d.alt_c.toFixed(1)}%</b>  (this month's high: ${d.alt_h.toFixed(1)}%)`,
    `${rest} points to the 100% ceiling`,
    `S&amp;P 500 close: ${fmt(d.close)}`,
    ``,
    `0% floor:    ${fmt(d.levels["0"])}`,
    `50% mid:     ${fmt(d.levels["50"])}`,
    `100% ceiling: ${fmt(d.levels["100"])}`,
    ``,
    `This is a description of where the price sits in a historical channel,
not a trading signal — 30 backtested rules using this indicator all failed
to beat buy-and-hold. Full writeup: see the site below.`,
  ];
  return lines.join("\n");
}

const HELP = [
  "<b>SPX Altimeter bot</b>",
  "",
  "/now — current reading, on demand",
  "/subscribe — get this same reading once a day",
  "/unsubscribe — stop the daily message",
  "/help — this message",
].join("\n");

async function handleUpdate(update, env) {
  const msg = update.message;
  if (!msg || !msg.text) return;
  const chatId = msg.chat.id;
  const text = msg.text.trim();

  if (text === "/start" || text === "/help") {
    await sendMessage(env, chatId, HELP);
    return;
  }

  if (text === "/now") {
    try {
      const d = await fetchLatest(env);
      await sendMessage(env, chatId, renderReading(d));
    } catch (e) {
      await sendMessage(env, chatId, `Couldn't fetch live data right now (${e.message}). Try again shortly.`);
    }
    return;
  }

  if (text === "/subscribe") {
    await env.SUBSCRIBERS.put(`chat:${chatId}`, "1");
    await sendMessage(env, chatId, "Subscribed. You'll get one message a day after the data updates (~06:30 JST / 21:30 UTC). Send /unsubscribe any time.");
    return;
  }

  if (text === "/unsubscribe") {
    await env.SUBSCRIBERS.delete(`chat:${chatId}`);
    await sendMessage(env, chatId, "Unsubscribed. Send /subscribe to turn it back on.");
    return;
  }

  await sendMessage(env, chatId, "Not sure what that means. " + HELP);
}

/** Fan out the identical daily message to every subscriber. Cloudflare KV's
 * free tier caps writes at 1,000/day but list+get+send has no such cap on
 * reads at this volume, so this scales to several thousand subscribers
 * before you'd need to page through list() cursors (already handled below)
 * or upgrade off the free tier. */
async function sendDaily(env) {
  const d = await fetchLatest(env);
  const text = renderReading(d);
  let cursor;
  let sent = 0;
  do {
    const page = await env.SUBSCRIBERS.list({ prefix: "chat:", cursor });
    for (const key of page.keys) {
      const chatId = key.name.slice("chat:".length);
      try {
        await sendMessage(env, chatId, text);
        sent++;
      } catch (e) {
        console.log("daily send failed for", chatId, e.message);
      }
    }
    cursor = page.cursor;
  } while (cursor);
  console.log(`daily push: sent to ${sent} subscribers`);
}

/** Analytics Engine is write-only from inside a Worker (writeDataPoint()).
 * Reading it back requires calling OUT to the separate SQL HTTP API with a
 * Cloudflare API token that has "Account Analytics Engine: Read" — hence
 * env.CF_ACCOUNT_ID / env.CF_API_TOKEN, distinct from the write-side binding
 * env.PAGEVIEWS. See DEPLOY.md for how those two are set up. */
async function aeSql(env, query) {
  const r = await fetch(
    `https://api.cloudflare.com/client/v4/accounts/${env.CF_ACCOUNT_ID}/analytics_engine/sql`,
    { method: "POST", headers: { Authorization: `Bearer ${env.CF_API_TOKEN}` }, body: query }
  );
  const j = await r.json();
  if (!r.ok) throw new Error("AE SQL " + r.status + ": " + JSON.stringify(j).slice(0, 300));
  return j.data || [];
}

function escHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

async function renderAnalytics(env) {
  const DS = "spx_pageviews"; // must match the dataset name bound as PAGEVIEWS
  const [byPath, byDay, byRef, byCountry] = await Promise.all([
    aeSql(env, `SELECT blob1 AS path, count() AS n FROM ${DS} WHERE timestamp > NOW() - INTERVAL '30' DAY GROUP BY path ORDER BY n DESC`),
    aeSql(env, `SELECT toDate(timestamp) AS day, count() AS n FROM ${DS} WHERE timestamp > NOW() - INTERVAL '14' DAY GROUP BY day ORDER BY day DESC`),
    aeSql(env, `SELECT blob3 AS ref, count() AS n FROM ${DS} WHERE timestamp > NOW() - INTERVAL '30' DAY GROUP BY ref ORDER BY n DESC LIMIT 10`),
    aeSql(env, `SELECT blob2 AS country, count() AS n FROM ${DS} WHERE timestamp > NOW() - INTERVAL '30' DAY GROUP BY country ORDER BY n DESC LIMIT 10`),
  ]);
  const rows = (arr, cols) => arr.length
    ? arr.map((r) => `<tr>${cols.map((c) => `<td>${escHtml(r[c])}</td>`).join("")}</tr>`).join("")
    : `<tr><td colspan="${cols.length}" class="mut">no data yet</td></tr>`;
  const html = `<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SPX Altimeter — Analytics</title>
<style>
body{font:14px -apple-system,system-ui,sans-serif;background:#0d1014;color:#e9edf2;
margin:0;padding:32px;max-width:720px}
h1{font-size:19px;margin:0 0 4px}
.mut{color:#79838e;font-size:12.5px;margin:0 0 32px}
h2{font-size:14px;color:#a6b0bb;margin:32px 0 6px;font-weight:600}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
td,th{padding:6px 14px 6px 0;border-bottom:1px solid #232a31;text-align:left;font-size:13.5px}
th{color:#79838e;font-weight:600;font-size:11.5px;letter-spacing:.03em}
td:last-child,th:last-child{text-align:right}
</style></head><body>
<h1>SPX Altimeter — Access Analytics</h1>
<p class="mut">直近30日（一部は直近14日）／ bot・クローラーは除外</p>
<h2>ページ別（30日）</h2>
<table><tr><th>Path</th><th>Views</th></tr>${rows(byPath, ["path", "n"])}</table>
<h2>日別（14日）</h2>
<table><tr><th>Day</th><th>Views</th></tr>${rows(byDay, ["day", "n"])}</table>
<h2>参照元（30日・上位10）</h2>
<table><tr><th>Referrer</th><th>Views</th></tr>${rows(byRef, ["ref", "n"])}</table>
<h2>国（30日・上位10）</h2>
<table><tr><th>Country</th><th>Views</th></tr>${rows(byCountry, ["country", "n"])}</table>
</body></html>`;
  return new Response(html, { headers: { "content-type": "text/html;charset=utf-8" } });
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);

    if (req.method === "POST" && url.pathname === "/webhook") {
      // Telegram sends this header on every webhook call when a secret_token
      // was set at registration time (see DEPLOY.md) — reject anything else
      // so a stranger can't POST fake updates at your bot.
      const got = req.headers.get("X-Telegram-Bot-Api-Secret-Token");
      if (got !== env.WEBHOOK_SECRET) return new Response("forbidden", { status: 403 });

      const update = await req.json();
      // Telegram only waits a few seconds for the 200; fetchLatest() can be
      // slower than that under cold start. waitUntil lets the response
      // return immediately while the Worker keeps running the actual reply.
      ctx.waitUntil(handleUpdate(update, env));
      return new Response("ok");
    }

    if (url.pathname === "/cron-test" && url.searchParams.get("key") === env.WEBHOOK_SECRET) {
      // Manual trigger for testing the daily push without waiting for the
      // real cron. Gated behind the same secret so it isn't a public toggle.
      await sendDaily(env);
      return new Response("daily push sent");
    }

    if (url.pathname === "/beacon") {
      // Fire-and-forget pageview logger, called from both static pages.
      // Accepts GET (navigator.sendBeacon posts with no meaningful body, a
      // plain fetch fallback uses GET) — method doesn't matter, only the
      // query params do.
      const path = (url.searchParams.get("p") || "/").slice(0, 40);
      let ref = "(direct)";
      try {
        const raw = url.searchParams.get("r") || "";
        ref = raw ? new URL(raw).hostname : "(direct)";
      } catch (e) { ref = "(direct)"; }
      const country = req.cf && req.cf.country ? req.cf.country : "XX";
      const ua = req.headers.get("User-Agent") || "";
      // Skip obvious non-human traffic so it doesn't pollute the counts.
      if (!/bot|spider|crawl|headless|curl|python-requests|monitor|uptime/i.test(ua) && env.PAGEVIEWS) {
        env.PAGEVIEWS.writeDataPoint({
          blobs: [path, country, ref.slice(0, 60), ua.slice(0, 120)],
          doubles: [1],
          indexes: [path],
        });
      }
      return new Response(null, { status: 204 });
    }

    if (url.pathname === "/admin/analytics") {
      const token = url.searchParams.get("token") || "";
      if (!env.ANALYTICS_TOKEN || token !== env.ANALYTICS_TOKEN) {
        return new Response("unauthorized", { status: 401 });
      }
      try {
        return await renderAnalytics(env);
      } catch (e) {
        return new Response("query error: " + e.message, { status: 500 });
      }
    }

    return new Response("SPX Altimeter bot. See /webhook (Telegram only).", { status: 200 });
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(sendDaily(env));
  },
};
