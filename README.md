# SPX Altimeter

A 0–100% gauge for where the S&P 500 sits inside its 1871–present log
channel — floor at 0%, ceiling at 100% — plus an interactive candlestick
chart (monthly → weekly → daily, auto-zooming) and a backtest writeup of
the 30 trading rules that tried to use this and lost to buy-and-hold.

**Live site:** _fill in after deploying — see `DEPLOY.md`_
**Telegram bot:** `/now` for an on-demand reading, `/subscribe` for one
daily message — see `DEPLOY.md` for setup.

## What's here

- `index.html` — the page (self-contained, built by `make_global_page.py`)
- `fetch_public.py` + `.github/workflows/update.yml` — daily data refresh,
  no server required
- `telegram_worker.js` — the bot, runs as a free Cloudflare Worker
- `DEPLOY.md` — the full setup guide

## Data & methodology

Channel definition, backtests, and all caveats (including why this indicator
has no trading value in 92 years of testing) are on the page itself, under
"How this works." Price data: Robert Shiller's dataset (1871–1927, monthly)
spliced with Yahoo Finance `^GSPC` daily bars (1927–present).

## License

MIT — see `LICENSE`. Not investment advice.
