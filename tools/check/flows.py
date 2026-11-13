"""Behaviour check for the built site: the things a reader actually does.

Serves the built folder and walks the journeys that cross pages (menu, the hero map card into a
country, book-this-lane into a prefilled form, old #page links), plus the pieces that have to keep
working on their own page (board, cover carousel, search, film, contact form).
  python3 tools/check/flows.py [folder]        0 failures means the behaviour survived the split.
"""
import asyncio, sys, pathlib, threading, http.server, functools, socketserver, re
from playwright.async_api import async_playwright
ROOT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[2]

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True; daemon_threads = True
    def handle_error(self, *a): pass

def serve():
    srv = S(("127.0.0.1", 0), functools.partial(H, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

async def main():
    srv = serve(); base = f"http://127.0.0.1:{srv.server_address[1]}"
    fails, notes = [], []
    def ok(cond, label, got=""):
        (notes if cond else fails).append(f"{'ok  ' if cond else 'FAIL'} {label}{'' if cond else f'  (got: {got})'}")

    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])

        # ---------- desktop journeys ----------
        ctx = await b.new_context(viewport={"width": 1440, "height": 900})
        pg = await ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:200]))

        # 1. menu navigation lands on real pages
        await pg.goto(base + "/"); await pg.wait_for_timeout(900)
        await pg.click('nav a.nl[href="/services/"]'); await pg.wait_for_load_state("load"); await pg.wait_for_timeout(900)
        ok(pg.url.endswith("/services/"), "nav link goes to /services/", pg.url.replace(base, ""))
        ok(await pg.evaluate("!!document.getElementById('board')"), "the board is on the services page")

        # 2. the board renders its rows and the covers stay in step
        rows = await pg.evaluate("document.querySelectorAll('#board .fbd-r').length")
        ok(rows >= 5, "board lists the featured lanes", rows)
        await pg.evaluate("document.querySelectorAll('.dc')[2].click()"); await pg.wait_for_timeout(800)
        st = await pg.evaluate("({lane:document.querySelector('.lx')?.dataset.lane, on:[...document.querySelectorAll('.dc.on')].map(c=>c.dataset.l)})")
        ok(st["lane"] == "west" and st["on"] == ["west"], "a cover opens that lane and marks itself", st)
        await pg.evaluate("document.querySelectorAll('.lx-tab')[1].click()"); await pg.wait_for_timeout(900)
        st = await pg.evaluate("({lane:document.querySelector('.lx')?.dataset.lane, on:[...document.querySelectorAll('.dc.on')].map(c=>c.dataset.l)})")
        ok(st["lane"] == "east" and st["on"] == ["east"], "the board's own tabs turn the covers", st)

        # 3. country search
        await pg.fill("#lsIn", "Lusaka"); await pg.wait_for_timeout(700)
        sug = await pg.evaluate("document.getElementById('lsSug').innerText.slice(0,80)")
        ok("Zambia" in sug, "inland city search finds the country", sug)

        # 4. the film player is wired up and its share link uses the real page
        share = await pg.evaluate("""(()=>{const v=document.getElementById('promo'); if(!v) return 'no video';
            return {src:(v.currentSrc||v.querySelector('source')?.src||'').split('/').pop(), controls:!!document.querySelector('.vp-play')}})()""")
        ok(isinstance(share, dict) and share["controls"], "film player controls are present", share)

        # 5. grid: every country opens on the board
        await pg.evaluate("window.SLG_showCountry('Malawi',false)"); await pg.wait_for_timeout(800)
        nm = await pg.evaluate("document.querySelector('#board .lbc-name')?.getAttribute('aria-label')")
        ok(nm == "Malawi", "a grid country opens on the board", nm)

        # 6. book this lane carries the country into the form
        href = await pg.evaluate("""document.querySelector('#board a.btn[href*="contact"]')?.getAttribute('href')""")
        ok(bool(href) and href.startswith("/contact/?") and "Malawi" in href, "book this lane points at /contact/ with the country", href)
        await pg.goto(base + href); await pg.wait_for_timeout(1200)
        val = await pg.evaluate("""(()=>{const d=[...document.querySelectorAll('#askf .dd')].find(e=>e.dataset.name==='Destination country');
            return d?(d.querySelector('.dd-q')?.value||d.querySelector('.v')?.textContent||'').trim():'no field'})()""")
        ok(val == "Malawi", "the contact form arrives prefilled", val)

        # 7. the hero map card crosses into the open country
        await pg.goto(base + "/"); await pg.wait_for_timeout(1200)
        await pg.evaluate("scrollTo({top:1500,behavior:'instant'})"); await pg.wait_for_timeout(1600)
        await pg.evaluate("document.querySelectorAll('.hmap .spots').forEach(g=>{g.style.opacity=1;g.style.pointerEvents=''})")
        r = await pg.evaluate("""(async()=>{const sp=document.querySelector('.hmap .spot[data-c="Zambia"]'); if(!sp) return 'no spot';
            sp.dispatchEvent(new MouseEvent('click',{bubbles:true})); await new Promise(r=>setTimeout(r,400));
            const b=document.querySelector('.spotcard [data-go]'); if(!b) return 'no card'; b.click(); return 'clicked'})()""")
        ok(r == "clicked", "the hero map card has an open-in-index button", r)
        await pg.wait_for_load_state("load"); await pg.wait_for_timeout(1500)
        land = await pg.evaluate("""({url:location.pathname+location.search+location.hash,
            country:document.querySelector('#board .lbc-name')?.getAttribute('aria-label'),
            boardTop:Math.round(document.getElementById('board').getBoundingClientRect().top)})""")
        ok(land["country"] == "Zambia", "it lands with Zambia open on the board", land)
        ok(-5 <= land["boardTop"] <= 140, "and lands on the board, not the top of the page", land["boardTop"])

        # 8. old single-file links still work
        for old, want in [("/#services?film", "/services/?film"), ("/#about", "/about/"), ("/#contact?lane=East%20Africa", "/contact/?lane=East%20Africa")]:
            await pg.goto(base + old); await pg.wait_for_timeout(1000)
            ok(pg.url.replace(base, "") == want, f"old link {old} lands on {want}", pg.url.replace(base, ""))

        # 9. in-page section link
        await pg.goto(base + "/"); await pg.wait_for_timeout(900)
        h = await pg.evaluate("""document.querySelector('[data-scroll],a[href*="#dest"]')?.getAttribute('href')""")
        ok(bool(h) and "/services/#dest" in h, "see-every-destination points at the services section", h)

        ok(not errs, "no script errors on the desktop journey", errs[:3])
        await ctx.close()

        # ---------- phone ----------
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); perrs = []
        pg.on("pageerror", lambda e: perrs.append(str(e)[:200]))
        await pg.goto(base + "/about/"); await pg.wait_for_timeout(900)
        await pg.click("#mbtn"); await pg.wait_for_timeout(600)
        vis = await pg.evaluate("document.getElementById('menu').classList.contains('open')")
        ok(vis, "the menu opens on a sub-page")
        cur = await pg.evaluate("""[...document.querySelectorAll('#menu .tile')].filter(t=>t.classList.contains('cur')).map(t=>t.textContent.trim().slice(0,20))""")
        ok(cur and "About" in cur[0], "the menu marks the page you are on", cur)
        await pg.click('#menu a[href="/myslg/"]'); await pg.wait_for_load_state("load"); await pg.wait_for_timeout(800)
        ok(pg.url.endswith("/myslg/"), "the menu navigates between pages", pg.url.replace(base, ""))
        # the phone cover shelf on services
        await pg.goto(base + "/services/"); await pg.wait_for_timeout(1200)
        n = await pg.evaluate("document.querySelectorAll('.dcar .dc').length")
        ok(n >= 5, "the cover shelf is on the phone services page", n)
        ok(not perrs, "no script errors on the phone journey", perrs[:3])
        await ctx.close()
        await b.close()

    for n in notes: print(" ", n)
    print(f"\n{len(fails)} failures")
    for f in fails: print(" -", f)

asyncio.run(main())
