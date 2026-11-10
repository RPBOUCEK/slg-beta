# Special Logistics Group — beta site

Single-file static site. `index.html` is the whole thing: markup, styles, script,
the 2026 lane map (inline SVG) and the destination index are all embedded, as are
the two photographs and the WCAworld mark.

No build step. Open `index.html` locally, or serve the folder.

## Deploying
Served by GitHub Pages from the default branch. Pushing to `main` redeploys.

## Custom domain
None yet: the site serves on its github.io URL. To move it to
beta.speciallogistics.net, add a `CNAME` file holding that hostname AND a matching
DNS record at the registrar. Adding the file without the DNS record takes the site
offline, so do both together.
