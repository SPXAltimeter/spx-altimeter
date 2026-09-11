# SPX Altimeter — Global (Stage 1) — Deploy guide

Everything in this folder is built and tested locally (Playwright-driven
browser tests, geometry/overflow checks on the SVG figures, live data
end-to-end). What's left needs credentials I don't have: GitHub push access,
a Telegram bot token, and a Cloudflare account. This doc is the exact,
copy-pasteable path through those steps.

**Total cost: $0/month.** GitHub Pages, GitHub Actions (well under the free
2,000 min/month), Cloudflare Workers, Cloudflare KV, and the Telegram Bot API
are all free at this scale.

---

## What's in this folder

| File | What it is |
|---|---|
| `index.html` | The public page (built from the other files below — see "Rebuilding" at the bottom) |
| `data/latest.json`, `data/weeks.json` | Sample data, already fetched once so the page isn't empty on first load |
| `fetch_public.py` | The daily data updater (no personal info, no LINE dependency) |
| `.github/workflows/update.yml` | Runs `fetch_public.py` on a cron and commits the result |
| `telegram_worker.js` | The Telegram bot, as a Cloudflare Worker |
| `build_global_chart.py`, `global_detail.py`, `make_global_page.py` | The page generator (reuses your private `/spx` chart component, translated) |
| `test_global.py` | The Playwright test suite that verified all of this |

---

## Part A — Publish the page (GitHub Pages)

### A1. Pick a home for it

**Recommended: a new, separate public repo** (e.g. `spx-altimeter`), not a
folder inside your other personal-portal repo. Reasons: its own Actions run
(won't touch that portal's automation), it's trivial to hand off a link
without exposing the rest of your GitHub account's context, and if you ever
want to stop maintaining it, deleting one repo is cleaner than untangling a
subpath.

If you'd rather keep everything in one place, a subfolder of an existing
repo works too — just adjust the paths below accordingly (and note its
existing GitHub Actions minutes budget will be shared).

### A2. Create the repo and push

```bash
# from this folder
git init
git add .
git commit -m "SPX Altimeter: public English page + daily data + Telegram bot"

# create the repo on GitHub first (via the website, or `gh repo create` if
# you have the CLI authenticated), then:
git remote add origin git@github.com:<you>/spx-altimeter.git
git branch -M main
git push -u origin main
```

### A3. Turn on GitHub Pages

Repo → **Settings → Pages** → Source: **Deploy from a branch** → Branch:
`main` / `/ (root)` → Save.

Your URL will be `https://<you>.github.io/spx-altimeter/`.

### A4. Let Actions write to the repo

The workflow has `permissions: contents: write` built in, which is usually
enough. If the first scheduled run fails with a permissions error:
**Settings → Actions → General → Workflow permissions → Read and write
permissions → Save.**

### A5. Verify

- Wait for Pages to build (a minute or two), then load your URL. You should
  see live-ish data (from the sample `data/latest.json` already in the repo).
- **Settings → Actions → your workflow → Run workflow** to trigger it
  manually once, confirm it commits an updated `data/latest.json`.
- After that, it runs weekdays at 22:30 UTC (06:30 JST) automatically — see
  the cron line in `.github/workflows/update.yml` if you want a different
  time.

---

## Part B — The Telegram bot

### B1. Create the bot (you have to do this — I can't message BotFather for you)

1. Open Telegram, message **@BotFather**.
2. `/newbot` → give it a name (e.g. "SPX Altimeter") and a username ending
   in `bot` (e.g. `spx_altimeter_bot`).
3. BotFather replies with a **token** that looks like `123456:ABC-def...`.
   Save it somewhere private — treat it like a password (anyone with it can
   send messages as your bot).

### B2. Create a Cloudflare account + KV namespace

1. Sign up at [dash.cloudflare.com](https://dash.cloudflare.com) (free).
2. **Workers & Pages → KV** → Create a namespace, name it `SUBSCRIBERS`.

### B3. Deploy the Worker (dashboard method — no CLI needed)

1. **Workers & Pages → Create → Workers → Create Worker.** Name it
   `spx-altimeter-bot` (or anything).
2. Click **Edit code**, delete the placeholder, paste in the full contents
   of `telegram_worker.js`, click **Deploy**.
3. Back on the Worker's page → **Settings → Variables**:
   - **KV Namespace Bindings**: add binding `SUBSCRIBERS` → your KV
     namespace from B2.
   - **Environment Variables** → add `DATA_URL` (plain text) =
     `https://<you>.github.io/spx-altimeter/data/latest.json`
   - **Environment Variables** → add `BOT_TOKEN` (click **Encrypt**) = the
     token from B1.
   - Add `WEBHOOK_SECRET` (click **Encrypt**) = any random string you make
     up (e.g. run `openssl rand -hex 20` or just mash the keyboard — this is
     only to stop strangers from POSTing fake messages to your bot).
4. **Settings → Triggers → Cron Triggers → Add Cron Trigger.** Use
   `35 22 * * 1-5` (5 minutes after the data update, weekdays, UTC) so the
   daily push always has fresh numbers.
5. Note your Worker's URL, shown at the top of the page:
   `https://spx-altimeter-bot.<your-subdomain>.workers.dev`

### B4. Point Telegram at the Worker

One curl command, using the token from B1 and the secret from B3 and the URL
from B3 step 5 — **run this yourself**, since it contains your bot token:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "content-type: application/json" \
  -d '{
    "url": "https://spx-altimeter-bot.<your-subdomain>.workers.dev/webhook",
    "secret_token": "<the WEBHOOK_SECRET you made up in B3>"
  }'
```

A `{"ok":true,"result":true,...}` response means it worked.

### B5. Test it

Open Telegram, find your bot by the username you gave it in B1, send `/start`,
then `/now`. You should get a live reading back within a second or two.

Test the daily push without waiting for the cron:

```bash
curl "https://spx-altimeter-bot.<your-subdomain>.workers.dev/cron-test?key=<WEBHOOK_SECRET>"
```

That sends the daily message to every current subscriber immediately (useful
for checking formatting; harmless to run once you've subscribed yourself).

---

## Why this design stays out of "investment advice" territory

Both Japan's 金商法 and the US/EU equivalents (SEC's *Lowe v. SEC* publisher's
exemption, MiFID II, FSMA) draw roughly the same line: **the same content, to
everyone, is fine; a personalized recommendation is regulated.** This build
was deliberately kept on the safe side of that line:

- `/now` and the daily push send **identical text to everyone** — no
  per-user thresholds, no "you should sell" language.
- There's no way for a user to configure a custom alert level. If you add
  one later (see Stage 2 notes below), that's the point where you should
  get this reviewed by someone qualified, not extrapolate from this note.
- The message itself states plainly that the indicator doesn't work as a
  trading signal (linking to the backtest results), which cuts against any
  reading of it as advice.

**I'm not a lawyer and this isn't legal advice** — it's the same reasoning
from our earlier conversation, now baked into the code instead of just
discussed. If this gets real traction, it's worth 30 minutes with someone
qualified before scaling further.

---

## Suggested order of operations

1. Do Part A only. Watch the daily Action run for a few days. Confirm the
   page looks right, `data/latest.json` actually updates, nothing breaks.
2. Do Part B. Use the bot yourself for a week.
3. **Only then**, post it somewhere (Hacker News "Show HN", r/algotrading,
   r/investing). Lead with the honest-findings section ("I built this, then
   proved it doesn't work as a signal") — that's the actual hook for a
   technical audience, more than the chart itself.
4. Watch what happens. If nobody cares, you've spent $0 and a few hours.
   If people do, *that's* the signal to think about Stage 2 (paid tiers,
   custom alerts, and — only at that point — actually consulting someone
   on the regulatory question for real).

---

## Rebuilding the page after an edit

If you change `global_detail.py` (wording) or want a different default
zoom range, rebuild with:

```bash
python make_global_page.py
```

This regenerates `index.html` from scratch (embeds the full 1871–2026
history again, ~780KB). Run `python test_global.py` afterward if you have
Playwright + Edge installed locally — it serves the folder over a throwaway
local HTTP server and checks rendering, live-data wiring, zoom/LOD
switching, and (importantly) that no Japanese text leaked back in.
