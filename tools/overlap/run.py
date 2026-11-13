"""Overlap check for the SLG site.

Loads every page in headless Chromium at phone, tablet and desktop sizes, with the menu open, in
country views and in the search answer, and reports any text or control covered by another element,
text sitting on text, or a page scrolling sideways.

The built pages (real URLs, served from the repo root over a local port) are what visitors get, so
they are what is checked. Review mode only exists in the single file the review artifact is
published from, so those passes load src/site.html with #page routing instead.

  python3 tools/overlap/run.py            all sizes
  python3 tools/overlap/run.py 390,1440   some widths
Needs Python Playwright with Chromium.  0 findings means clean.
"""
import asyncio, json, sys, pathlib, threading, http.server, functools, socketserver
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parent.parent
from playwright.async_api import async_playwright
SRC=(ROOT/"src"/"site.html").as_uri()
CHECK=(HERE/'check.js').read_text(); MOCK=(HERE/'mock.js').read_text()
VPS=[(440,956,True),(844,390,True),(932,430,True),(320,568,True),(360,780,True),(375,667,True),(390,844,True),(414,896,True),(430,932,True),(768,1024,True),(1024,768,False),(1280,800,False),(1440,900,False)]
if len(sys.argv)>1: VPS=[v for v in VPS if str(v[0]) in sys.argv[1].split(',')]
PAGES=["home","about","services","myslg","contact"]
URL={"home":"/","about":"/about/","services":"/services/","myslg":"/myslg/","contact":"/contact/","privacy":"/privacy/"}

class _H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
class _S(socketserver.ThreadingTCPServer):
    allow_reuse_address=True; daemon_threads=True
    def handle_error(self,*a): pass
def serve():
    srv=_S(("127.0.0.1",0),functools.partial(_H,directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever,daemon=True).start(); return srv

async def scan(pg,label,results,full=True):
    vh=await pg.evaluate("innerHeight"); H=await pg.evaluate("document.documentElement.scrollHeight")
    ys=list(range(0,max(1,H-vh),int(vh*.8)))+[max(0,H-vh)] if full else [await pg.evaluate("scrollY")]
    for y in ys:
        if full: await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(140)
        for f in await pg.evaluate(CHECK,{}):
            f['at']=label; results.append(f)

async def main():
    res=[]; srv=serve(); web=f"http://127.0.0.1:{srv.server_address[1]}"
    async def show(pg,page,review):
        """Open a page: a real navigation on the built site, a hash change in the single file."""
        if review: await pg.evaluate(f"location.hash='{page}'"); await pg.wait_for_timeout(500)
        else: await pg.goto(web+URL[page]); await pg.wait_for_timeout(700)
        await pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--no-sandbox"])
        for (w,h,mob) in VPS:
            for theme in ["light"]:  # dark mode retired Nov 11
                for review in ([False,True] if w in (320,390,768,1440) and theme=="light" else [False]):
                    ctx=await b.new_context(viewport={"width":w,"height":h},is_mobile=mob,has_touch=mob,device_scale_factor=1)
                    if review: await ctx.add_init_script("window.__ROLE='admin';"+MOCK)
                    await ctx.add_init_script(f"try{{localStorage.setItem('slg-theme','{theme}')}}catch(e){{}};try{{localStorage.setItem('slg-guide-seen','1')}}catch(e){{}}")
                    await ctx.route("**/fonts.g*/**",lambda r:r.abort())
                    pg=await ctx.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
                    await pg.goto(SRC+"#home" if review else web+"/"); await pg.wait_for_timeout(900)
                    tag=f"{w}x{h} {theme}{' review' if review else ''}"
                    if review:
                        # close guide if open, turn feedback mode on
                        await pg.evaluate("for(const b of document.querySelectorAll('button')){ if(/start reviewing/i.test(b.textContent)){b.click();break;} }")
                        await pg.wait_for_timeout(400)
                    for page in PAGES:
                        await show(pg,page,review)
                        await scan(pg,f"{tag} #{page}",res)
                    if not review:
                        await show(pg,"home",review); await pg.evaluate("window.scrollTo(0,0)")
                        opened=await pg.evaluate("(()=>{const b=[...document.querySelectorAll('button')].find(x=>/^\\s*menu\\s*$/i.test(x.textContent)); if(b){b.click();return true} return false})()")
                        await pg.wait_for_timeout(600); await scan(pg,f"{tag} menu-open({opened})",res,full=False)
                        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)
                        await show(pg,"services",review)
                        for c in ["Zambia","St. Vincent & the Grenadines","Central African Republic","DR Congo","Mongolia"]:
                            await pg.evaluate(f"window.slgBoard.country({json.dumps(c)})"); await pg.wait_for_timeout(1500)
                            await pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
                            y0=await pg.evaluate("document.getElementById('board').getBoundingClientRect().top+scrollY-80")
                            bh=await pg.evaluate("document.getElementById('board').offsetHeight"); vh=h
                            for y in range(int(y0),int(y0+bh),int(vh*.7)):
                                await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(120); await scan(pg,f"{tag} country {c}",res,full=False)
                        await pg.evaluate("(()=>{const i=document.getElementById('lsIn'); i.value='Lilongwe'; i.dispatchEvent(new Event('input')); document.getElementById('lsGo').click(); document.getElementById('lsIn').scrollIntoView({block:'center'});})()")
                        await pg.wait_for_timeout(500); await scan(pg,f"{tag} search answer",res,full=False)
                    else:
                        await show(pg,"services",review)
                        await pg.evaluate("(()=>{const b=[...document.querySelectorAll('button')].find(x=>/^\\s*feedback\\s*$/i.test(x.textContent)); b&&b.click();})()"); await pg.wait_for_timeout(500)
                        await scan(pg,f"{tag} feedback-mode #services",res)
                        await pg.evaluate("(()=>{const p=document.querySelector('.fbPin'); p&&p.click();})()"); await pg.wait_for_timeout(600)
                        await scan(pg,f"{tag} drawer-open",res,full=False)
                    if errs: res.append({'type':'js-error','at':tag,'e':errs[:2]})
                    await ctx.close()
        await b.close()
    json.dump(res,open(HERE/'results.json','w'),indent=0)
    print(len(res),"findings")
    seen=set()
    for f in res:
        k=(f['type'],f.get('item') or f.get('a'),f.get('by') or f.get('b'))
        if k in seen: continue
        seen.add(k); print(f['at'],'|',json.dumps({x:f[x] for x in f if x!='at'})[:330])
asyncio.run(main())
