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
  badge?: 'NEW' | 'BESTSELLER' | 'LIMITED';
  description: string;
  composition: string;
};

const APPAREL = ['XS', 'S', 'M', 'L', 'XL'];

export const products: Product[] = [
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
];

export const collections = [
  { slug: 'new-in', title: 'New In', image: 'hero' },
  { slug: 'women', title: 'Woman', image: 'blue-coat' },
  { slug: 'men', title: 'Man', image: 'biker-model' },
  { slug: 'outerwear', title: 'Outerwear', image: 'check-coat' },
  { slug: 'knitwear', title: 'Knitwear', image: 'knit-model' },
  { slug: 'basics', title: 'Basics', image: 'tee-white' },
] as const;

export const getProduct = (slug: string) => products.find((p) => p.slug === slug);
export const inCollection = (slug: string) => products.filter((p) => p.collections.includes(slug));
export const money = (n: number) => `${n.toFixed(2).replace('.', ',')} ${CURRENCY}`;
