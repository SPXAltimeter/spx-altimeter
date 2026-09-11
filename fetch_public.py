#!/usr/bin/env python3
"""SPX Altimeter (global, public) — daily data updater for GitHub Actions.

Writes two public JSON files, no personal data, no LINE dependency:
  data/latest.json — current altitude, level, channel prices (mirrors N100's
                      latest.json but with no personal fields)
  data/weeks.json   — recent weekly + daily bars, for the chart to splice in
                      after the page's embedded data goes stale (same technique
                      as the private N100 deployment's weeks.json)

Run by .github/workflows/update.yml on a daily cron. No secrets required —
Yahoo Finance's chart endpoint is public and unauthenticated.
"""
import datetime
import json
import math
import os
import sys
import urllib.request

AU = -133.011205444447
BU = 0.070173684970
WIDTH = 1.487041168721

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
YAHOO = ("https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
         "?range=2y&interval=1d")
RECENT_WEEKS = 110
RECENT_DAYS = 400


def days_in_month(y, m):
    return (datetime.date(y + (m == 12), m % 12 + 1, 1) - datetime.date(y, m, 1)).days


def t_of(d):
    return d.year + (d.month - 1) / 12.0 + (d.day - 1) / (days_in_month(d.year, d.month) * 12.0)


def level_price(t, pct):
    return math.exp(AU + BU * t - WIDTH * (1 - pct / 100.0))


def position(price, t):
    return (math.log(price) - (AU + BU * t) + WIDTH) / WIDTH * 100.0


def fetch():
    req = urllib.request.Request(YAHOO, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        d = json.load(r)
    res = d["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    ts = res["timestamp"]
    rows = [(datetime.datetime.fromtimestamp(t, datetime.timezone.utc).date(), c, h, o, lo)
            for t, c, h, o, lo in zip(ts, q["close"], q["high"], q["open"], q["low"])
            if c and h and o and lo]
    if not rows:
        raise RuntimeError("Yahoo response had no usable rows")
    last_date, last_close = rows[-1][0], rows[-1][1]
    cur = [r for r in rows if (r[0].year, r[0].month) == (last_date.year, last_date.month)]
    return (last_close, last_date, max(r[2] for r in cur), cur[0][3],
            min(r[4] for r in cur), rows)


def build_weeks(rows, n=RECENT_WEEKS):
    bk = {}
    for d, c, h, o, lo in rows:
        k = d - datetime.timedelta(days=d.weekday())
        b = bk.get(k)
        if b is None:
            bk[k] = {"d0": d, "d1": d, "o": o, "h": h, "l": lo, "c": c}
        else:
            b["d1"] = d
            b["h"] = max(b["h"], h)
            b["l"] = min(b["l"], lo)
            b["c"] = c
    out = []
    for k in sorted(bk)[-n:]:
        b = bk[k]
        out.append({"ym": f"{b['d0']}", "ye": f"{b['d1']}", "t": round(t_of(b["d0"]), 6),
                    "o": round(b["o"], 2), "h": round(b["h"], 2),
                    "l": round(b["l"], 2), "c": round(b["c"], 2)})
    return out


def build_days(rows, n=RECENT_DAYS):
    return [{"ym": f"{d}", "t": round(t_of(d), 6), "o": round(o, 2),
             "h": round(h, 2), "l": round(lo, 2), "c": round(c, 2)}
            for d, c, h, o, lo in rows[-n:]]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        close, date, high, m_open, m_low, daily = fetch()
    except Exception as e:                                   # noqa: BLE001
        print(f"fetch failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    t = t_of(date)
    now = datetime.datetime.now(datetime.timezone.utc)
    latest = {
        "ym": f"{date:%Y-%m}", "date": f"{date}",
        "close": round(close, 2), "high": round(high, 2),
        "open": round(m_open, 2), "low": round(m_low, 2),
        "alt_c": round(position(close, t), 2), "alt_h": round(position(high, t), 2),
        "levels": {str(p): round(level_price(t, p), 2)
                   for p in (100, 98, 95, 90, 75, 50, 25, 0)},
        "updated_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "channel": {"slope_pct_pa": round(math.expm1(BU) * 100, 3),
                    "width_x": round(math.exp(WIDTH), 3)},
    }
    with open(os.path.join(DATA_DIR, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, separators=(",", ":"))

    weeks = {"updated_utc": latest["updated_utc"],
             "weeks": build_weeks(daily), "days": build_days(daily)}
    with open(os.path.join(DATA_DIR, "weeks.json"), "w", encoding="utf-8") as f:
        json.dump(weeks, f, ensure_ascii=False, separators=(",", ":"))

    print(f"latest.json: {date} close={close:.2f} altitude={latest['alt_c']:.1f}%")
    print(f"weeks.json: {len(weeks['weeks'])} weeks + {len(weeks['days'])} days")
    return 0


if __name__ == "__main__":
    sys.exit(main())
