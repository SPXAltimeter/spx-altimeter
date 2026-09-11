"""Build the public, English-language SPX Altimeter page (index.html).

No token auth, no personal data. Live values come from data/latest.json and
data/weeks.json, written daily by .github/workflows/update.yml (fetch_public.py).
If those files are missing (e.g. before the first Action run), the page still
works off its embedded history — it just shows a "not live yet" notice.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build_global_chart import build_chart_en          # noqa: E402
import global_detail                                    # noqa: E402

CH_CSS, CH_HTML, CH_JS, CH_N, CH_W, CH_D = build_chart_en(start=1932.4)
DET_CSS, DET_HTML = global_detail.build(CH_N)

CSS = """
:root{color-scheme:light;
--bg:#f4f6f8;--surf:#fff;--ink:#11161c;--ink2:#4e5862;--mut:#88929c;
--line:#dfe4e9;--grid:#edf0f3;--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--neu:#9aa4ae;
--up:#1baf7a;--dn:#e34948;--warn:#eda100}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){
color-scheme:dark;
--bg:#0c0f13;--surf:#12161b;--ink:#e8edf2;--ink2:#a3adb7;--mut:#77818b;
--line:#222932;--grid:#1a2028;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--neu:#6f7983;
--up:#199e70;--dn:#e66767;--warn:#c98500}}
:root[data-theme="dark"]{color-scheme:dark;
--bg:#0c0f13;--surf:#12161b;--ink:#e8edf2;--ink2:#a3adb7;--mut:#77818b;
--line:#222932;--grid:#1a2028;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--neu:#6f7983;
--up:#199e70;--dn:#e66767;--warn:#c98500}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased;
-webkit-text-size-adjust:100%}
.wrap{max-width:1180px;margin:0 auto;padding:20px 16px 64px}
header{display:flex;align-items:center;gap:12px;margin:0 0 4px}
header img{width:38px;height:38px;border-radius:9px;flex:none}
h1{font-size:20px;font-weight:800;margin:0;letter-spacing:-.01em}
.sub{color:var(--mut);font-size:13px;margin:0 0 18px 50px}
.hero{background:var(--surf);border:1px solid var(--line);border-radius:12px;
padding:22px 20px;margin:0 0 12px;display:grid;
grid-template-columns:minmax(200px,1fr) 2fr;gap:20px;align-items:center}
@media(max-width:640px){.hero{grid-template-columns:1fr;gap:16px}.sub{margin-left:0}}
.big{text-align:center}
.big .lab{font-size:11px;color:var(--mut);letter-spacing:.12em;margin:0 0 2px;
text-transform:uppercase}
.big .v{font-size:56px;font-weight:800;line-height:1;margin:0;
font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.big .u{font-size:26px;font-weight:700;margin-left:2px}
.big .n{font-size:12.5px;color:var(--ink2);margin:8px 0 0}
.gauge{height:9px;background:var(--grid);border-radius:5px;margin:14px 0 0;
position:relative;overflow:hidden}
.gauge i{position:absolute;left:0;top:0;bottom:0;border-radius:5px;
background:linear-gradient(90deg,var(--s3),var(--warn),var(--dn))}
.gt{display:flex;justify-content:space-between;font-size:10.5px;color:var(--mut);
margin-top:4px}
table{border-collapse:collapse;width:100%;font-size:13.5px;
font-variant-numeric:tabular-nums}
th,td{text-align:right;padding:6px 10px;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}
thead th{color:var(--mut);font-weight:600;font-size:11px;letter-spacing:.04em}
.up{color:var(--up)}.dn{color:var(--dn)}
.card{background:var(--surf);border:1px solid var(--line);border-radius:12px;
padding:18px;margin:0 0 12px}
.lg{display:flex;flex-wrap:wrap;gap:6px 16px;margin:10px 2px 0;font-size:11.5px;color:var(--ink2)}
.lg span{display:inline-flex;align-items:center;gap:6px}
.k2{width:12px;height:12px;border-radius:3px;flex:none}
.k2.l{height:3px;width:17px;border-radius:2px}
.card h2{font-size:14px;margin:0 0 10px;font-weight:700;color:var(--ink2)}
footer{color:var(--mut);font-size:11.5px;margin-top:22px;line-height:1.8}
footer a{color:var(--ink2)}
.stale{background:rgba(237,161,0,.12);border:1px solid var(--warn);color:var(--warn);
border-radius:8px;padding:9px 13px;font-size:12.5px;margin:0 0 12px;display:none}
.cta{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 0}
.cta a{font-size:12.5px;font-weight:700;padding:8px 14px;border-radius:8px;
text-decoration:none;border:1px solid var(--line);color:var(--ink2)}
.cta a.pri{background:var(--s1);border-color:var(--s1);color:#fff}
code{font-family:ui-monospace,Consolas,monospace;background:var(--grid);
padding:1px 5px;border-radius:4px;font-size:12px}
"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="How far is the S&amp;P 500 flying inside its 1932-present log channel? A 0-100% altitude gauge, an interactive 1871-2026 chart, and an honest writeup of the 30 trading rules that failed to beat buy-and-hold.">
<meta name="theme-color" content="#12161b">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>%F0%9F%93%88</text></svg>">
<title>SPX Altimeter</title>
<meta property="og:title" content="SPX Altimeter">
<meta property="og:description" content="A 0-100% gauge for where the S&amp;P 500 sits in its long-run log channel, plus the backtests that show it isn't a trading signal.">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
<style>{CSS}{CH_CSS}{DET_CSS}</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>📈 SPX Altimeter</h1>
</header>
<p class="sub">How far the S&amp;P 500 is flying inside its 1871–2026 log channel</p>

<div class="stale" id="stale"></div>

<div class="hero">
  <div class="big">
    <p class="lab">Current altitude</p>
    <p class="v"><span id="alt">--</span><span class="u">%</span></p>
    <p class="n"><b id="rest">--</b> points to the ceiling</p>
  </div>
  <div>
    <table><tbody>
      <tr><td>S&amp;P 500 close</td><td id="close" style="font-size:19px;font-weight:700">--</td></tr>
      <tr><td>This month's high</td><td id="high">--</td></tr>
      <tr><td>Data date (UTC)</td><td id="date">--</td></tr>
    </tbody></table>
    <div class="gauge"><i id="gauge" style="width:0%"></i></div>
    <div class="gt"><span>0% floor</span><span>50% mid</span><span>100% ceiling</span></div>
  </div>
</div>

<div class="card">
  <h2>Channel line prices</h2>
  <table>
    <thead><tr><th>Altitude</th><th>S&amp;P 500</th><th>vs. now</th></tr></thead>
    <tbody id="levels"><tr><td colspan="3" style="color:var(--mut)">Loading…</td></tr></tbody>
  </table>
</div>

<div class="card">
  <h2>1871–2026 chart ({CH_N:,} monthly / {CH_W:,} weekly / {CH_D:,} daily bars)</h2>
  {CH_HTML}
  <div class="lg">
    <span><i class="k2" style="background:var(--up)"></i>up candle</span>
    <span><i class="k2" style="background:var(--dn)"></i>down candle</span>
    <span><i class="k2 l" style="background:#7c6bb5"></i>1871–1927 monthly average</span>
    <span><i class="k2 l" style="background:var(--s1)"></i>ceiling / floor</span>
    <span><i class="k2 l" style="background:var(--s2)"></i>mid (50%)</span>
    <span><i class="k2" style="background:var(--dn)"></i>▼ Crash 30%+ (6)</span>
    <span><i class="k2" style="background:var(--warn)"></i>▽ Correction 20-30% (9)</span>
    <span><i class="k2" style="background:rgba(125,135,145,.35)"></i>outside channel range</span>
  </div>
  <p style="font-size:12px;color:var(--ink2);margin:10px 0 0">
  Scroll to zoom (auto-switches monthly → weekly → daily), drag to pan, double-click to
  reset. Daily candles only render from 1962 onward (earlier daily bars have no intraday
  high/low on record). Hover to read any bar's OHLC and altitude.</p>
</div>

{DET_HTML}

<footer>
  Channel: tangent through the Mar 1937 high (18.67) and Mar 2000 high (1,552.87), extended
  both ways. Floor is parallel, touching the Aug 1982 low. Slope 7.269%/yr, width 4.424×.<br>
  Price data: Robert Shiller (1871–1927, monthly average), Yahoo Finance <code>^GSPC</code>
  (1927–present, daily OHLC). Refreshed daily via GitHub Actions. This is not investment
  advice — see &ldquo;What this can't do&rdquo; above.<br>
  Built with an <a href="https://github.com/">open-source</a> pipeline; the page,
  the backtests, and the daily updater are all in one small repo.
</footer>
</div>

<script>
const F=v=>v>=1000?Math.round(v).toLocaleString():v.toFixed(2);
fetch('data/latest.json',{{cache:'no-store'}}).then(r=>{{
  if(!r.ok)throw new Error('HTTP '+r.status);
  return r.json();
}}).then(d=>{{
  if(typeof d.alt_c!=='number')throw new Error('bad response');
  document.getElementById('alt').textContent=d.alt_c.toFixed(1);
  document.getElementById('rest').textContent=(100-d.alt_h).toFixed(1);
  document.getElementById('close').textContent=F(d.close);
  document.getElementById('high').textContent=F(d.high)+' (altitude '+d.alt_h.toFixed(1)+'%)';
  document.getElementById('date').textContent=d.date+' · updated '+d.updated_utc;
  document.getElementById('gauge').style.width=Math.max(0,Math.min(100,d.alt_c))+'%';
  const rows=[100,98,95,75,50,25,0].map(k=>{{
    const p=d.levels[k], df=(p/d.close-1)*100;
    return '<tr><td>'+k+'%</td><td>'+F(p)+'</td><td class="'+(df>=0?'up':'dn')+'">'+
      (df>=0?'+':'')+df.toFixed(1)+'%</td></tr>';}});
  document.getElementById('levels').innerHTML=rows.join('');
  const age=(Date.now()-new Date(d.updated_utc).getTime())/86400000;
  if(age>3){{const s=document.getElementById('stale');
    s.style.display='block';
    s.textContent='This data is '+age.toFixed(1)+' days old. The daily update may be paused.';}}
  if(window.__lchSetLatest)window.__lchSetLatest(d);
}}).catch(e=>{{
  const s=document.getElementById('stale');s.style.display='block';
  s.textContent="Live data isn't available yet ("+e.message+"). The chart below still works "
    +'off its built-in history through the page\\'s last build date.';
}});
fetch('data/weeks.json',{{cache:'no-store'}})
  .then(r=>r.ok?r.json():null)
  .then(w=>{{
    if(!w)return;
    if(w.weeks&&window.__lchMergeWeeks)window.__lchMergeWeeks(w.weeks);
    if(w.days&&window.__lchMergeDays)window.__lchMergeDays(w.days);
  }}).catch(()=>{{}});
</script>
<script>{CH_JS}</script>
</body>
</html>
"""

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(HTML)
    print(f"index.html built ({len(HTML):,} bytes) / "
          f"{CH_N:,} monthly / {CH_W:,} weekly / {CH_D:,} daily bars")

    js = CH_JS
    try:
        import esprima
        esprima.parseScript(js)
        i = HTML.index("<script>\nconst F=")
        esprima.parseScript(HTML[i + 8:HTML.index("</script>", i)])
        print("  JS syntax OK (esprima)")
    except Exception as e:                                        # noqa: BLE001
        raise SystemExit(f"JS syntax error: {e}")
