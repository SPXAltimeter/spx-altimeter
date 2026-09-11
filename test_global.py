"""Verify the public English SPX Altimeter page: rendering, live-data fetch,
zoom/LOD, crash bands, and — importantly — that no Japanese text leaked
into anything a visitor actually sees.
"""
import sys
import io
import re
import pathlib
import http.server
import socketserver
import threading
import time
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
errs = []


def chk(c, m, x=""):
    print(("  OK   " if c else "  NG   ") + m + (("  " + x) if x else ""))
    if not c:
        errs.append(m)


HERE = pathlib.Path(__file__).parent

# file:// can't fetch data/*.json (CORS), and this page's live-data path is
# central to the product, so serve it over a real local HTTP server instead.
handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("127.0.0.1", 0), lambda *a: handler(*a, directory=str(HERE)))
port = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
time.sleep(0.3)
URL = f"http://127.0.0.1:{port}/index.html"

with sync_playwright() as p:
    br = p.chromium.launch(channel="msedge", headless=True)
    pg = br.new_context(viewport={"width": 1400, "height": 950}).new_page()
    logs = []
    pg.on("pageerror", lambda e: logs.append(str(e)))
    pg.on("console", lambda m: logs.append(m.text) if m.type == "error" else None)
    pg.goto(URL, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(1200)

    real_errs = [e for e in logs if "favicon" not in e]
    chk(not real_errs, "no JS errors", str(real_errs[:3]) if real_errs else "")

    print("\n■ Live data wiring (data/latest.json + data/weeks.json)")
    alt = pg.evaluate("()=>document.getElementById('alt').textContent")
    date = pg.evaluate("()=>document.getElementById('date').textContent")
    print(f"       altitude={alt}%  date={date}")
    chk(alt != "--", "hero altitude populated from data/latest.json", alt)
    stale = pg.evaluate("()=>getComputedStyle(document.getElementById('stale')).display")
    chk(stale == "none", "no stale-data banner (fresh fetch succeeded)")

    print("\n■ Text audit — no leaked Japanese anywhere a visitor reads")
    # textContent (not innerText) so collapsed <details> content is included —
    # a visitor who expands any section must not hit Japanese. <script>/<style>
    # are excluded: their Japanese is source-code comments, never rendered.
    text = pg.evaluate("""()=>{
      const c=document.body.cloneNode(true);
      c.querySelectorAll('script,style').forEach(e=>e.remove());
      return c.textContent;}""")
    cjk = sorted(set(re.findall(r"[぀-ヿ一-鿿]", text)))
    print(f"       CJK chars in page content (scripts/styles excluded): {cjk or 'none'}")
    chk(not cjk, "zero Japanese characters in visible/expandable content", str(cjk[:20]))
    title = pg.title()
    chk(title == "SPX Altimeter", "page title", title)

    print("\n■ Detail sections")
    n_sections = pg.evaluate("()=>document.querySelectorAll('details.det').length")
    chk(n_sections == 6, "6 explainer sections rendered", f"{n_sections}")
    chk("30" in text and "Reality Check" in text, "honest-findings section present")
    chk("effective sample size" in text.lower(), "AR(1) caveat present")

    print("\n■ Chart: zoom / LOD / crash bands")
    pg.locator("#lcv").scroll_into_view_if_needed()
    pg.wait_for_timeout(300)
    rng0 = pg.evaluate("()=>document.getElementById('lrng').textContent")
    per0 = pg.evaluate("()=>document.getElementById('lper').textContent")
    print(f"       initial: {rng0} [{per0}]")
    chk("1932-06" in rng0, "default view is 1932- valid range", rng0)
    chk(per0 == "Monthly", "default granularity label reads 'Monthly'", per0)

    bb = pg.locator("#lcv").bounding_box()
    cx, cy = bb["x"] + bb["width"] * 0.85, bb["y"] + bb["height"] * 0.35
    pg.mouse.move(cx, cy)
    for _ in range(30):
        pg.mouse.wheel(0, -120)
        pg.wait_for_timeout(25)
    pg.wait_for_timeout(400)
    per1 = pg.evaluate("()=>document.getElementById('lper').textContent")
    rng1 = pg.evaluate("()=>document.getElementById('lrng').textContent")
    print(f"       zoomed: {rng1} [{per1}]")
    chk(per1 in ("Weekly", "Daily"), "zoom switches to a finer granularity", per1)

    pg.locator("button#lbcr").click()
    pg.wait_for_timeout(250)
    pg.locator("button#lbcr2").click()
    pg.wait_for_timeout(300)
    bands = pg.evaluate("()=>document.querySelectorAll('#lcv rect.lcrash,#lcv rect.lcrash2').length")
    chk(bands > 0, "crash/correction bands render on click", f"{bands} rects")

    print("\n■ Tooltip (hover)")
    pg.locator("#lrst").click()
    pg.wait_for_timeout(300)
    pg.mouse.move(bb["x"] + bb["width"] * 0.5, bb["y"] + bb["height"] * 0.3)
    pg.wait_for_timeout(250)
    tip = pg.evaluate("()=>document.getElementById('ltip').textContent")
    print(f"       {tip[:70]}")
    chk("High" in tip and "Close" in tip, "tooltip labels are English", tip[:60])

    pg.locator(".wrap").screenshot(path=str(HERE / "shot_global_full.png"))
    pg.close()
    br.close()

httpd.shutdown()
print("=" * 78)
print("ALL PASS" if not errs else f"{len(errs)} FAILED: " + " / ".join(errs))
sys.exit(1 if errs else 0)
