"""Build the published site from the single-file source.

  src/site.html   the whole site in one file with #page routing. Edit this. It is also what the
                  review artifact is published from (see claude/beta-site-handoff.md).
  python3 tools/build/build.py
                  writes the real pages GitHub Pages serves from the repo root:
                    index.html, services/, about/, myslg/, contact/, privacy/ (each index.html),
                    404.html, sitemap.xml, robots.txt and assets/ (shared CSS, images, map data).

Each built page holds only its own section, its own title, description, canonical URL, share tags and
structured data, and sets window.SLG_MP so the script uses real URLs instead of #page.
Never edit the built files by hand: they are overwritten on every build.
"""
import re, hashlib, base64, json, pathlib, datetime, io, shutil, sys
REPO=pathlib.Path(__file__).resolve().parents[2]; SRC=REPO/"src"/"site.html"
ROOT=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else REPO   # optional output folder (default: the repo root)
ASSETS=ROOT/"assets"
SITE="https://shipslg.com"
PAGES={ # key: (path, title, description, breadcrumb name)
 "home":("/","Special Logistics Group | Freight to the world’s hardest-to-reach places",
   "FMC-licensed NVOCC in Elkhart, Indiana. Humanitarian and commercial freight from U.S. ports to 85+ countries, all the way to final delivery.","Home"),
 "services":("/services/","Ocean Freight, Trucking and Export Services | Special Logistics Group",
   "Everything SLG handles as a licensed NVOCC: drayage, warehousing, bonded cargo, export clearance, ocean bookings, insurance and destination documents such as ECTN and CNCA.","Services"),
 "about":("/about/","About Us | Special Logistics Group, Elkhart, Indiana",
   "Special Logistics Group: founded by a lifelong mariner, with thousands of humanitarian shipments to 85+ countries for more than 100 NGOs, charities and ministries.","About Us"),
 "myslg":("/myslg/","mySLG Shipment Tracking | Special Logistics Group",
   "Track every Special Logistics Group shipment in mySLG, our online tracking portal.","mySLG"),
 "contact":("/contact/","Contact | Talk to an Expert at Special Logistics Group",
   "Talk to an expert at Special Logistics Group. Book a time, call +1 574 326 3152 or email info@speciallogistics.net.","Contact"),
 "privacy":("/privacy/","Privacy | Special Logistics Group",
   "How Special Logistics Group handles the information you send us. We do not sell personal data.","Privacy"),
}
EXT={"image/jpeg":"jpg","image/png":"png","image/webp":"webp","image/gif":"gif"}
# Pictures that are bigger than they are ever drawn. Keyed by the sha1 of the bytes in src/site.html,
# so changing a picture drops it back to "leave it alone" and the build says so.
#   sha1 prefix -> (widest it is ever drawn at 2x, jpeg quality or None to keep the original)
TRIM={
 "ab611b33e5":(2560,82),   # home photo band: drawn at most 1920 wide, 300 tall
 "3fb44db826":(2560,82),   # services photo band
 "001e1a8de1":(300,None),  # WCAworld mark: drawn 132 wide
}
LEAVE={"ca3753c5cb","03e63f84d0","744b1c9803","dc90673352","16582ca51e","87d9f41b55","e02785a67a"}  # already no bigger than they need to be
def esc(t): return t.replace("&","&amp;").replace('"',"&quot;").replace("<","&lt;")

def trim(raw, mime, key):
    """Shrink a picture to the size it is actually drawn at. Returns the bytes to publish."""
    if key not in TRIM: return raw
    maxw, q = TRIM[key]
    try:
        from PIL import Image
    except ImportError:
        return raw
    im = Image.open(io.BytesIO(raw))
    if im.width > maxw: im = im.resize((maxw, round(im.height*maxw/im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if mime == "image/jpeg": im.convert("RGB").save(buf, "JPEG", quality=q or 82, optimize=True, progressive=True)
    else: im.save(buf, "PNG", optimize=True)
    out = buf.getvalue()
    return out if len(out) < len(raw) else raw

def main():
    s=SRC.read_text(encoding="utf-8")
    if ASSETS.exists(): shutil.rmtree(ASSETS)
    ASSETS.mkdir()
    sizes={}
    def asset(m):
        mime,b64=m.group(1),m.group(2); raw=base64.b64decode(b64)
        key=hashlib.sha1(raw).hexdigest()[:10]
        out=trim(raw,mime,key)
        if key not in TRIM and key not in LEAVE and len(raw)>120_000:
            print(f"  note: {key} is {len(raw)//1024}KB and is not in TRIM or LEAVE in tools/build/build.py; published as is")
        name=f"img-{key}.{EXT[mime]}"; (ASSETS/name).write_bytes(out)
        if len(out)!=len(raw): print(f"  {name}: {len(raw)//1024}KB -> {len(out)//1024}KB")
        try:
            from PIL import Image; sizes[name]=Image.open(io.BytesIO(out)).size
        except Exception: pass
        return "/assets/"+name
    DATAURI=re.compile(r"data:(image/(?:jpeg|png|webp|gif));base64,([A-Za-z0-9+/=]{2000,})")   # small inline icons stay inline
    s=DATAURI.sub(asset,s)
    # images: intrinsic size (no layout shift) and lazy loading below the fold
    def img(m):
        tag=m.group(0); src=re.search(r'src="/assets/([^"]+)"',tag)
        if src and src.group(1) in sizes and " width=" not in tag:
            w,h=sizes[src.group(1)]; tag=tag[:-1]+f' width="{w}" height="{h}">'
        if " loading=" not in tag: tag=tag[:-1]+' loading="lazy" decoding="async">'
        return tag
    s=re.sub(r"<img\b[^>]*>",img,s)
    # shared stylesheet
    m=max(re.finditer(r"<style>(.*?)</style>",s,re.S),key=lambda x:len(x.group(1)))
    css=m.group(1).replace("url(fonts/","url(/fonts/").replace("url(media/","url(/media/")
    cssname=f"site-{hashlib.sha1(css.encode()).hexdigest()[:10]}.css"; (ASSETS/cssname).write_text(css,encoding="utf-8")
    s=s[:m.start()]+f'<link rel="preload" href="/fonts/Montserrat-Bold.woff2" as="font" type="font/woff2" crossorigin>\n<link rel="preload" href="/fonts/Montserrat-Regular.woff2" as="font" type="font/woff2" crossorigin>\n<link rel="stylesheet" href="/assets/{cssname}">'+s[m.end():]
    # map geometry (lane maps and country outlines) is only needed on Services
    g=re.search(r"<script>\s*window\.SLG_LANEMAPS=.*?</script>",s,re.S); assert g and "SLG_OUTLINES" in g.group(0)
    geo=re.sub(r"^<script>|</script>$","",g.group(0)); geoname=f"geo-{hashlib.sha1(geo.encode()).hexdigest()[:10]}.js"; (ASSETS/geoname).write_text(geo,encoding="utf-8")
    s=s[:g.start()]+"<!--GEO-->"+s[g.end():]
    # links and media paths
    def href(m):
        page,q=m.group(1),m.group(2) or ""; return 'href="'+PAGES[page][0]+q+'"'
    s=re.sub(r'href="/services/"( data-nav)? data-scroll="([\w-]+)"',r'href="/services/#\2"\1',
             re.sub(r'href="#(home|services|about|contact|myslg|privacy)(\?[^"]*)?"',href,s))
    s=s.replace('"media/','"/media/')
    # split the pages
    starts=[(mm.start(),mm.group(1)) for mm in re.finditer(r'<div class="page" id="p-([a-z]+)">',s)]
    foot=s.index("<footer"); assert [k for _,k in starts] and set(k for _,k in starts)==set(PAGES), starts
    secs={}
    for i,(st,k) in enumerate(starts):
        en=starts[i+1][0] if i+1<len(starts) else foot; sec=s[st:en]
        assert sec.count("<div")==sec.count("</div>"),(k,sec.count("<div"),sec.count("</div>"))
        secs[k]=sec
    before,after=s[:starts[0][0]],s[foot:]
    hs,he=before.index("<head>")+6,before.index("</head>")
    head=before[hs:he]
    org=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',head,re.S).group(1))
    today=datetime.date.today().isoformat()
    for k,(path,title,desc,crumb) in PAGES.items():
        url=SITE+path; h=head
        h=re.sub(r"<title>.*?</title>",f"<title>{esc(title)}</title>",h,flags=re.S)
        h=re.sub(r'(<meta name="description" content=")[^"]*"',lambda m:m.group(1)+esc(desc)+'"',h)
        h=re.sub(r'(<link rel="canonical" href=")[^"]*"',lambda m:m.group(1)+url+'"',h)
        h=re.sub(r'(<meta property="og:url" content=")[^"]*"',lambda m:m.group(1)+url+'"',h)
        if k!="home":
            h=re.sub(r'(<meta property="og:title" content=")[^"]*"',lambda m:m.group(1)+esc(title)+'"',h)
            h=re.sub(r'(<meta name="twitter:title" content=")[^"]*"',lambda m:m.group(1)+esc(title)+'"',h)
        h=re.sub(r'(<meta property="og:description" content=")[^"]*"',lambda m:m.group(1)+esc(desc)+'"',h)
        h=re.sub(r'(<meta name="twitter:description" content=")[^"]*"',lambda m:m.group(1)+esc(desc)+'"',h)
        graph=list(org["@graph"])+[{"@type":"ContactPage" if k=="contact" else "AboutPage" if k=="about" else "WebPage","@id":url+"#page","url":url,"name":title,"description":desc,
               "isPartOf":{"@id":SITE+"/#site"},"about":{"@id":SITE+"/#org"},"inLanguage":"en-US"}]
        if k!="home":
            graph.append({"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},{"@type":"ListItem","position":2,"name":crumb,"item":url}]})
        h=re.sub(r'<script type="application/ld\+json">.*?</script>',lambda m:'<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@graph":graph},ensure_ascii=False,separators=(",",":"))+"</script>",h,flags=re.S)
        boot=f'<script>window.SLG_MP={{page:"{k}"}};'
        if k=="home":   # old single-file links such as /#services or /#services?film go to the real page
            boot+='(function(){var m=location.hash.match(/^#(services|about|contact|myslg|privacy)(\\?.*)?$/);if(m)location.replace("/"+m[1]+"/"+(m[2]||""));})();'
        h=h+boot+"</script>\n"
        sec=secs[k].replace('<div class="page" id="p-'+k+'">','<div class="page on" id="p-'+k+'">',1)
        body=after.replace("<!--GEO-->",f'<script src="/assets/{geoname}"></script>' if k=="services" else "")
        out=before[:hs]+h+before[he:]+sec+body
        dest=ROOT/("index.html" if k=="home" else path.strip("/")+"/index.html"); dest.parent.mkdir(exist_ok=True)
        dest.write_text(out,encoding="utf-8"); print(f"{str(dest.relative_to(ROOT)):24} {len(out)//1024:5} KB")
    (ROOT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+
        "".join(f"  <url><loc>{SITE+p[0]}</loc><lastmod>{today}</lastmod></url>\n" for p in PAGES.values())+"</urlset>\n")
    (ROOT/"robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    fav=re.search(r'<link rel="icon"[^>]*>',head).group(0)
    (ROOT/"404.html").write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page not found | Special Logistics Group</title><meta name="robots" content="noindex">
{fav}
<link rel="stylesheet" href="/assets/{cssname}">
<style>.nf{{min-height:100svh;display:flex;flex-direction:column;justify-content:center;gap:22px;padding-block:80px}}.nf h1{{font-size:clamp(40px,7vw,84px);line-height:1.02;letter-spacing:-.03em}}.nf h1 em{{font-style:normal;background:linear-gradient(var(--b),var(--b)) left 100%/100% .13em no-repeat}}.nf p{{max-width:52ch;font-size:18px;color:var(--mut)}}.nf nav{{position:static;display:flex;justify-content:flex-start;flex-wrap:wrap;gap:10px;padding:0;background:none;border:0;height:auto;backdrop-filter:none}}</style>
</head><body><main class="nf wrap"><p class="lbl">Error 404</p><h1>That page is <em>off the map</em>.</h1>
<p>The address may have changed when we moved to shipslg.com. Everything is still here:</p>
<nav aria-label="Pages"><a class="btn" href="/">Home</a><a class="btn o" href="/services/">Services</a><a class="btn o" href="/about/">About Us</a><a class="btn o" href="/myslg/">mySLG</a><a class="btn o" href="/contact/">Talk to an expert</a></nav>
</main></body></html>
''',encoding="utf-8")
    print("assets:",", ".join(f"{p.name} {p.stat().st_size//1024}KB" for p in sorted(ASSETS.iterdir())))
main()
