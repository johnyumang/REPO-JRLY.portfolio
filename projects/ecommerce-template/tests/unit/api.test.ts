import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest';
import { products, variantsOf } from '@/content/catalog';
import type { TemplateDB } from '@/lib/db';
import { BASE, freshDb, json, mockServer } from './helpers';

const { server, ctx } = mockServer();
let db: TemplateDB;
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterAll(() => server.close());
beforeEach(async () => { db = ctx.db = await freshDb(); });

const get = (p: string) => fetch(BASE + p);
const tee = products.find((p) => p.slug === 'essential-white-tee')!;
const teeLine = { slug: tee.slug, color: 'White', size: 'M' };
const soldOut = products.find((p) => p.soldOut?.length)!;

describe('catalog', () => {
  it('lists collections', async () => {
    expect((await (await get('/api/collections')).json()).length).toBe(8);
  });

  it('paginates products, newest first by default', async () => {
    const body = await (await get('/api/products?limit=10&offset=5')).json();
    expect(body.total).toBe(48);
    expect(body.items.length).toBe(10);
    expect(body.items[0].slug).toBe(products[5].slug);
  });

  it('filters by collection and sorts by price', async () => {
    const asc = await (await get('/api/products?collection=outerwear&sort=price-asc&limit=100')).json();
    const want = products.filter((p) => p.collections.includes('outerwear'));
    expect(asc.total).toBe(want.length);
    const prices = asc.items.map((p: { price: number }) => p.price);
    expect(prices).toEqual([...prices].sort((a, b) => a - b));
    const desc = await (await get('/api/products?collection=outerwear&sort=price-desc&limit=100')).json();
    expect(desc.items[0].price).toBe(Math.max(...prices));
  });

  it('searches name, colour and collection with all terms required', async () => {
    const b1 = await (await get('/api/products?q=knit')).json();
    expect(b1.items.length).toBeGreaterThan(3);
    for (const p of b1.items) expect(JSON.stringify(p).toLowerCase()).toContain('knit');
    const b2 = await (await get('/api/products?q=black%20tee')).json();
    expect(b2.items.every((p: { name: string }) => /tee/i.test(p.name))).toBe(true);
    expect((await (await get('/api/products?q=zzzz')).json()).total).toBe(0);
  });

  it('rejects bad query params', async () => {
    expect((await get('/api/products?limit=1000')).status).toBe(400);
    expect((await get('/api/products?sort=evil')).status).toBe(400);
  });

  it('returns a product with variants, or 404', async () => {
    const p = await (await get(`/api/products/${tee.slug}`)).json();
    expect(p.variants).toEqual(variantsOf(tee));
    expect((await get('/api/products/nope')).status).toBe(404);
  });

  it('returns reviews with an average', async () => {
    const r = await (await get(`/api/products/${products[0].slug}/reviews`)).json();
    expect(r.count).toBe(2);
    expect(r.average).toBeGreaterThan(0);
    expect((await (await get(`/api/products/${products[40].slug}/reviews`)).json()).average).toBeNull();
  });

  it('serves blog posts newest first and FAQs by category', async () => {
    const posts = await (await get('/api/blog')).json();
    expect(posts.length).toBe(6);
    expect(posts[0].publishedAt >= posts[5].publishedAt).toBe(true);
    expect((await get('/api/blog/autumn-edit')).status).toBe(200);
    expect((await get('/api/blog/missing')).status).toBe(404);
    expect((await (await get('/api/faqs')).json()).length).toBe(30);
    expect((await (await get('/api/faqs?category=Returns')).json()).length).toBe(5);
  });
});

describe('cart', () => {
  it('adds, merges identical lines, updates and removes', async () => {
    expect((await fetch(`${BASE}/api/cart`, json({ ...teeLine, qty: 1 }))).status).toBe(201);
    const merged = await fetch(`${BASE}/api/cart`, json({ ...teeLine, qty: 2 }));
    expect(merged.status).toBe(200);
    const line = await merged.json();
    expect(line.qty).toBe(3);
    expect((await (await get('/api/cart')).json()).length).toBe(1);

    const patched = await fetch(`${BASE}/api/cart/${encodeURIComponent(line.id)}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ qty: 1 }) });
    expect((await patched.json()).qty).toBe(1);
    expect((await fetch(`${BASE}/api/cart/${encodeURIComponent(line.id)}`, { method: 'PATCH', body: JSON.stringify({ qty: 0 }) })).status).toBe(204);
    expect(await db.cart.count()).toBe(0);
  });

  it('refuses unknown variants, sold-out sizes and invalid bodies', async () => {
    expect((await fetch(`${BASE}/api/cart`, json({ ...teeLine, size: 'XXXL' }))).status).toBe(404);
    expect((await fetch(`${BASE}/api/cart`, json({ slug: soldOut.slug, color: soldOut.colors[0].name, size: soldOut.soldOut![0] }))).status).toBe(409);
    expect((await fetch(`${BASE}/api/cart`, json({ ...teeLine, qty: 99 }))).status).toBe(400);
    expect((await fetch(`${BASE}/api/cart`, { method: 'POST', body: 'not json' })).status).toBe(400);
    expect(await db.cart.count()).toBe(0);
  });
});

describe('wishlist', () => {
  it('is idempotent on add and supports remove', async () => {
    await fetch(`${BASE}/api/wishlist/${tee.slug}`, { method: 'PUT' });
    await fetch(`${BASE}/api/wishlist/${tee.slug}`, { method: 'PUT' });
    expect(await db.wishlist.count()).toBe(1);
    expect((await fetch(`${BASE}/api/wishlist/nope`, { method: 'PUT' })).status).toBe(404);
    await fetch(`${BASE}/api/wishlist/${tee.slug}`, { method: 'DELETE' });
    expect(await db.wishlist.count()).toBe(0);
  });
});

describe('orders', () => {
  const stockOf = async (slug: string, color: string, size: string) => (await db.products.get(slug))!.variants.find((v) => v.color === color && v.size === size)!.stock;

  it('creates an order from the stored cart, recomputing prices and shipping server-side', async () => {
    await fetch(`${BASE}/api/cart`, json({ ...teeLine, qty: 2 }));
    const before = await stockOf(tee.slug, 'White', 'M');
    const res = await fetch(`${BASE}/api/orders`, json({ email: 'Buyer@Example.com' }));
    expect(res.status).toBe(201);
    const order = await res.json();
    expect(order.email).toBe('buyer@example.com');
    expect(order.subtotal).toBe(tee.price * 2);
    expect(order.shipping).toBe(4.95);
    expect(order.total).toBe(Math.round((tee.price * 2 + 4.95) * 100) / 100);
    expect(await stockOf(tee.slug, 'White', 'M')).toBe(before - 2);
    expect(await db.cart.count()).toBe(0);
  });

  it('ignores any price the client tries to send', async () => {
    const res = await fetch(`${BASE}/api/orders`, json({ email: 'a@b.co', lines: [{ ...teeLine, qty: 1, unitPrice: 0.01, price: 0.01 }] }));
    expect((await res.json()).lines[0].unitPrice).toBe(tee.price);
  });

  it('is idempotent on Idempotency-Key and decrements stock once', async () => {
    const before = await stockOf(tee.slug, 'White', 'M');
    const body = { email: 'a@b.co', lines: [{ ...teeLine, qty: 1 }] };
    const a = await fetch(`${BASE}/api/orders`, json(body, { 'Idempotency-Key': 'k-1' }));
    const b = await fetch(`${BASE}/api/orders`, json(body, { 'Idempotency-Key': 'k-1' }));
    expect([a.status, b.status]).toEqual([201, 200]);
    expect((await a.json()).id).toBe((await b.json()).id);
    expect(await db.orders.where('idempotencyKey').equals('k-1').count()).toBe(1);
    expect(await stockOf(tee.slug, 'White', 'M')).toBe(before - 1);
  });

  it('handles concurrent duplicates without double-writing', async () => {
    const body = { email: 'a@b.co', lines: [{ ...teeLine, qty: 1 }] };
    const results = await Promise.all([1, 2, 3].map(() => fetch(`${BASE}/api/orders`, json(body, { 'Idempotency-Key': 'race' }))));
    expect(results.filter((r) => r.status === 201).length).toBe(1);
    expect(await db.orders.where('idempotencyKey').equals('race').count()).toBe(1);
  });

  it('is all-or-nothing when one line is out of stock', async () => {
    const before = await stockOf(tee.slug, 'White', 'M');
    const lines = [{ ...teeLine, qty: 1 }, { slug: soldOut.slug, color: soldOut.colors[0].name, size: soldOut.soldOut![0], qty: 1 }];
    expect((await fetch(`${BASE}/api/orders`, json({ email: 'a@b.co', lines }))).status).toBe(409);
    expect(await stockOf(tee.slug, 'White', 'M')).toBe(before);
    expect(await db.orders.count()).toBe(5);
  });

  it('rejects an empty cart and invalid emails', async () => {
    expect((await fetch(`${BASE}/api/orders`, json({ email: 'a@b.co' }))).status).toBe(422);
    expect((await fetch(`${BASE}/api/orders`, json({ email: 'not-an-email', lines: [{ ...teeLine, qty: 1 }] }))).status).toBe(400);
  });

  it('lists a user’s orders newest first', async () => {
    const list = await (await get('/api/orders?userId=usr_customer')).json();
    expect(list.length).toBe(5);
    expect(list[0].createdAt >= list[4].createdAt).toBe(true);
  });
});

describe('tickets and newsletter', () => {
  it('creates tickets idempotently and validates input', async () => {
    const t = { email: 'a@b.co', subject: 'Where is my order?', message: 'It has been a week, please help.' };
    const a = await fetch(`${BASE}/api/tickets`, json(t, { 'Idempotency-Key': 'tkt-1' }));
    const b = await fetch(`${BASE}/api/tickets`, json(t, { 'Idempotency-Key': 'tkt-1' }));
    expect([a.status, b.status]).toEqual([201, 200]);
    expect(await db.tickets.count()).toBe(1);
    expect((await fetch(`${BASE}/api/tickets`, json({ ...t, message: 'short' }))).status).toBe(400);
  });

  it('stores XSS payloads as inert text (escaping happens at render)', async () => {
    const payload = '<script>alert(1)</script> please help me';
    const res = await fetch(`${BASE}/api/tickets`, json({ email: 'a@b.co', subject: 'xss test', message: payload }));
    expect((await res.json()).message).toBe(payload);
  });

  it('subscribes each email once, case-insensitively', async () => {
    expect((await fetch(`${BASE}/api/newsletter`, json({ email: 'News@Example.com' }))).status).toBe(201);
    expect((await fetch(`${BASE}/api/newsletter`, json({ email: 'news@example.com' }))).status).toBe(200);
    expect(await db.newsletter.count()).toBe(1);
    expect((await fetch(`${BASE}/api/newsletter`, json({ email: 'nope' }))).status).toBe(400);
  });
});
