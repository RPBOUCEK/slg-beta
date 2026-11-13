"""Publishing check for the built site.

Serves a folder (default: the repo root) on a local port and loads every real page at phone, tablet and
desktop sizes. Reports script errors, failed requests, pages that scroll sideways, broken internal links,
and SEO basics (one h1, title and description lengths, canonical, share tags, structured data, image alt text).
  python3 tools/check/site_check.py [folder]        0 problems means ready to publish.
"""
import asyncio, sys, re, json, pathlib, threading, http.server, functools, socketserver
from playwright.async_api import async_playwright
ROOT=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parents[2]
PAGES=["/","/services/","/about/","/myslg/","/contact/","/privacy/"]
VPS=[(320,568,True),(390,844,True),(768,1024,True),(1024,768,False),(1440,900,False),(1920,1080,False)]
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer):
    allow_reuse_address=True; daemon_threads=True
    def handle_error(self,*a): pass   # the browser dropping a connection mid-file is not a site problem
def serve():
    srv=S(("127.0.0.1",0),functools.partial(H,directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever,daemon=True).start(); return srv
SEO="""(()=>{const q=s=>document.querySelector(s), c=(s)=>q(s)?q(s).getAttribute('content'):null;
 const vis=e=>e.offsetParent!==null;
 return {title:document.title, desc:c('meta[name=description]'), canon:q('link[rel=canonical]')?.href, ogurl:c('meta[property="og:url"]'), ogimg:c('meta[property="og:image"]'), ogtitle:c('meta[property="og:title"]'),
  h1:[...document.querySelectorAll('h1')].filter(vis).map(h=>h.textContent.replace(/\\s+/g,' ').trim()), lang:document.documentElement.lang,
  ld:[...document.querySelectorAll('script[type="application/ld+json"]')].map(s=>{try{return JSON.parse(s.textContent)['@graph'].map(n=>[].concat(n['@type']).join('+'))}catch(e){return 'BAD JSON'}}),
  noalt:[...document.images].filter(i=>!i.hasAttribute('alt')).map(i=>i.src.slice(-30)),
  links:[...new Set([...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')))],
  pages:document.querySelectorAll('.page').length, emptyLinks:[...document.querySelectorAll('a[href]')].filter(a=>vis(a)&&!a.textContent.trim()&&!a.getAttribute('aria-label')&&!a.querySelector('img[alt],svg[aria-label]')).map(a=>a.getAttribute('href'))}})()"""
async def main():
    srv=serve(); base=f"http://127.0.0.1:{srv.server_address[1]}"; probs=[]; seo={}
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--no-sandbox"])
        for (w,h,mob) in VPS:
            ctx=await b.new_context(viewport={"width":w,"height":h},is_mobile=mob,has_touch=mob)
            for path in PAGES:
                pg=await ctx.new_page(); tag=f"{w}px {path}"
                pg.on("pageerror",lambda e,t=tag:probs.append(f"{t}: script error: {(getattr(e,'stack',None) or str(e)).replace(chr(10),' | ')[:330]}"))
                pg.on("console",lambda m,t=tag:probs.append(f"{t}: console error: {m.text[:160]}") if m.type=="error" else None)
                pg.on("response",lambda r,t=tag:probs.append(f"{t}: HTTP {r.status} {r.url.replace(base,'')[:90]}") if r.status>=400 else None)
                await pg.goto(base+path); await pg.wait_for_timeout(1200)
                H=await pg.evaluate("document.documentElement.scrollHeight")
                for y in range(0,H,h):
                    await pg.evaluate(f"scrollTo({{top:{y},behavior:'instant'}})"); await pg.wait_for_timeout(120)
                ov=await pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
                if ov>1: probs.append(f"{tag}: page scrolls sideways by {ov}px")
                wide=await pg.evaluate("[...document.querySelectorAll('.page.on *, footer *, nav *')].filter(e=>{const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>0&&r.right>innerWidth+2&&cs.position!=='fixed'&&!e.closest('.marq,.dcar-track,.hmap,.filters,.lx-tabs,[hidden]')&&cs.visibility!=='hidden'}).slice(0,3).map(e=>e.tagName+'.'+e.className+' '+(e.innerText||'').slice(0,30))")
                if wide and ov>1: probs.append(f"{tag}: runs past the right edge: {wide}")
                if (w,h)==(1440,900): seo[path]=await pg.evaluate(SEO)
                await pg.close()
            await ctx.close()
        # 404 and legacy links
        ctx=await b.new_context(viewport={"width":1280,"height":800}); pg=await ctx.new_page()
        await pg.goto(base+"/#services?film"); await pg.wait_for_timeout(1200)
        if not pg.url.endswith("/services/?film"): probs.append(f"old link /#services?film did not go to /services/?film (got {pg.url.replace(base,'')})")
        await pg.goto(base+"/#contact?lane=East%20Africa"); await pg.wait_for_timeout(1200)
        if "/contact/?lane=" not in pg.url: probs.append("old link /#contact?lane= did not go to /contact/")
        await b.close()
    # link targets and SEO rules
    allpaths=set()
    for path,d in seo.items():
        t,ds=d['title'],d['desc'] or ''
        if not (15<=len(t)<=75): probs.append(f"{path}: title length {len(t)}")
        if not (70<=len(ds)<=175): probs.append(f"{path}: description length {len(ds)}")
        if d['canon']!="https://shipslg.com"+path: probs.append(f"{path}: canonical is {d['canon']}")
        if d['ogurl']!="https://shipslg.com"+path: probs.append(f"{path}: og:url is {d['ogurl']}")
        if not d['ogimg'] or not d['ogtitle']: probs.append(f"{path}: missing share tags")
        if len(d['h1'])!=1: probs.append(f"{path}: {len(d['h1'])} visible h1 headings {d['h1']}")
        if d['lang']!="en": probs.append(f"{path}: html lang")
        if d['ld']=='BAD JSON' or not d['ld'] or 'BAD JSON' in d['ld']: probs.append(f"{path}: structured data")
        if d['noalt']: probs.append(f"{path}: images without alt text {d['noalt']}")
        if d['pages']!=1: probs.append(f"{path}: {d['pages']} page sections in the file")
        if d['emptyLinks']: probs.append(f"{path}: links with no text {d['emptyLinks']}")
        for l in d['links']:
            if l.startswith("#") and re.match(r"#(home|services|about|contact|myslg|privacy)\b",l): probs.append(f"{path}: old #page link {l}")
            if l.startswith("/"): allpaths.add(l.split("#")[0].split("?")[0])
    for l in sorted(allpaths):
        f=ROOT/l.lstrip("/"); f=f/"index.html" if l.endswith("/") or l=="" else f
        if not f.exists(): probs.append(f"internal link to missing file: {l}")
    titles=[d['title'] for d in seo.values()]; descs=[d['desc'] for d in seo.values()]
    if len(set(titles))!=len(titles): probs.append("duplicate page titles")
    if len(set(descs))!=len(descs): probs.append("duplicate descriptions")
    sm=(ROOT/"sitemap.xml").read_text() if (ROOT/"sitemap.xml").exists() else ""
    for path in PAGES:
        if f"<loc>https://shipslg.com{path}</loc>" not in sm: probs.append(f"sitemap missing {path}")
    for f in ["robots.txt","404.html","CNAME",".nojekyll"]:
        if not (ROOT/f).exists() and ROOT.name!="site": probs.append(f"missing {f}")
    for path,d in seo.items(): print(f"{path:11} h1={d['h1']} | title({len(d['title'])}) {d['title']} | desc({len(d['desc'] or '')}) | ld={d['ld']}")
    seen=[]; [seen.append(x) for x in probs if x not in seen]
    print(len(seen),"problems"); [print(" -",x) for x in seen[:60]]
asyncio.run(main())
