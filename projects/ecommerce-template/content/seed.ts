// PLACEHOLDER SEED DATA — every record here is template content. Replace before launch.
import { BRAND, products } from './catalog';

export type Role = 'customer' | 'support' | 'admin';
export type User = { id: string; email: string; name: string; role: Role; passwordHash: string; createdAt: string };
export type Post = { slug: string; title: string; excerpt: string; body: string; image: string; author: string; publishedAt: string; tags: string[] };
export type Faq = { id: string; category: 'Orders' | 'Shipping' | 'Returns' | 'Payments' | 'Products' | 'Account'; q: string; a: string };
export type Review = { id: string; productSlug: string; author: string; rating: 1 | 2 | 3 | 4 | 5; title: string; body: string; createdAt: string; verified: boolean };
export type OrderLine = { slug: string; name: string; color: string; size: string; qty: number; unitPrice: number };
export type OrderStatus = 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled' | 'refunded';
export type Order = {
  id: string; userId: string | null; email: string; lines: OrderLine[];
  subtotal: number; shipping: number; total: number; status: OrderStatus;
  createdAt: string; updatedAt: string; idempotencyKey?: string;
};

// Demo accounts. Plain-text passwords are documented in README.md only; the bundle ships hashes.
export const users: User[] = [
  { id: 'usr_customer', email: 'customer@example.com', name: '[CUSTOMER NAME]', role: 'customer', createdAt: '2026-09-01T09:00:00.000Z',
    passwordHash: 'pbkdf2$sha256$210000$uL5xWdBQEvXwtxWROxRlaw==$6ZdYhGmhmO5hIwJwjxofa3qfI9K5wwkTYz+yh4WcivU=' },
  { id: 'usr_support', email: 'support@example.com', name: '[SUPPORT AGENT]', role: 'support', createdAt: '2026-08-15T09:00:00.000Z',
    passwordHash: 'pbkdf2$sha256$210000$jpy3DN4+gtx4mNIWDB4mCQ==$6bA8klHqsiOOYxPfMNRtCxQjCzubE6mp2LplZpxdP5o=' },
  { id: 'usr_admin', email: 'admin@example.com', name: '[ADMIN NAME]', role: 'admin', createdAt: '2026-08-01T09:00:00.000Z',
    passwordHash: 'pbkdf2$sha256$210000$qOszNrz630B602QAOkrUsQ==$PHCNMi4Y+xPy1v5Am0GFrMDxg9hdiCruRL7FPcdCK+0=' },
];

const post = (slug: string, title: string, image: string, day: number, tags: string[]): Post => ({
  slug, title, image, tags, author: `${BRAND} Editorial`,
  publishedAt: new Date(Date.UTC(2026, 9, 28 - day * 5)).toISOString(),
  excerpt: `[EXCERPT] ${title}: a short placeholder summary for the blog listing.`,
  body: `[BODY] Placeholder article for "${title}". Replace with real ${BRAND} content.\n\n[SECTION] Second paragraph of placeholder copy.`,
});

export const posts: Post[] = [
  post('autumn-edit', 'The Autumn Edit', 'check-coat', 0, ['style', 'outerwear']),
  post('how-to-layer-knitwear', 'How to Layer Knitwear', 'knit-model', 1, ['style', 'knitwear']),
  post('capsule-wardrobe-basics', 'Building a Capsule Wardrobe', 'tee-white', 2, ['basics', 'guide']),
  post('caring-for-leather', 'Caring for Leather', 'biker-model', 3, ['care', 'guide']),
  post('finding-your-fit', 'Finding Your Fit', 'stripe-pant', 4, ['sizing', 'guide']),
  post('behind-the-collection', 'Behind the Collection', 'rack-store', 5, ['brand']),
];

const FAQ_TOPICS: Record<Faq['category'], string[]> = {
  Orders: ['How do I track my order?', 'Can I change my order?', 'Can I cancel my order?', 'Why was my order split?', 'Do I need an account to order?'],
  Shipping: ['How long does delivery take?', 'How much is shipping?', 'Do you ship internationally?', 'Can I change my delivery address?', 'What if my parcel is lost?'],
  Returns: ['What is your returns policy?', 'How do I start a return?', 'When will I get my refund?', 'Can I exchange an item?', 'Are returns free?'],
  Payments: ['Which payment methods do you accept?', 'Is my payment secure?', 'Do you offer instalments?', 'Why was my payment declined?', 'Can I use a gift card?'],
  Products: ['How do I find my size?', 'How do I care for my garment?', 'Will a sold-out item be restocked?', 'Are your products sustainable?', 'Where are your products made?'],
  Account: ['How do I reset my password?', 'How do I update my details?', 'How do I delete my account?', 'How do I unsubscribe from emails?', 'Why can’t I log in?'],
};
export const faqs: Faq[] = (Object.entries(FAQ_TOPICS) as [Faq['category'], string[]][])
  .flatMap(([category, qs]) => qs.map((q, i) => ({ id: `faq_${category.toLowerCase()}_${i + 1}`, category, q, a: `[ANSWER] Placeholder answer for "${q}" Replace with ${BRAND} policy.` })));

const REVIEWERS = ['[REVIEWER A]', '[REVIEWER B]', '[REVIEWER C]', '[REVIEWER D]', '[REVIEWER E]'];
const RATINGS: Review['rating'][] = [5, 4, 5, 3, 5, 4, 5, 5, 2, 4, 5, 4, 3, 5, 4, 5, 5, 4, 1, 5];
export const reviews: Review[] = RATINGS.map((rating, i) => ({
  id: `rev_${i + 1}`,
  productSlug: products[i % 10].slug, // concentrated on the first 10 products so PDPs show multiple reviews
  author: REVIEWERS[i % REVIEWERS.length],
  rating,
  title: `[REVIEW TITLE] ${rating}-star placeholder`,
  body: '[REVIEW BODY] Placeholder review text.',
  createdAt: new Date(Date.UTC(2026, 9, 25) - i * 86_400_000).toISOString(),
  verified: i % 4 !== 3,
}));

export const SHIPPING_FEE = 4.95;
export const FREE_SHIPPING_THRESHOLD = 50;
const round = (n: number) => Math.round(n * 100) / 100;
export const shippingFor = (subtotal: number) => (subtotal >= FREE_SHIPPING_THRESHOLD || subtotal === 0 ? 0 : SHIPPING_FEE);
export const totals = (lines: Pick<OrderLine, 'qty' | 'unitPrice'>[]) => {
  const subtotal = round(lines.reduce((s, l) => s + l.qty * l.unitPrice, 0));
  const shipping = shippingFor(subtotal);
  return { subtotal, shipping, total: round(subtotal + shipping) };
};

const line = (i: number, qty = 1): OrderLine => {
  const p = products[i];
  return { slug: p.slug, name: p.name, color: p.colors[0].name, size: p.sizes[Math.min(2, p.sizes.length - 1)], qty, unitPrice: p.price };
};
const order = (n: number, status: OrderStatus, lines: OrderLine[], day: number): Order => {
  const at = new Date(Date.UTC(2026, 9, 20) - day * 86_400_000).toISOString();
  return { id: `ord_100${n}`, userId: 'usr_customer', email: 'customer@example.com', lines, ...totals(lines), status, createdAt: at, updatedAt: at };
};
export const orders: Order[] = [
  order(1, 'delivered', [line(0), line(3, 2)], 30),
  order(2, 'delivered', [line(1)], 22),
  order(3, 'shipped', [line(7), line(5)], 9),
  order(4, 'paid', [line(4, 3)], 3),
  order(5, 'refunded', [line(9)], 15),
];

export const SEED_VERSION = 1;
