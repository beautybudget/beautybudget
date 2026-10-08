#!/usr/bin/env python3
"""Generate index.html from products.json (static HTML, no JavaScript).

Add a product: put a square 600x600 JPG in img/, add an entry at the TOP
of "products" in products.json (with "added" as YYYY-MM-DD), update
"site.last_checked", then run:  python3 build.py
Products are sorted newest first by "added" date; products with the same
date keep their order from products.json (top = newest).
"""
import json
import re
from datetime import date
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "products.json").read_text(encoding="utf-8"))
site = data["site"]
products = sorted(data["products"], key=lambda p: p["added"], reverse=True)

REQUIRED = ("id", "added", "name", "price", "shop", "fact", "image", "url")
for p in products:
    missing = [k for k in REQUIRED if not p.get(k)]
    if missing:
        raise SystemExit(f"Product {p.get('id', '?')} mist velden: {missing}")
    if not (HERE / p["image"]).exists():
        raise SystemExit(f"Afbeelding niet gevonden: {p['image']}")

e = lambda s: escape(str(s), quote=True)
base = site.get("site_url", "").rstrip("/")
og_image = f"{base}/img/og-logo.png" if base else "img/og-logo.png"
ig = site["instagram_handle"]

# --- SEO: title/description built only from facts already on the page ---
def price_value(price):
    m = re.search(r"\d+(?:[.,]\d+)?", price)
    return float(m.group(0).replace(",", ".")) if m else None

prices = [v for v in (price_value(p["price"]) for p in products) if v is not None]
limit = next((t for t in (10, 15, 20, 25, 30, 40, 50) if prices and max(prices) < t), None)
seo_title = (f"Betaalbare beauty-favorieten onder €{limit} | {site['brand']}" if limit
             else f"Betaalbare beauty-favorieten | {site['brand']}")
brands = list(dict.fromkeys(p["name"].split()[0] for p in products))
brand_list = ", ".join(brands[:-1]) + f" en {brands[-1]}" if len(brands) > 1 else "".join(brands)
seo_desc = (f"{len(products)} betaalbare beautyproducten uit de posts van @{ig} op één pagina"
            + (f", allemaal onder €{limit}" if limit else "")
            + f", met prijs en directe link. Met o.a. {brand_list}.")

cards = []
for i, p in enumerate(products):
    loading = "eager" if i == 0 else "lazy"
    cards.append(f"""      <article class="card" id="{e(p['id'])}">
        <img class="card-img" src="{e(p['image'])}" alt="Productfoto van {e(p['name'])}" width="600" height="600" loading="{loading}" decoding="async">
        <div class="card-body">
          <h2 class="card-title">{e(p['name'])}</h2>
          <p class="card-price"><strong>{e(p['price'])}</strong> bij {e(p['shop'])}</p>
          <p class="card-fact">{e(p['fact'])}</p>
          <a class="btn" href="{e(p['url'])}" rel="sponsored nofollow noopener" target="_blank">Bekijk bij {e(p['shop'])}</a>
        </div>
      </article>""")

html = f"""<!doctype html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(seo_title)}</title>
  <meta name="description" content="{e(seo_desc)}">
  <meta name="robots" content="index, follow">
  <meta name="theme-color" content="#C8AAF0">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{e(seo_title)}">
  <meta property="og:description" content="{e(seo_desc)}">
  <meta property="og:image" content="{e(og_image)}">
  <meta property="og:locale" content="nl_NL">{f'''
  <meta property="og:url" content="{e(base)}/">
  <link rel="canonical" href="{e(base)}/">''' if base else ''}
  <meta name="twitter:card" content="summary">
  <link rel="icon" href="favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="img/favicon-32.png">
  <link rel="apple-touch-icon" href="img/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *,*::before,*::after{{box-sizing:border-box}}
    html{{-webkit-text-size-adjust:100%}}
    html{{min-height:100%;background:#C8AAF0 linear-gradient(170deg,#C8AAF0 0%,#E0A0E0 55%,#FF96C8 100%) no-repeat;background-size:100% 100%}}
    body{{margin:0;font-family:'Poppins',system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;color:#3a2a4a;line-height:1.5}}
    .wrap{{max-width:480px;margin:0 auto;padding:28px 16px 32px}}
    header{{text-align:center;color:#fff}}
    .logo{{width:96px;height:96px;border-radius:50%;display:block;margin:0 auto 12px;box-shadow:0 6px 20px rgba(90,40,120,.25);border:3px solid #fff}}
    .brand{{margin:0;font-size:1.6rem;font-weight:700;letter-spacing:-.01em;text-shadow:0 1px 8px rgba(90,40,120,.25)}}
    .tagline{{margin:2px 0 0;font-size:1rem;font-weight:500;opacity:.95;text-shadow:0 1px 6px rgba(90,40,120,.2)}}
    .disclosure{{margin:20px 0 22px;padding:12px 14px;background:rgba(255,255,255,.92);border-radius:14px;font-size:.86rem;font-weight:500;color:#5a2a6a;text-align:center;box-shadow:0 4px 14px rgba(90,40,120,.15)}}
    .disclosure strong{{color:#d0408a}}
    .cards{{display:grid;gap:18px}}
    .card{{display:flex;flex-direction:column;background:#fff;border-radius:22px;overflow:hidden;box-shadow:0 8px 24px rgba(90,40,120,.18)}}
    .card-img{{display:block;width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;background:#f3e8fb}}
    .card-body{{flex:1 1 auto;display:flex;flex-direction:column;padding:16px 18px 18px}}
    .card-title{{margin:0 0 4px;font-size:1.08rem;font-weight:600;line-height:1.35;color:#3a2a4a}}
    .card-price{{margin:0 0 8px;font-size:1rem;color:#6a4a7a}}
    .card-price strong{{font-size:1.2rem;font-weight:700;color:#d0408a}}
    .card-fact{{margin:0 0 14px;font-size:.92rem;color:#5a4a66}}
    .btn{{display:block;margin-top:auto;text-align:center;text-decoration:none;font-weight:600;font-size:1.05rem;color:#fff;padding:14px 18px;border-radius:999px;
      background:linear-gradient(90deg,#B58CEB 0%,#FF7DBA 100%);box-shadow:0 4px 12px rgba(208,64,138,.3);transition:transform .15s ease,box-shadow .15s ease}}
    .btn:hover,.btn:focus-visible{{transform:translateY(-1px);box-shadow:0 6px 16px rgba(208,64,138,.4)}}
    .btn:focus-visible{{outline:3px solid #fff;outline-offset:2px}}
    footer{{margin-top:26px;text-align:center;color:#fff;font-size:.85rem;text-shadow:0 1px 6px rgba(90,40,120,.25)}}
    footer p{{margin:4px 0;font-weight:500}}
    .ig{{display:inline-block;margin-bottom:10px;padding:10px 20px;border-radius:999px;background:rgba(255,255,255,.95);color:#a03a8a;font-weight:600;font-size:.95rem;text-decoration:none;text-shadow:none;box-shadow:0 4px 12px rgba(90,40,120,.15)}}
    .ig:hover,.ig:focus-visible{{background:#fff}}
    @media (min-width:600px){{.wrap{{padding-top:44px}}}}
    /* Desktop/tablet: wider container for the grid; header, disclosure and footer stay narrow and centred */
    @media (min-width:640px){{
      .wrap{{max-width:1100px;padding-left:24px;padding-right:24px}}
      .disclosure{{max-width:560px;margin-left:auto;margin-right:auto}}
      .cards{{grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}}
    }}
    @media (min-width:1100px){{.cards{{grid-template-columns:repeat(3,minmax(0,1fr))}}}}
    @media (prefers-reduced-motion:reduce){{.btn{{transition:none}}}}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <img class="logo" src="img/logo.png" alt="beautybudget logo" width="96" height="96">
      <h1 class="brand">{e(site['brand'])}</h1>
      <p class="tagline">{e(site['tagline'])}</p>
    </header>

    <p class="disclosure" role="note">{e(site['disclosure']).replace('#adv', '<strong>#adv</strong>', 1)}</p>

    <main class="cards">
{chr(10).join(cards)}
    </main>

    <footer>
      <a class="ig" href="https://www.instagram.com/{e(ig)}/" rel="noopener" target="_blank">Volg @{e(ig)} op Instagram</a>
      <p>Prijs kan wijzigen. Laatst gecheckt: {e(site['last_checked'])}</p>
    </footer>
  </div>
</body>
</html>
"""
(HERE / "index.html").write_text(html, encoding="utf-8")
# robots.txt + sitemap.xml at the domain root (https://beautybudget.nl/), plus CNAME so
# GitHub Pages serves the site on the custom domain. Submit the sitemap in Search Console.
today = date.today().isoformat()
page_url = f"{base}/" if base else ""
if page_url:
    (HERE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    (HERE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url>\n    <loc>{escape(page_url)}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n'
        '</urlset>\n', encoding="utf-8")
    print(f"robots.txt en sitemap.xml geschreven (lastmod {today}).")
# CNAME for GitHub Pages custom domain (only when site_url is a root domain, not *.github.io)
from urllib.parse import urlparse
_u = urlparse(base)
if _u.hostname and not _u.hostname.endswith(".github.io") and _u.path in ("", "/"):
    (HERE / "CNAME").write_text(_u.hostname, encoding="utf-8")
    print(f"CNAME geschreven ({_u.hostname}).")
print(f"index.html geschreven met {len(products)} producten (nieuwste eerst).")
