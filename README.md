# Special Logistics Group — shipslg.com

The site is six real pages, built from one source file.

```
src/site.html          the whole site in one file. THIS IS WHAT YOU EDIT.
tools/build/build.py   writes the published pages from it
```

Everything in the repo root except `src/`, `tools/`, `drafts/`, `fonts/`, `media/`, `terms/`,
`CNAME` and this README is **generated**: `index.html`, `services/`, `about/`, `myslg/`,
`contact/`, `privacy/` (each an `index.html`), plus `404.html`, `sitemap.xml`, `robots.txt`
and `assets/`. Never edit those by hand, they are overwritten on the next build.

## Making a change

```bash
# edit src/site.html, then
python3 tools/build/build.py          # write the pages
python3 tools/check/site_check.py     # SEO + responsive, must say 0 problems
python3 tools/check/flows.py          # the journeys still work, must say 0 failures
python3 tools/overlap/run.py 390,1440 # nothing covering anything else
git add -A && git commit && git push  # pushing to main redeploys
```

## Why one source, two shapes

`src/site.html` holds all six pages with `#page` routing. The build splits it into real pages
and sets `window.SLG_MP`, which switches the same script over to real URLs. The file still
works as-is in a browser, which is what the **review artifact** is published from (it only
passes plain `#name` hashes, so it needs the single-file shape). See
`claude/beta-site-handoff.md` for how to publish that.

Old links keep working: `/#services` and `/#contact?lane=East%20Africa` redirect to
`/services/` and `/contact/?lane=East%20Africa`.

## What the build does

- splits the pages, giving each its own title, description, canonical URL, share tags and
  structured data (plus a breadcrumb on everything but the home page)
- pulls every embedded picture out into `assets/` as a real file, shrinks the ones that are
  bigger than they are ever drawn (see `TRIM` in the build script), and adds width, height
  and lazy loading
- pulls the stylesheet out to one cached file, and the 450 KB of map geometry out to a file
  only the Services page loads
- writes `sitemap.xml`, `robots.txt` and a `404.html`

A page went from 3.1 MB to 109–182 KB of HTML.

## Custom domain

Serves at https://shipslg.com (www.shipslg.com redirects to it). The `CNAME` file holds that
hostname. The domain is registered at Cloudflare Registrar and its DNS is on Cloudflare: four
A and four AAAA records on `@` pointing to GitHub Pages, and a CNAME on `www` pointing to
`rpboucek.github.io`, all set to DNS only (grey cloud). The domain is verified for the
RPBOUCEK account under GitHub Settings > Pages. The `CNAME` file and the DNS records must
agree: deleting either one takes the site offline.

Before Nov 12, 2026 the site served at beta.speciallogistics.net, which no longer serves from
this repo.
