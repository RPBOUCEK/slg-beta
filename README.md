# Special Logistics Group — beta site

Single-file static site. `index.html` is the whole thing: markup, styles, script,
the 2026 lane map (inline SVG) and the destination index are all embedded, as are
the two photographs and the WCAworld mark.

No build step. Open `index.html` locally, or serve the folder.

## Deploying
Served by GitHub Pages from the default branch. Pushing to `main` redeploys.

## Custom domain
Serves at https://shipslg.com (www.shipslg.com redirects to it). The `CNAME` file
holds that hostname. The domain is registered at Cloudflare Registrar and its DNS is
on Cloudflare: four A and four AAAA records on `@` pointing to GitHub Pages, and a
CNAME on `www` pointing to `rpboucek.github.io`, all set to DNS only (grey cloud).
The domain is verified for the RPBOUCEK account under GitHub Settings > Pages.
The `CNAME` file and the DNS records must agree: deleting either one takes the site
offline.

Before Nov 12, 2026 the site served at beta.speciallogistics.net, which no longer
serves from this repo.
