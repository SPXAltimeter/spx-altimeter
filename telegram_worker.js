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
  const rest = (100 - d.alt_h).toFixed(1);
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

    return new Response("SPX Altimeter bot. See /webhook (Telegram only).", { status: 200 });
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(sendDaily(env));
  },
};
