# SPX Altimeter

A 0–100% gauge for where the S&P 500 sits inside its 1871–present log
channel — floor at 0%, ceiling at 100% — plus an interactive candlestick
chart (monthly → weekly → daily, auto-zooming) and a backtest writeup of
the 30 trading rules that tried to use this and lost to buy-and-hold.

**Live site:** _fill in after deploying — see `DEPLOY.md`_
**Telegram bot:** `/now` for an on-demand reading, `/subscribe` for one
daily message — see `DEPLOY.md` for setup.

## What's here

- `index.html` / `ja/index.html` — the pages (self-contained, built by
  `make_global_page.py`)
- `fetch_public.py` + `.github/workflows/update.yml` — daily data refresh,
  no server required
- `telegram_worker.js` — the bot, runs as a free Cloudflare Worker
- `DEPLOY.md` — the full setup guide

## Known gap: `chart_component.py` is not in this repo

`build_global_chart.py` does `import chart_component as cc` from the
repo's **parent** directory, and `make_global_page.py` (which rebuilds
`index.html`'s embedded monthly/weekly/daily chart data) depends on it.
That file — and the source CSVs it reads (`spx_long_1871.csv`,
`spx_weekly_1927.csv`, expected next to it, one level above this repo) —
are not committed here and were not found anywhere else on this machine
as of 2026-11-07. Until that's located or recreated, **`make_global_page.py`
cannot be run**, so the embedded chart data in `index.html` / `ja/index.html`
can only be hand-patched, not regenerated from scratch.

**Why this matters (2026-11-07 incident):** the daily GitHub Action only
ever updates `data/latest.json` / `data/weeks.json` / `data/months.json` —
it never rebuilds the embedded monthly chart data in `index.html`. The
embedded monthly series also used to be kept current client-side by
`window.__lchSetLatest`, but that function only ever patches a single
"current month" entry. Because the page hadn't been rebuilt since
2026-08-16, three months (2026-09, 2026-10, and a stale/partial 2026-08)
went missing from the monthly chart — `__lchSetLatest` kept overwriting
the same last array slot instead of ever appending 09 or 10.

Fixed for now by: (1) hand-patching the embedded monthly arrays in both
pages with the correct OHLC for 2026-08/09/10/11, computed from
`data/weeks.json`'s daily bars; (2) adding a `data/months.json` (last ~15
confirmed + in-progress months, written by `fetch_public.py`) and a new
`window.__lchMergeMonths` client-side function (patched directly into both
pages' embedded JS, right after `function mergeInto(...)`) that merges the
*whole* array by `ym` — like `__lchMergeWeeks`/`__lchMergeDays` already do
for weekly/daily — so any number of skipped months get backfilled instead
of silently gapping. `make_global_page.py` now also fetches
`data/months.json` and calls `__lchMergeMonths`, but **if `chart_component.py`
is ever recovered and `make_global_page.py` is run again, port the
`mergeMonths`/`window.__lchMergeMonths` function into `chart_component.py`
itself** (next to `mergeInto`) — otherwise a fresh rebuild will silently
drop this fix along with the hand-patch.

## Data & methodology

Channel definition, backtests, and all caveats (including why this indicator
has no trading value in 92 years of testing) are on the page itself, under
"How this works." Price data: Robert Shiller's dataset (1871–1927, monthly)
spliced with Yahoo Finance `^GSPC` daily bars (1927–present).

## License

MIT — see `LICENSE`. Not investment advice.
