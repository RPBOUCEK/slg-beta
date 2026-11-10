# Special Logistics Group — beta site

Single-file static site. `index.html` is the whole thing: markup, styles, script,
the 2026 lane map (inline SVG) and the destination index are all embedded, as are
the two photographs and the WCAworld mark.

No build step. Open `index.html` locally, or serve the folder.

## Deploying
Served by GitHub Pages from the default branch. Pushing to `main` redeploys.

## Custom domain
Serves at https://beta.speciallogistics.net. The `CNAME` file holds that hostname;
the matching DNS record is a CNAME on `beta` pointing to `rpboucek.github.io`, held
at Squarespace with the rest of the speciallogistics.net zone. Both must agree:
deleting either one takes the site offline.
