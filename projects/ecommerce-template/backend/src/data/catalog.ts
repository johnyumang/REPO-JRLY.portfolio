// GENERATED from ../../content/catalog.ts by scripts/sync-catalog.mjs — edit the storefront file, not this one.
// PLACEHOLDER CATALOG — replace with real products. All names/prices are template data.
export const BRAND = '[BRAND]';
export const CURRENCY = '€';
export const FREE_SHIPPING_OVER = 50;

export type Product = {
  slug: string;
  name: string;
  price: number;
  compareAt?: number;
  colors: { name: string; hex: string }[];
  sizes: string[];
  soldOut?: string[];
  images: string[]; // stock image keys, first two = card + hover
  collections: string[];
  createdAt: string; // ISO date, drives "new" sorting
  badge?: 'NEW' | 'BESTSELLER' | 'LIMITED';
  description: string;
  composition: string;
};

const APPAREL = ['XS', 'S', 'M', 'L', 'XL'];
const WAIST = ['26', '28', '30', '32', '34'];
const ONE = ['ONE SIZE'];
const c = (name: string, hex: string) => ({ name, hex });

// Compact row helper for the extended placeholder range.
const row = (slug: string, name: string, price: number, colors: Product['colors'], images: string[], cols: string[], extra: Partial<Product> = {}): Omit<Product, 'createdAt'> => ({
  slug, name, price, colors, sizes: APPAREL, images, collections: cols,
  description: `[PRODUCT DESCRIPTION] ${name} — placeholder copy.`, composition: '[COMPOSITION] Placeholder composition.', ...extra,
});

const base: Omit<Product, 'createdAt'>[] = [
  { slug: 'leather-biker-jacket', name: 'Leather Biker Jacket', price: 189, colors: [{ name: 'Black', hex: '#111' }], sizes: APPAREL, soldOut: ['XS'], images: ['biker-model', 'leather-model', 'rack-store'], collections: ['new-in', 'outerwear', 'men'], badge: 'BESTSELLER', description: '[PRODUCT DESCRIPTION] Classic biker silhouette with asymmetric zip, notched lapels and zipped cuffs.', composition: '[COMPOSITION] Outer: 100% leather. Lining: 100% polyester.' },
  { slug: 'knit-fringe-poncho', name: 'Knit Fringe Poncho', price: 59, colors: [{ name: 'Ecru', hex: '#EDE6D6' }], sizes: ['ONE SIZE'], images: ['poncho', 'knit-model', 'rack-neutral'], collections: ['new-in', 'women', 'knitwear'], badge: 'NEW', description: '[PRODUCT DESCRIPTION] Open-knit V-neck poncho with fringed hem.', composition: '[COMPOSITION] 60% cotton, 40% acrylic.' },
  { slug: 'terracotta-bomber', name: 'Terracotta Bomber', price: 89, colors: [{ name: 'Terracotta', hex: '#C46A4E' }, { name: 'Black', hex: '#111' }], sizes: APPAREL, images: ['bomber', 'leather-model', 'rack-hanger'], collections: ['new-in', 'outerwear', 'men'], badge: 'NEW', description: '[PRODUCT DESCRIPTION] Lightweight bomber with ribbed trims and front zip.', composition: '[COMPOSITION] 100% polyester.' },
  { slug: 'essential-white-tee', name: 'Essential White Tee', price: 19, colors: [{ name: 'White', hex: '#F7F7F7' }, { name: 'Black', hex: '#111' }], sizes: APPAREL, images: ['tee-white', 'rack-hanger', 'tee-graphic-model'], collections: ['basics', 'men', 'new-in'], badge: 'BESTSELLER', description: '[PRODUCT DESCRIPTION] Heavyweight crew-neck tee with a relaxed fit.', composition: '[COMPOSITION] 100% cotton.' },
  { slug: 'pocket-crest-tee', name: 'Pocket Crest Tee', price: 25, colors: [{ name: 'Black', hex: '#111' }], sizes: APPAREL, images: ['tee-black', 'tee-graphic-model', 'rack-store'], collections: ['basics', 'men'], description: '[PRODUCT DESCRIPTION] Black tee with a small chest print.', composition: '[COMPOSITION] 100% cotton.' },
  { slug: 'washed-blue-tee', name: 'Washed Blue Tee', price: 19, colors: [{ name: 'Sky', hex: '#A9C3DE' }], sizes: APPAREL, images: ['tee-blue', 'tee-white', 'rack-neutral'], collections: ['basics', 'women'], description: '[PRODUCT DESCRIPTION] Garment-washed tee in a soft regular fit.', composition: '[COMPOSITION] 100% cotton.' },
  { slug: 'satin-cargo-jogger', name: 'Satin Cargo Jogger', price: 49, colors: [{ name: 'Blush', hex: '#D9A9A0' }], sizes: APPAREL, images: ['jogger', 'stripe-pant', 'rack-store'], collections: ['new-in', 'women'], badge: 'LIMITED', description: '[PRODUCT DESCRIPTION] Fluid satin jogger with patch pockets and elastic cuffs.', composition: '[COMPOSITION] 100% polyester.' },
  { slug: 'wool-check-coat', name: 'Wool Check Coat', price: 159, compareAt: 199, colors: [{ name: 'Navy check', hex: '#1E2A44' }], sizes: APPAREL, images: ['check-coat', 'blue-coat', 'rack-hanger'], collections: ['outerwear', 'women'], description: '[PRODUCT DESCRIPTION] Longline coat in a brushed check with notch lapels.', composition: '[COMPOSITION] 70% wool, 30% polyamide.' },
  { slug: 'olive-utility-jacket', name: 'Olive Utility Jacket', price: 79, colors: [{ name: 'Olive', hex: '#5E5A3A' }], sizes: APPAREL, images: ['utility', 'denim-hood', 'rack-neutral'], collections: ['outerwear', 'women', 'new-in'], description: '[PRODUCT DESCRIPTION] Four-pocket utility jacket with a contrast hood.', composition: '[COMPOSITION] 100% cotton.' },
  { slug: 'floral-wrap-dress', name: 'Floral Wrap Dress', price: 69, colors: [{ name: 'Ivory floral', hex: '#EFE7DC' }], sizes: APPAREL, images: ['wrap-dress', 'yellow-wall', 'rack-neutral'], collections: ['women', 'new-in'], badge: 'NEW', description: '[PRODUCT DESCRIPTION] Midi wrap dress with ruffle sleeves and tie waist.', composition: '[COMPOSITION] 100% viscose.' },
  { slug: 'fleece-co-ord', name: 'Fleece Co-ord', price: 65, colors: [{ name: 'Mustard', hex: '#E0B126' }], sizes: APPAREL, images: ['coord-yellow', 'red-tee-model', 'rack-store'], collections: ['women', 'basics'], description: '[PRODUCT DESCRIPTION] Cropped hoodie and jogger set in brushed fleece.', composition: '[COMPOSITION] 80% cotton, 20% polyester.' },
  { slug: 'patchwork-knit', name: 'Patchwork Knit', price: 75, colors: [{ name: 'Camel', hex: '#B07A4A' }], sizes: APPAREL, soldOut: ['XL'], images: ['knit-model', 'poncho', 'rack-neutral'], collections: ['knitwear', 'women'], description: '[PRODUCT DESCRIPTION] Colour-block knit jumper with a turtleneck.', composition: '[COMPOSITION] 50% wool, 50% acrylic.' },

  // Extended placeholder range (Phase 2 seed: 48 products total)
  row('cropped-denim-jacket', 'Cropped Denim Jacket', 69, [c('Mid blue', '#5B7BA6')], ['denim-hood', 'utility', 'rack-store'], ['outerwear', 'women']),
  row('quilted-liner-jacket', 'Quilted Liner Jacket', 85, [c('Black', '#111'), c('Olive', '#5E5A3A')], ['bomber', 'utility', 'rack-hanger'], ['outerwear', 'men']),
  row('double-breasted-coat', 'Double-Breasted Coat', 179, [c('Cobalt', '#2E4C9A')], ['blue-coat', 'check-coat', 'rack-neutral'], ['outerwear', 'women'], { badge: 'NEW' }),
  row('suede-trucker-jacket', 'Suede Trucker Jacket', 149, [c('Tan', '#A67B52')], ['leather-model', 'biker-model', 'rack-store'], ['outerwear', 'men']),
  row('hooded-parka', 'Hooded Parka', 129, [c('Khaki', '#8A8256')], ['utility', 'denim-hood', 'rack-hanger'], ['outerwear', 'men'], { compareAt: 159 }),
  row('trench-coat', 'Classic Trench Coat', 139, [c('Stone', '#C9B99A')], ['check-coat', 'blue-coat', 'rack-neutral'], ['outerwear', 'women'], { badge: 'BESTSELLER' }),
  row('ribbed-turtleneck', 'Ribbed Turtleneck', 39, [c('Ecru', '#EDE6D6'), c('Black', '#111')], ['knit-model', 'poncho', 'rack-neutral'], ['knitwear', 'women', 'basics']),
  row('cable-knit-cardigan', 'Cable-Knit Cardigan', 59, [c('Oat', '#D8C8A8')], ['poncho', 'knit-model', 'rack-hanger'], ['knitwear', 'women']),
  row('merino-crew-jumper', 'Merino Crew Jumper', 55, [c('Navy', '#1E2A44'), c('Grey', '#8C8C8C')], ['knit-model', 'tee-black', 'rack-store'], ['knitwear', 'men']),
  row('chunky-roll-neck', 'Chunky Roll-Neck', 69, [c('Cream', '#F1EBDD')], ['poncho', 'knit-model', 'rack-neutral'], ['knitwear', 'men', 'new-in'], { badge: 'NEW' }),
  row('knit-vest', 'Knit Vest', 35, [c('Camel', '#B07A4A')], ['knit-model', 'poncho', 'rack-hanger'], ['knitwear', 'basics'], { soldOut: ['XS', 'S'] }),
  row('mohair-blend-sweater', 'Mohair-Blend Sweater', 79, [c('Lilac', '#B9A6D0')], ['poncho', 'knit-model', 'rack-store'], ['knitwear', 'women'], { badge: 'LIMITED' }),
  row('slim-rib-tank', 'Slim Rib Tank', 15, [c('White', '#F7F7F7'), c('Black', '#111')], ['tee-white', 'tee-black', 'rack-neutral'], ['basics', 'women']),
  row('oversized-tee', 'Oversized Tee', 22, [c('Washed black', '#2A2A2A')], ['tee-black', 'tee-graphic-model', 'rack-store'], ['basics', 'men']),
  row('long-sleeve-tee', 'Long-Sleeve Tee', 25, [c('Sky', '#A9C3DE'), c('White', '#F7F7F7')], ['tee-blue', 'tee-white', 'rack-hanger'], ['basics', 'men', 'women']),
  row('graphic-print-tee', 'Graphic Print Tee', 29, [c('White', '#F7F7F7')], ['tee-graphic-model', 'tee-white', 'rack-store'], ['basics', 'men', 'new-in'], { badge: 'NEW' }),
  row('red-boxy-tee', 'Red Boxy Tee', 22, [c('Red', '#B8302B')], ['red-tee-model', 'tee-black', 'rack-neutral'], ['basics', 'women']),
  row('zip-hoodie', 'Zip Hoodie', 49, [c('Mustard', '#E0B126'), c('Grey', '#8C8C8C')], ['coord-yellow', 'denim-hood', 'rack-hanger'], ['basics', 'men']),
  row('slip-midi-dress', 'Slip Midi Dress', 59, [c('Champagne', '#E5D3B3')], ['wrap-dress', 'yellow-wall', 'rack-neutral'], ['dresses', 'women', 'new-in'], { badge: 'NEW' }),
  row('shirt-dress', 'Belted Shirt Dress', 65, [c('Ivory', '#EFE7DC')], ['yellow-wall', 'wrap-dress', 'rack-store'], ['dresses', 'women']),
  row('knit-midi-dress', 'Knit Midi Dress', 75, [c('Camel', '#B07A4A')], ['knit-model', 'wrap-dress', 'rack-hanger'], ['dresses', 'knitwear']),
  row('tiered-maxi-dress', 'Tiered Maxi Dress', 79, [c('Sun yellow', '#E7C24B')], ['yellow-wall', 'coord-yellow', 'rack-neutral'], ['dresses', 'women'], { badge: 'BESTSELLER' }),
  row('mini-wrap-dress', 'Mini Wrap Dress', 49, [c('Floral', '#EFE7DC')], ['wrap-dress', 'red-tee-model', 'rack-store'], ['dresses', 'women'], { compareAt: 65 }),
  row('satin-cami-dress', 'Satin Cami Dress', 55, [c('Blush', '#D9A9A0')], ['jogger', 'wrap-dress', 'rack-hanger'], ['dresses', 'women'], { soldOut: ['M'] }),
  row('t-shirt-dress', 'T-Shirt Dress', 35, [c('Black', '#111')], ['tee-black', 'yellow-wall', 'rack-neutral'], ['dresses', 'basics']),
  row('pleated-midi-dress', 'Pleated Midi Dress', 85, [c('Navy', '#1E2A44')], ['blue-coat', 'wrap-dress', 'rack-store'], ['dresses', 'women'], { badge: 'LIMITED' }),
  row('wide-leg-trousers', 'Wide-Leg Trousers', 55, [c('Ecru', '#EDE6D6'), c('Black', '#111')], ['stripe-pant', 'jogger', 'rack-neutral'], ['trousers', 'women'], { sizes: WAIST }),
  row('pinstripe-trousers', 'Pinstripe Trousers', 59, [c('Navy stripe', '#1E2A44')], ['stripe-pant', 'check-coat', 'rack-hanger'], ['trousers', 'women', 'new-in'], { sizes: WAIST, badge: 'NEW' }),
  row('straight-leg-jeans', 'Straight-Leg Jeans', 45, [c('Mid blue', '#5B7BA6')], ['denim-hood', 'stripe-pant', 'rack-store'], ['trousers', 'men', 'basics'], { sizes: WAIST, badge: 'BESTSELLER' }),
  row('relaxed-chinos', 'Relaxed Chinos', 45, [c('Sand', '#C9B99A'), c('Olive', '#5E5A3A')], ['utility', 'stripe-pant', 'rack-neutral'], ['trousers', 'men'], { sizes: WAIST }),
  row('cargo-trousers', 'Cargo Trousers', 55, [c('Khaki', '#8A8256')], ['utility', 'jogger', 'rack-hanger'], ['trousers', 'men'], { sizes: WAIST, soldOut: ['26'] }),
  row('pleated-tailored-trousers', 'Pleated Tailored Trousers', 65, [c('Charcoal', '#3A3A3A')], ['stripe-pant', 'blue-coat', 'rack-store'], ['trousers', 'men'], { sizes: WAIST }),
  row('fleece-joggers', 'Fleece Joggers', 39, [c('Mustard', '#E0B126'), c('Grey', '#8C8C8C')], ['coord-yellow', 'jogger', 'rack-neutral'], ['trousers', 'basics']),
  row('satin-wide-trousers', 'Satin Wide Trousers', 49, [c('Blush', '#D9A9A0')], ['jogger', 'stripe-pant', 'rack-hanger'], ['trousers', 'women'], { compareAt: 59 }),
  row('knit-scarf', 'Ribbed Knit Scarf', 25, [c('Camel', '#B07A4A'), c('Ecru', '#EDE6D6')], ['poncho', 'knit-model', 'rack-store'], ['knitwear', 'new-in'], { sizes: ONE }),
  row('canvas-tote', 'Canvas Shopper Tote', 19, [c('Natural', '#E8DFCC')], ['shopping', 'rack-store', 'rack-neutral'], ['basics', 'new-in'], { sizes: ONE, badge: 'NEW' }),
];

// Deterministic placeholder dates: newest first in declaration order, one day apart.
export const products: Product[] = base.map((p, i) => ({ ...p, createdAt: new Date(Date.UTC(2026, 9, 30) - i * 86_400_000).toISOString() }));

export type Variant = { sku: string; color: string; size: string; stock: number };
const slugify = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
// Stable pseudo-stock per SKU so seed data is reproducible across runs.
const stockFor = (sku: string) => { let h = 0; for (const ch of sku) h = (h * 31 + ch.charCodeAt(0)) >>> 0; return 3 + (h % 38); };
export const variantsOf = (p: Product): Variant[] =>
  p.colors.flatMap((col) => p.sizes.map((size) => {
    const sku = `${p.slug}-${slugify(col.name)}-${slugify(size)}`;
    return { sku, color: col.name, size, stock: p.soldOut?.includes(size) ? 0 : stockFor(sku) };
  }));

export const collections = [
  { slug: 'new-in', title: 'New In', image: 'hero' },
  { slug: 'women', title: 'Woman', image: 'blue-coat' },
  { slug: 'men', title: 'Man', image: 'biker-model' },
  { slug: 'outerwear', title: 'Outerwear', image: 'check-coat' },
  { slug: 'knitwear', title: 'Knitwear', image: 'knit-model' },
  { slug: 'basics', title: 'Basics', image: 'tee-white' },
  { slug: 'dresses', title: 'Dresses', image: 'wrap-dress' },
  { slug: 'trousers', title: 'Trousers', image: 'stripe-pant' },
] as const;

export const getProduct = (slug: string) => products.find((p) => p.slug === slug);
export const inCollection = (slug: string) => products.filter((p) => p.collections.includes(slug));
export const money = (n: number) => `${n.toFixed(2).replace('.', ',')} ${CURRENCY}`;
