"""English explainer sections for the public SPX Altimeter page.

Content is a fresh English write-up of the same substance as the Japanese
/spx detail sections (spx_detail.py) — not a mechanical translation — but the
three figures reuse identical coordinate geometry (only label text differs),
since those coordinates are back-solved from the channel definition and
verified against the raw data.
"""
import math

CSS = """
.det{margin:0 0 10px}
.det>summary{cursor:pointer;list-style:none;padding:13px 16px;background:var(--surf);
border:1px solid var(--line);border-radius:10px;font-weight:700;font-size:14px;
display:flex;align-items:center;gap:10px;transition:border-color .12s}
.det>summary::-webkit-details-marker{display:none}
.det>summary::before{content:'▶';font-size:10px;color:var(--mut);transition:transform .15s}
.det[open]>summary::before{transform:rotate(90deg)}
.det>summary:hover{border-color:var(--s1)}
.det>summary:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
.det>summary .no{font-size:11px;color:var(--mut);font-weight:600;min-width:14px}
.body{padding:4px 18px 20px;border:1px solid var(--line);border-top:none;
border-radius:0 0 10px 10px;background:var(--surf);margin-top:-10px;padding-top:16px}
.body p{margin:0 0 13px;font-size:13.5px;line-height:1.85}
.body p:last-child{margin-bottom:0}
.body h4{font-size:12.5px;margin:20px 0 8px;color:var(--ink2);letter-spacing:.04em}
.body ul{margin:0 0 13px;padding-left:1.2em;font-size:13.5px;line-height:1.8}
.body li{margin-bottom:5px}
.body table{margin:10px 0 14px}
.body td,.body th{padding:5px 9px;font-size:12.5px}
.fg{background:var(--bg);border:1px solid var(--line);border-radius:8px;
padding:12px;margin:14px 0;overflow-x:auto}
.fg svg{display:block;width:100%;height:auto;min-width:520px}
.fc{font-size:11.5px;color:var(--mut);margin:8px 2px 0;line-height:1.6}
.eq{background:var(--bg);border-left:3px solid var(--s1);padding:10px 14px;
margin:12px 0;font-family:ui-monospace,"Cascadia Mono",Consolas,monospace;
font-size:12px;line-height:1.75;overflow-x:auto;white-space:pre}
.warn2{border-left:3px solid var(--dn);background:rgba(227,73,72,.06);
padding:10px 14px;margin:12px 0;font-size:13px;border-radius:0 6px 6px 0}
.dl{font-size:11px;fill:var(--mut)}
.dt2{font-size:12px;fill:var(--ink2);font-weight:700}
.dax{stroke:var(--line);stroke-width:1}
"""

# ───────────────────────────────── Fig. 1: channel structure
# Geometry back-solved from (x, altitude%) so the sample path never
# crosses the band edges. Do not hand-tune these coordinates.
_X0, _X1, _UY0, _UY1, _H = 60, 580, 190.0, 50.0, 80.0
_up = lambda x: _UY0 + (x - _X0) / (_X1 - _X0) * (_UY1 - _UY0)
_lo = lambda x: _up(x) + _H
_pt = lambda x, a: f"{x},{_lo(x) - a / 100 * _H:.1f}"
_SERIES = [(60, 30), (110, 48), (160, 22), (210, 55), (260, 35), (310, 68),
           (360, 45), (410, 72), (460, 52), (510, 80), (560, 86)]
_PATH = " ".join(_pt(x, a) for x, a in _SERIES)
_MX, _MA = 410, 72
_MY, _MB = _lo(_MX) - _MA / 100 * _H, _lo(_MX)

FIG1 = f"""<svg viewBox="0 0 700 300" role="img" aria-label="Diagram of the channel structure">
<defs><marker id="ar" markerWidth="9" markerHeight="9" refX="7" refY="4.5"
 orient="auto-start-reverse"><path d="M0,1 L8,4.5 L0,8 z" fill="var(--s2)"/></marker></defs>
<polygon points="{_X0},{_UY0} {_X1},{_UY1} {_X1},{_UY1+_H} {_X0},{_UY0+_H}"
 fill="var(--s1)" opacity=".07"/>
<line x1="{_X0}" y1="{_UY0}" x2="{_X1}" y2="{_UY1}" stroke="var(--s1)" stroke-width="2.4"/>
<line x1="{_X0}" y1="{_UY0+_H}" x2="{_X1}" y2="{_UY1+_H}" stroke="var(--s1)" stroke-width="2.4"/>
<line x1="{_X0}" y1="{_UY0+_H*.25}" x2="{_X1}" y2="{_UY1+_H*.25}" stroke="var(--neu)"
 stroke-width="1" stroke-dasharray="4 4"/>
<line x1="{_X0}" y1="{_UY0+_H*.5}" x2="{_X1}" y2="{_UY1+_H*.5}" stroke="var(--s2)"
 stroke-width="1.3" stroke-dasharray="8 4"/>
<line x1="{_X0}" y1="{_UY0+_H*.75}" x2="{_X1}" y2="{_UY1+_H*.75}" stroke="var(--neu)"
 stroke-width="1" stroke-dasharray="4 4"/>
<polyline points="{_PATH}" fill="none" stroke="var(--dn)" stroke-width="2.2"
 stroke-linejoin="round"/>
<text class="dt2" x="586" y="{_UY1+4}" fill="var(--s1)">100% ceiling</text>
<text class="dl" x="586" y="{_UY1+_H*.25+4}">75%</text>
<text class="dt2" x="586" y="{_UY1+_H*.5+4}" fill="var(--s2)">50% mid</text>
<text class="dl" x="586" y="{_UY1+_H*.75+4}">25%</text>
<text class="dt2" x="586" y="{_UY1+_H+4}" fill="var(--s1)">0% floor</text>
<line x1="{_MX-9}" y1="{_MB:.1f}" x2="{_MX+9}" y2="{_MB:.1f}" stroke="var(--s2)"
 stroke-width="1.6"/>
<line x1="{_MX}" y1="{_MB:.1f}" x2="{_MX}" y2="{_MY:.1f}" stroke="var(--s2)"
 stroke-width="1.6" marker-start="url(#ar)" marker-end="url(#ar)"/>
<circle cx="{_MX}" cy="{_MY:.1f}" r="5" fill="var(--dn)" stroke="var(--surf)"
 stroke-width="2"/>
<text class="dt2" x="{_MX+14}" y="{(_MY+_MB)/2-2:.0f}" fill="var(--s2)">Altitude {_MA}%</text>
<text class="dl" x="{_MX+14}" y="{(_MY+_MB)/2+13:.0f}">height above the 0% line</text>
<text class="dl" x="{_X0}" y="288">← time (the whole channel drifts up 7.269%/yr) →</text>
</svg>"""

# ───────────────────────────────── Fig. 2: how the tangent lines are drawn
_X0b, _X1b, _U0b, _U1b, _Hb = 35, 560, 125.0, 45.0, 115.0
_upb = lambda x: _U0b + (x - _X0b) / (_X1b - _X0b) * (_U1b - _U0b)
_lob = lambda x: _upb(x) + _Hb
_ptb = lambda x, a: f"{x},{_lob(x) - a / 100 * _Hb:.1f}"
_SER2 = [(35, 52), (72, 28), (110, 100), (150, 14), (195, 46), (240, 66),
         (275, 24), (310, 0), (355, 34), (400, 56), (445, 76), (470, 88),
         (495, 100), (520, 52), (545, 18), (560, 58)]
_P2 = " ".join(_ptb(x, a) for x, a in _SER2)
_A1, _A2, _A3 = 110, 495, 310
_A1Y, _A2Y, _A3Y = _upb(_A1), _upb(_A2), _lob(_A3)

FIG2 = f"""<svg viewBox="0 0 730 300" role="img" aria-label="How the tangent lines are drawn">
<polyline points="{_P2}" fill="none" stroke="var(--ink2)" stroke-width="1.7"
 stroke-linejoin="round"/>
<line x1="{_X0b}" y1="{_U0b}" x2="{_X1b}" y2="{_U1b}" stroke="var(--s1)" stroke-width="2.4"/>
<line x1="{_X0b}" y1="{_U0b+_Hb}" x2="{_X1b}" y2="{_U1b+_Hb}" stroke="var(--s1)"
 stroke-width="2.4" stroke-dasharray="9 5"/>
<circle cx="{_A1}" cy="{_A1Y:.1f}" r="7" fill="none" stroke="var(--s2)" stroke-width="2.6"/>
<circle cx="{_A2}" cy="{_A2Y:.1f}" r="7" fill="none" stroke="var(--s2)" stroke-width="2.6"/>
<circle cx="{_A3}" cy="{_A3Y:.1f}" r="7" fill="none" stroke="var(--s3)" stroke-width="2.6"/>
<text class="dt2" x="{_A1}" y="{_A1Y-26:.0f}" text-anchor="middle" fill="var(--s2)">Mar 1937</text>
<text class="dl" x="{_A1}" y="{_A1Y-14:.0f}" text-anchor="middle">high 18.67</text>
<text class="dt2" x="{_A2}" y="{_A2Y-26:.0f}" text-anchor="middle" fill="var(--s2)">Mar 2000</text>
<text class="dl" x="{_A2}" y="{_A2Y-14:.0f}" text-anchor="middle">high 1,552.87</text>
<text class="dt2" x="{_A3}" y="{_A3Y+24:.0f}" text-anchor="middle" fill="var(--s3)">Aug 1982</text>
<text class="dl" x="{_A3}" y="{_A3Y+37:.0f}" text-anchor="middle">low 102.20</text>
<text class="dt2" x="568" y="{_U1b+4:.0f}" fill="var(--s1)">100% ceiling</text>
<text class="dl" x="568" y="{_U1b+17:.0f}">through both highs</text>
<text class="dt2" x="568" y="{_U1b+_Hb+4:.0f}" fill="var(--s1)">0% floor</text>
<text class="dl" x="568" y="{_U1b+_Hb+17:.0f}">parallel to ceiling</text>
<text class="dl" x="568" y="{_U1b+_Hb+30:.0f}">touches deepest low</text>
<text class="dl" x="{_X0b}" y="288">← time →  Since Jun 1932, monthly highs have crossed this ceiling 0 times</text>
</svg>"""

# ───────────────────────────────── Fig. 3: hurdle rate for leaving the market
FIG3 = """<svg viewBox="0 0 640 220" role="img" aria-label="Real return difference between staying invested and holding cash">
<line x1="250" y1="26" x2="250" y2="160" class="dax"/>
<rect x="250" y="44" width="268" height="34" rx="5" fill="var(--s3)"/>
<text class="dt2" x="242" y="66" text-anchor="end">stay invested</text>
<text class="dt2" x="528" y="66" fill="var(--s3)">+6.46%</text>
<rect x="94" y="104" width="156" height="34" rx="5" fill="var(--dn)"/>
<text class="dt2" x="242" y="126" text-anchor="end" fill="#fff">cash, no interest</text>
<text class="dt2" x="86" y="126" text-anchor="end" fill="var(--dn)">−3.75%</text>
<path d="M556,44 v96" stroke="var(--s2)" stroke-width="1.4" stroke-dasharray="4 3"/>
<path d="M556,61 h-24 M556,121 h-24" stroke="var(--s2)" stroke-width="1.4"/>
<path d="M556,61 v60" stroke="var(--s2)" stroke-width="2.4"/>
<text class="dt2" x="564" y="88" fill="var(--s2)">gap 10.2</text>
<text class="dl" x="564" y="102">points</text>
<text class="dl" x="320" y="182" text-anchor="middle">Real (inflation-adjusted), annualized return.</text>
<text class="dl" x="320" y="197" text-anchor="middle">That's the expected cost of sitting out the market for a year.</text>
</svg>"""

# 15 crash / correction episodes: (name_en, peak, trough, drawdown%, peak_alt, trough_alt, is_crash30)
EPISODES = [
    ("1957 Recession", "1956-08", "1957-10", -21.5, 74.1, 52.4, False),
    ("Kennedy Slide", "1961-12", "1962-06", -29.3, 74.6, 48.9, False),
    ("1966 Correction", "1966-02", "1966-10", -23.7, 72.8, 51.4, False),
    ("1969–70 Correction", "1968-12", "1970-05", -37.3, 69.1, 31.0, True),
    ("Oil Shock", "1973-01", "1974-10", -49.9, 57.0, 2.2, True),
    ("1981–82 Recession", "1980-11", "1982-08", -28.0, 30.4, 0.0, False),
    ("Black Monday", "1987-08", "1987-10", -35.9, 56.8, 26.1, True),
    ("Gulf War Crisis", "1990-07", "1990-10", -20.4, 49.1, 32.6, False),
    ("LTCM Crisis", "1998-07", "1998-10", -22.4, 90.0, 71.7, False),
    ("Dot-com Crash", "2000-03", "2002-10", -50.5, 100.0, 40.5, True),
    ("Global Financial Crisis", "2007-10", "2009-03", -57.7, 65.2, 0.7, True),
    ("Late-2018 Correction", "2018-09", "2018-12", -20.2, 55.6, 39.3, False),
    ("COVID Crash", "2020-02", "2020-03", -35.4, 58.6, 28.8, True),
    ("2022 Correction", "2022-01", "2022-10", -27.5, 73.1, 47.9, False),
    ("Spring 2025 Correction", "2025-02", "2025-04", -21.3, 74.9, 58.0, False),
]


def _episode_rows():
    out = []
    for name, pk, tr, dd, pa, ta, crash in EPISODES:
        w = "<b>" if crash else ""
        we = "</b>" if crash else ""
        out.append(f"<tr><td>{w}{name}{we}</td><td>{pk} → {tr}</td>"
                   f"<td>{w}{dd:.1f}%{we}</td><td>{pa:.1f}%</td><td>{ta:.1f}%</td></tr>")
    return "".join(out)


def build(n_months=1868):
    S = []
    _n = [0]

    def sec(title, body, open_=False):
        _n[0] += 1
        S.append(f'<details class="det"{" open" if open_ else ""}>'
                 f'<summary><span class="no">{_n[0]}</span>{title}</summary>'
                 f'<div class="body">{body}</div></details>')

    sec("What &ldquo;Altitude&rdquo; means", f"""
<p>Altitude is a home-built 0–100% gauge for where the S&amp;P 500 sits inside a rising
&ldquo;flight corridor&rdquo; on a log scale &mdash; the <b>floor is 0%</b>, the <b>ceiling is 100%</b>,
and the space between is a channel that drifts upward at a constant rate.</p>
<div class="fg">{FIG1}<p class="fc">The corridor itself climbs 7.269%/yr, so holding altitude
still requires the price to rise 7.269%/yr. <b>A falling altitude does not mean the price is
falling</b> &mdash; only that it's rising slower than the channel.</p></div>
<div class="eq">t     = year + (month-1)/12 + (day-1)/(days_in_month × 12)
altitude = (log(price) − (AU + BU × t) + WIDTH) / WIDTH × 100   [%]

AU    = -133.011205444447   ceiling intercept (log)
BU    =    0.070173684970   ceiling slope (= 7.269%/yr)
WIDTH =    1.487041168721   channel width (= 4.424×)</div>
<h4>Where it sits historically</h4>
<p>Since June 1932 (1,131 months), altitude has averaged <b>50.6%</b>, median <b>50.0%</b> &mdash;
it clings to the middle of the channel. All-time high: <b>98.2%</b> (Feb 1937). All-time low:
<b>3.5%</b> (Jul 1982).</p>""", open_=True)

    sec("How the channel is drawn", f"""
<p>Not a regression (no ±2σ band). The lines are <b>tangents to the actual candle highs and
lows</b>, so overshoots and undershoots are captured directly rather than averaged away.</p>
<div class="fg">{FIG2}<p class="fc">The ceiling connects the March 1937 high (18.67) and the
March 2000 high (1,552.87) on a log scale, extended both ways. The floor runs parallel,
dropped to touch the deepest low on record (102.20, Aug 1982).</p></div>
<table><tbody>
<tr><td>Slope</td><td><b>7.269%/yr</b> (1.920 decades over 63 years)</td></tr>
<tr><td>Channel width</td><td><b>4.424×</b> (ceiling ÷ floor)</td></tr>
<tr><td>Floor → ceiling transit time</td><td>width ÷ slope = <b>21 yr 2 mo</b></td></tr>
</tbody></table>
<h4>The striking part</h4>
<p><b>From June 1932 to today &mdash; 1,131 months &mdash; no monthly high has crossed the
ceiling.</b> Excluding the two anchor points, the closest approaches were Feb 1937 (0.986×)
and Apr 2000 (0.976×), measured against the ceiling on the actual date the high was set (the
channel's time axis is anchored to month-start, so same-month measurements need the exact
day). Checked against <b>daily</b> data too: across 23,669 trading days since 1932, the
ceiling was crossed on <b>zero</b> days.</p>
<p>The floor is symmetric: the <b>2009-03-06</b> low sits at <b>1.0092×</b> the floor on that
date &mdash; the second-closest touch in 94 years.</p>
<p>But there's a circularity worth naming: <b>a line drawn through the two highest points, by
construction, cannot be crossed by those same two points.</b> Zoom out past 1932 and it breaks
immediately &mdash; August 1929 traded at 2.89× the extended ceiling, and January 1871 sits at
24.7×. The &ldquo;never crossed&rdquo; claim describes 1932–present only, and it's partly a
property of how the line was drawn, not purely a discovery.</p>""")

    sec("What this can't do", f"""
<div class="warn2"><b>Trading on this indicator has not made money in backtests.</b>
30 rule variants were tested against 92 years of data. None beat buy-and-hold.</div>
<h4>The cost of leaving the market</h4>
<div class="fg">{FIG3}<p class="fc">Since this only trades the S&amp;P 500 itself, selling
means parking in cash, and cash loses to inflation. <b>To come out ahead, you'd need to call
drawdowns worth more than 10.2 points a year, every year.</b></p></div>
<h4>What was tested</h4>
<table><tbody>
<tr><td>30-strategy sweep</td><td>Symmetric, buy-the-dip, and ceiling-only variants all failed.
White's Reality Check <b>p = 0.21–0.25</b> (i.e. not distinguishable from noise after
correcting for having tried 30 strategies)</td></tr>
<tr><td>Original rule</td><td>Fired only <b>once</b> in 62 years. After that sale
(May 1997), the price rose another <b>78%</b> before the eventual top</td></tr>
<tr><td>Walk-forward</td><td>Re-drawing the channel with only past data at each point exits
the market in <b>Jul 1987</b> and doesn't re-enter until <b>Jul 2002</b> &mdash; sitting out
one of the largest bull runs on record</td></tr>
<tr><td>Is the parallelism real?</td><td>Against random log-walks with the same drift and
volatility, <b>27% produce equally parallel tangents by chance</b> (p = 0.270) &mdash;
because in a long random walk both tangents converge on the drift rate regardless</td></tr>
<tr><td>Drawdown control</td><td>Worst drawdown −50.1% vs. buy-and-hold's −51.8%. Since the
rule buys back 100% at the 0% line, it always takes the next crash fully invested</td></tr>
</tbody></table>
<p><b>This is a map, not a trading signal.</b> Use it as one, and you're taking on
open-ended upside risk in exchange for a hurdle rate you have to clear every single year.</p>""")

    sec("15 drawdowns of 20% or more (1932–present)", f"""
<p>Peaks and troughs are measured on monthly highs/lows within the channel's valid range
(Jun 1932 onward). <b>Bold rows</b> are the 6 episodes of −30% or worse; the rest are
−20% to −30% pullbacks.</p>
<table>
<thead><tr><th>Episode</th><th>Peak → trough</th><th>Drawdown</th>
<th>Peak alt.</th><th>Trough alt.</th></tr></thead>
<tbody>{_episode_rows()}</tbody></table>
<p>Peak altitude has essentially no predictive value for drawdown depth: the correlation
across all 15 episodes is <b>r = −0.119</b>. The Dot-com Crash started at the ceiling
(100.0%) and fell 50.5%; the 2008 Global Financial Crisis &mdash; the deepest of the
group at −57.7% &mdash; started from an unremarkable <b>65.2%</b>. The single episode that
reached the floor (0.0%) started from <b>30.4%</b>, the lowest starting altitude of the 15.
The 1929 crash (−86.2% peak-to-trough) is excluded: its peak sits outside the channel's
valid range.</p>""")

    sec("Is the altitude distribution actually normal?", """
<p>Take the 1,131 monthly closes since June 1932 and histogram them. The shape is close to
a bell curve: mean <b>50.58%</b>, median <b>50.02%</b>, skewness <b>+0.04</b> (essentially
symmetric), excess kurtosis <b>−0.34</b> (slightly thinner tails than normal &mdash; no
month has ever landed below 0% or above 100%, by construction).</p>
<p>Two of four normality tests reject the null (Shapiro–Wilk p = 7×10⁻⁵,
Anderson–Darling stat 1.18 vs. a 0.75 critical value); two don't
(Kolmogorov–Smirnov p = 0.51, Jarque–Bera p = 0.06). What they're detecting is the thin
tails, not outliers.</p>
<div class="warn2"><b>The 1,131 observations are not 1,131 independent data points.</b>
Monthly altitude has an AR(1) autocorrelation of <b>0.9844</b>, which works out to an
<b>effective sample size of about 8.9</b>. Treat every statistic on this page with that
in mind &mdash; a smooth-looking histogram here is mostly a smooth-looking random walk,
not a large sample.</p>""")

    sec("Data & methodology", """
<table><tbody>
<tr><td>Price, 1927-12 onward</td><td>Yahoo Finance <code>^GSPC</code> daily bars,
aggregated into monthly / weekly / daily OHLC as needed for the current zoom level</td></tr>
<tr><td>Price, 1871-01 – 1927-11</td><td>Robert Shiller's monthly dataset (Cowles Commission
reconstruction). Monthly averages only &mdash; no daily high/low exists for this stretch</td></tr>
<tr><td>Splice check</td><td>Over the 1,150-month overlap, Shiller's monthly average falls
inside the monthly high/low range <b>99.9%</b> of the time; median deviation from the
close is −0.43%</td></tr>
<tr><td>Update cadence</td><td>A GitHub Actions cron job re-fetches daily and republishes
<code>data/latest.json</code>. The page fetches it client-side; no server involved</td></tr>
</tbody></table>
<p>All prices are <b>nominal, price-only</b> &mdash; not real, not total-return. The
channel's 7.269% slope includes inflation and excludes dividends.</p>
<p class="fc">Yahoo Finance's endpoint is unofficial and could change or go away. Full
source, including the backtest code, the random-walk parallelism test, and the walk-forward
simulation, is linked at the bottom of this page.</p>""")

    return CSS, ("<h2 style=\"font-size:15px;margin:26px 0 12px;color:var(--ink2)\">"
                 "How this works</h2>" + "".join(S))
