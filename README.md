# Special Logistics Group: shipslg.com

The public website of Special Logistics Group, LLC (SLG), an FMC-licensed NVOCC in Elkhart,
Indiana. It is a static site served by GitHub Pages from the `main` branch of this repo.

- **Live site:** https://shipslg.com (six pages: `/`, `/services/`, `/about/`, `/myslg/`,
  `/contact/`, `/privacy/`)
- **Old domain:** https://speciallogistics.net now forwards to shipslg.com (see
  [Domains](#domains-and-dns)). Email on @speciallogistics.net is unchanged.
- **Owner of record for the site:** Corbin Boucek, General Manager (corbin@speciallogistics.net),
  a collaborator on this repo. Built by Robertson Boucek, who is available as a consultant.
- **Weekly health check:** a scheduled Claude task checks the pages, redirects, deploys and
  mail/DNS records every Monday morning and sends a push notification (see the handoff).

If you only read one section, read [Making a change](#making-a-change).

---

## How the repo is laid out

```
src/site.html          the whole site in one file. THIS IS WHAT YOU EDIT.
tools/build/build.py   writes the published pages from it
tools/check/           site_check.py (SEO + responsive), flows.py (cross-page journeys)
tools/overlap/         run.py: headless check that nothing on the page covers anything else
tools/routes/          generators for the Home lane map routings
fonts/  media/  terms/ self-hosted fonts, the promo film, the HBL and NRA terms PDFs
drafts/                design ideas that were not shipped, kept for reference
CNAME                  shipslg.com (must match the DNS, see below)
```

Everything else in the repo root is **generated** by the build and is overwritten every time:
`index.html`, `services/`, `about/`, `myslg/`, `contact/`, `privacy/` (each an `index.html`),
`404.html`, `sitemap.xml`, `robots.txt` and `assets/`. Never edit those by hand.

## Making a change

You need Python 3 and git. The checks also need Google Chrome and Playwright
(`pip install playwright`).

```bash
git clone https://github.com/RPBOUCEK/slg-beta
cd slg-beta
# edit src/site.html, then:
python3 tools/build/build.py          # write the pages
python3 tools/check/site_check.py     # must say "0 problems"
python3 tools/check/flows.py          # must say "0 failures"
python3 tools/overlap/run.py 390,1440 # baseline is 14 known, harmless findings
git add -A && git commit -m "what changed" && git push
```

Pushing to `main` redeploys the live site in about a minute. GitHub shows the deploy under
the repo's **Actions** tab ("pages build and deployment").

**Small text edits** (a phone number, a sentence) can be made right on github.com: open
`src/site.html`, click the pencil, edit, commit. But the pages are only rebuilt by the build
script, so a web edit to `src/site.html` alone does **not** change the live site. Either run
the build afterwards, or ask Claude (or Robertson) to run it.

**Undoing a bad change:** every change is a commit. `git revert <commit>` and push, or ask
Claude to roll the site back to an earlier commit.

### House rules for the copy

- Brand colors are exact: grey `#282828`, yellow `#ffde59`. No pure black, no red.
- No hard shipment counts. "85+" is the phrasing for countries served.
- Avoid wording that dates the site or pigeonholes SLG by volume.
- No em dashes.
- Reviewer comments (family, colleagues) are applied only after the owner approves each one.

## Why one source, two shapes

`src/site.html` holds all six pages with `#page` routing. The build splits it into real pages
and sets `window.SLG_MP`, which switches the same script over to real URLs. The file still
works as-is in a browser, which is what the private **review copy** on claude.ai is published
from. Old links keep working: `/#services` and `/#contact?lane=East%20Africa` redirect to
`/services/` and `/contact/?lane=East%20Africa`.

What the build does:

- splits the pages, giving each its own title, description, canonical URL, share tags and
  structured data (plus a breadcrumb on every page but Home)
- pulls every embedded picture out into `assets/`, shrinks oversized ones (`TRIM` in the
  build script) and adds width, height and lazy loading
- pulls the stylesheet into one cached file, and the 450 KB of map geometry into a file only
  the Services page loads
- writes `sitemap.xml`, `robots.txt` and `404.html`

## Domains and DNS

Both domains' DNS is managed in **one Cloudflare account**, "Robertson@speciallogistics.net's
Account" (dash.cloudflare.com, sign in with GitHub). Corbin (corbin@speciallogistics.net) is
invited to it as a Super Administrator.

### shipslg.com (the website)

- Registered at **Cloudflare Registrar** (Nov 12, 2026; renews Nov 12, 2028).
- DNS records, all **DNS only** (grey cloud) so GitHub can issue the HTTPS certificate:
  - A `@`: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
  - AAAA `@`: 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153
  - CNAME `www` to `rpboucek.github.io`
  - TXT `_github-pages-challenge-rpboucek` (GitHub domain verification, leave it)
- The `CNAME` file in this repo and these records must agree. Deleting either takes the site
  offline. Enforce HTTPS is on in the repo's Settings > Pages.
- **Email on @shipslg.com** (Microsoft 365, added Nov 15, 2026), all DNS only:
  MX `@` 0 `shipslg-com.mail.protection.outlook.com`; TXT `@`
  `v=spf1 include:spf.protection.outlook.com -all` and `MS=ms83220173`; CNAME `autodiscover`
  to `autodiscover.outlook.com`; TXT `_dmarc` `v=DMARC1; p=none`. Nine people have an
  @shipslg.com alias on their existing mailbox (list in the handoff). Never delete these.

### speciallogistics.net (email, and the old website address)

- Registered at **Squarespace Domains** (renews Apr 8, 2027, auto-renew on).
- Since Nov 15, 2026 its nameservers point at Cloudflare (`ashton.ns.cloudflare.com`, `hadlee.ns.cloudflare.com`),
  so its DNS lives in the same Cloudflare account. Every record from Squarespace was copied
  over unchanged, including all email records:
  - MX `@` 0 `speciallogistics-net.mail.protection.outlook.com` (Microsoft 365)
  - TXT `@`: SPF `v=spf1 include:spf.protection.outlook.com include:squarespace-mail.com -all`,
    `MS=ms41776576`, Apple and Proton verification
  - CNAME `autodiscover`, `lyncdiscover`, `sip`; SRV `_sip._tls`, `_sipfederationtls._tcp`
  - DKIM CNAMEs `ctct1._domainkey`, `ctct2._domainkey` (Constant Contact),
    `squarespace._domainkey`; TXT `_dmarc` `v=DMARC1; p=none`
  - **Never delete or proxy (orange-cloud) any of these.** That breaks company email.
- Web traffic is forwarded by **Cloudflare Redirect Rules** (zone speciallogistics.net, Rules >
  Redirect Rules), all 301 permanent, for both `speciallogistics.net` and
  `www.speciallogistics.net`:

  | Old address | Goes to |
  |---|---|
  | `/about`, `/credentials` | https://shipslg.com/about/ |
  | `/services`, `/services2` | https://shipslg.com/services/ |
  | `/myslg` | https://shipslg.com/myslg/ |
  | `/contact`, `/contact-us` | https://shipslg.com/contact/ |
  | `/hbl` | https://shipslg.com/terms/hbl-terms.pdf |
  | anything else | https://shipslg.com/ |

  The `@` A records and `www` CNAME still name Squarespace's servers, but they are proxied
  (orange cloud), so visitors only ever reach Cloudflare's redirect. Business cards and old
  links that say speciallogistics.net keep working.
- The old Squarespace website still exists in the Squarespace account but no longer receives
  visitors. Cancel its site plan only once the redirect has been confirmed for a few weeks.
  Keep the **domain** registration at Squarespace (or transfer it to Cloudflare Registrar).

## Contact form

The Contact page posts to FormSubmit (`https://formsubmit.co/ajax/info@speciallogistics.net`),
which emails each message to info@speciallogistics.net. FormSubmit delivers nothing until the
first submission is activated from the email it sends to info@. If messages are not arriving,
check that inbox for the activation email.

## Where else things live

- **Handoff notes** for the people running the site: `claude/handoff-corbin.md` in the
  "SLG Site" project on claude.ai, plus the older working notes in that project
  (`next-session-start-here.md`, `open-issues.md`, `domain-plan.md`).
- **Review copy** with the comment system: a private claude.ai artifact owned by Robertson.
- **Brand files** (logos, stationery): the "SLG Site" project, `claude/brand/`.
