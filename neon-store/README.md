# [BRAND NAME] — cyberpunk compression-wear store template

A static e-commerce template for a cyberpunk-style brand selling arm compression sleeves, compression tops and leggings. It is plain HTML, CSS and JavaScript, with no build step, no framework and no paid services. It is mobile-first, accessible (WCAG 2.1 AA) and ready for GitHub Pages.

## What's inside

| Page | File | Highlights |
|---|---|---|
| Home | `index.html` | Full-screen neon hero with glitch headline and scanlines, collection tiles, lookbook strip, fabric/tech section, reviews band, newsletter |
| Shop | `shop.html` | Product grid with category, size, colour and design filters and sorting. Filters are kept in the URL, so links like `shop.html?category=leggings` work |
| Product | `product.html?id=…` | Gallery, colour and size selectors, size-guide modal, quantity, add to cart, Details/Fabric/Care tabs, shipping and returns, related products |
| Lookbook | `lookbook.html` | Masonry gallery from `images/on_model/` |
| Our story | `about.html` | Founder and operations photos, how it's made, values |
| Shipping, Returns & FAQ | `shipping.html` | Packaging photos, policies, accordion FAQ (with FAQ structured data) |
| Contact | `contact.html` | Validated form (no backend yet) and social links |
| 404 | `404.html` | "Signal lost" page |

Every page also gets: an announcement bar (free-shipping threshold), a sticky header, a cart drawer with a free-shipping progress bar, a footer with policy links, SEO and Open Graph tags, and a favicon placeholder.

## Edit everything in one file

**`assets/js/config.js`** holds the brand name, prices, currency, shipping threshold, announcement text, navigation, social links, products, size guide, FAQ, lookbook list and all page copy.

1. Replace every `[BRAND NAME]` and `[PLACEHOLDER]` value.
2. Set `brand.siteUrl` to your live address, e.g. `https://yourname.github.io/your-repo`.
3. Run `node tools/apply-meta.mjs`. This writes the page titles, descriptions, Open Graph tags, `sitemap.xml` and `robots.txt` from the config. Link previews on Facebook and Messenger read these tags without running JavaScript, so they have to be written into the HTML.

### Adding real product photos

Put the files in `images/products/` and list them in that product's `images` array:

```js
{ id: 'circuit-leggings', /* … */ images: ['images/products/circuit-leggings-front.jpg', 'images/products/circuit-leggings-back.jpg', 'images/products/circuit-leggings-detail.jpg'] }
```

While `images` is empty, the site draws a neon placeholder in the product's colour and design pattern, labelled "PHOTO PLACEHOLDER".

## Preview locally

The pages load `config.js` with relative paths, so use a local server rather than double-clicking the file:

```bash
cd path/to/this/folder
python3 -m http.server 8000      # or: npx serve .
```

Then open <http://localhost:8000>.

## Deploy free on GitHub Pages

1. Create a new **public** repository on GitHub, e.g. `neon-store`.
2. Upload the contents of this folder to the repository root (`index.html` must be at the top level). You can drag and drop in the browser, or run:
   ```bash
   git init && git add . && git commit -m "Initial site"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/neon-store.git
   git push -u origin main
   ```
3. In the repository go to **Settings → Pages → Build and deployment → Source: Deploy from a branch**, then choose **Branch: `main`**, folder **`/ (root)`**, and click **Save**.
4. After about a minute the site is live at `https://YOUR-USERNAME.github.io/neon-store/`.
5. Put that URL in `brand.siteUrl`, run `node tools/apply-meta.mjs`, then commit and push again.

The `.nojekyll` file tells GitHub Pages to serve the files as they are.

## Connecting the parts that need a backend

| Feature | Free or low-cost option |
|---|---|
| Checkout | Shopify Starter or Buy Button, Snipcart, or Stripe Payment Links. Wire the cart drawer's **Checkout** button (`[data-checkout]` in `assets/js/app.js`) |
| Newsletter | Brevo, Mailchimp or Kit free tiers. Point the `[data-newsletter]` forms at their embed endpoint |
| Contact form | Formspree or Web3Forms free tier. Add `action="…" method="POST"` to the form in `contact.html` and remove the preview handler |

## Moving to Shopify later

The config mirrors Shopify's data model:

- `products[]` → Shopify products. Each `colours` × `sizes` combination becomes a variant, and `id` becomes the handle.
- `categories` → collections. `shop.html?category=…` maps to `/collections/…`.
- `copy`, `faq` and `productInfo` → theme settings or metafields.
- `assets/css/main.css` can be dropped into a Dawn-based theme as `assets/custom.css`. The section structure (hero, collection list, image with text, testimonials, newsletter) matches Dawn's built-in sections.

## Images

- Only the photos in `images/` are used. Read `images/README.md` for which folder feeds which section.
- `CREDITS.md` (also in `images/`) lists every photographer. All photos are under the Pexels License: free for commercial use, attribution appreciated.
- `social/README.md` explains how to use the 1:1, 4:5 and 9:16 crops for ads.
- **Before launch:** stock photos set the mood but don't show your product. Some of them also show other companies' logos (a branded top on `athlete_man_compression_top_01`, branded items in the flat-lay). Replace those with your own shoot before running ads.

## Accessibility and performance

- Skip link, landmarks and labelled forms. The cart drawer and size guide trap focus and close on Escape.
- Colour and size pickers are proper radio groups with arrow-key support.
- Text contrast is at least 4.5:1 and controls are at least 44–48 px. Focus rings are visible everywhere.
- Glitch and motion effects switch off under `prefers-reduced-motion`.
- Images below the fold are lazy-loaded, and the hero image is preloaded.
- For a faster site, convert `images/` to WebP at 1600 px wide (for example with Squoosh). This typically cuts total size by about 60%.

## File map

```
index.html shop.html product.html lookbook.html about.html shipping.html contact.html 404.html
assets/css/main.css        design tokens + components
assets/js/config.js        ← edit this
assets/js/app.js           header, footer, cart, shared helpers
assets/img/favicon.svg     favicon placeholder
images/                    photo kit + README + CREDITS
social/README.md           ad crop guide
tools/apply-meta.mjs       writes SEO/OG tags, sitemap, robots
CREDITS.md                 photo credits (keep in the repo)
```
