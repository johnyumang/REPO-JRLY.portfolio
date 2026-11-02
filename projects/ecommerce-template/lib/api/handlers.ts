// MSW request handlers: the offline implementation of the REST contract, backed by IndexedDB.
// Paths start with "*/" so they match any origin (browser, Node tests, or a live base URL).
import { http, HttpResponse } from 'msw';
import type { z } from 'zod';
import { totals, type Order, type OrderLine } from '@/content/seed';
import { cartLineId, nowIso, type TemplateDB } from '../db';
import { uuid } from '../crypto';
import { CartAdd, CartPatch, NewsletterCreate, OrderCreate, ProductQuery, TicketCreate } from './contract';

const bad = (error: string, status = 400, extra: object = {}) => HttpResponse.json({ error, ...extra }, { status });

async function parse<T extends z.ZodType>(schema: T, request: Request): Promise<{ data: z.infer<T> } | { res: Response }> {
  let raw: unknown;
  try { raw = await request.json(); } catch { return { res: bad('Invalid JSON body') }; }
  const r = schema.safeParse(raw);
  return r.success ? { data: r.data } : { res: bad('Validation failed', 400, { issues: r.error.issues }) };
}

export function createHandlers(getDb: () => TemplateDB) {
  return [
    http.get('*/api/collections', async () => HttpResponse.json(await getDb().collections.toArray())),

    http.get('*/api/products', async ({ request }) => {
      const r = ProductQuery.safeParse(Object.fromEntries(new URL(request.url).searchParams));
      if (!r.success) return bad('Validation failed', 400, { issues: r.error.issues });
      const { collection, q, sort, limit, offset } = r.data;
      const db = getDb();
      let items = collection ? await db.products.where('collections').equals(collection).toArray() : await db.products.toArray();
      if (q) {
        const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
        items = items.filter((p) => { const hay = `${p.name} ${p.collections.join(' ')} ${p.colors.map((c) => c.name).join(' ')}`.toLowerCase(); return terms.every((t) => hay.includes(t)); });
      }
      items.sort(sort === 'price-asc' ? (a, b) => a.price - b.price : sort === 'price-desc' ? (a, b) => b.price - a.price : (a, b) => b.createdAt.localeCompare(a.createdAt));
      return HttpResponse.json({ items: items.slice(offset, offset + limit), total: items.length, limit, offset });
    }),

    http.get('*/api/products/:slug', async ({ params }) => {
      const p = await getDb().products.get(String(params.slug));
      return p ? HttpResponse.json(p) : bad('Product not found', 404);
    }),

    http.get('*/api/products/:slug/reviews', async ({ params }) => {
      const items = await getDb().reviews.where('productSlug').equals(String(params.slug)).reverse().sortBy('createdAt');
      const average = items.length ? Math.round((items.reduce((s, r) => s + r.rating, 0) / items.length) * 10) / 10 : null;
      return HttpResponse.json({ items, count: items.length, average });
    }),

    // Cart
    http.get('*/api/cart', async () => HttpResponse.json(await getDb().cart.toArray())),
    http.post('*/api/cart', async ({ request }) => {
      const r = await parse(CartAdd, request); if ('res' in r) return r.res;
      const db = getDb();
      const p = await db.products.get(r.data.slug);
      const v = p?.variants.find((x) => x.color === r.data.color && x.size === r.data.size);
      if (!p || !v) return bad('Unknown product variant', 404);
      const id = cartLineId(r.data);
      const existing = await db.cart.get(id);
      const qty = (existing?.qty ?? 0) + r.data.qty;
      if (qty > v.stock) return bad('Not enough stock', 409, { available: v.stock });
      const line = { id, slug: p.slug, color: v.color, size: v.size, qty, updatedAt: nowIso() };
      await db.cart.put(line);
      return HttpResponse.json(line, { status: existing ? 200 : 201 });
    }),
    http.patch('*/api/cart/:id', async ({ params, request }) => {
      const r = await parse(CartPatch, request); if ('res' in r) return r.res;
      const db = getDb();
      const id = String(params.id);
      const line = await db.cart.get(id);
      if (!line) return bad('Cart line not found', 404);
      if (r.data.qty === 0) { await db.cart.delete(id); return new HttpResponse(null, { status: 204 }); }
      const v = (await db.products.get(line.slug))?.variants.find((x) => x.color === line.color && x.size === line.size);
      if (!v || r.data.qty > v.stock) return bad('Not enough stock', 409, { available: v?.stock ?? 0 });
      const next = { ...line, qty: r.data.qty, updatedAt: nowIso() };
      await db.cart.put(next);
      return HttpResponse.json(next);
    }),
    http.delete('*/api/cart/:id', async ({ params }) => { await getDb().cart.delete(String(params.id)); return new HttpResponse(null, { status: 204 }); }),

    // Wishlist
    http.get('*/api/wishlist', async () => HttpResponse.json(await getDb().wishlist.toArray())),
    http.put('*/api/wishlist/:slug', async ({ params }) => {
      const db = getDb();
      const slug = String(params.slug);
      if (!(await db.products.get(slug))) return bad('Product not found', 404);
      const row = (await db.wishlist.get(slug)) ?? { slug, addedAt: nowIso() };
      await db.wishlist.put(row);
      return HttpResponse.json(row);
    }),
    http.delete('*/api/wishlist/:slug', async ({ params }) => { await getDb().wishlist.delete(String(params.slug)); return new HttpResponse(null, { status: 204 }); }),

    // Orders — idempotent on the Idempotency-Key header so sync replays never duplicate.
    http.get('*/api/orders', async ({ request }) => {
      const userId = new URL(request.url).searchParams.get('userId');
      const db = getDb();
      const items = userId ? await db.orders.where('userId').equals(userId).toArray() : await db.orders.toArray();
      return HttpResponse.json(items.sort((a, b) => b.createdAt.localeCompare(a.createdAt)));
    }),
    http.post('*/api/orders', async ({ request }) => {
      const key = request.headers.get('Idempotency-Key') ?? undefined;
      const db = getDb();
      const r = await parse(OrderCreate, request); if ('res' in r) return r.res;
      const usingCart = !r.data.lines;
      const wanted = r.data.lines ?? (await db.cart.toArray());

      let result: Response | undefined;
      await db.transaction('rw', [db.products, db.orders, db.cart, db.audit], async () => {
        // Dedupe inside the transaction so concurrent replays of the same key can't both write.
        if (key) { const dup = await db.orders.where('idempotencyKey').equals(key).first(); if (dup) { result = HttpResponse.json(dup, { status: 200 }); return; } }
        if (!wanted.length) { result = bad('Cart is empty', 422); return; }
        const lines: OrderLine[] = [];
        for (const w of wanted) {
          const p = await db.products.get(w.slug);
          const v = p?.variants.find((x) => x.color === w.color && x.size === w.size);
          if (!p || !v) { result = bad(`Unknown product variant: ${w.slug}`, 404); return; }
          if (w.qty > v.stock) { result = bad(`Not enough stock: ${p.name} ${v.size}`, 409, { sku: v.sku, available: v.stock }); return; }
          lines.push({ slug: p.slug, name: p.name, color: v.color, size: v.size, qty: w.qty, unitPrice: p.price });
        }
        // Decrement stock only after every line validated.
        for (const l of lines) {
          const p = (await db.products.get(l.slug))!;
          p.variants.find((x) => x.color === l.color && x.size === l.size)!.stock -= l.qty;
          await db.products.put(p);
        }
        const at = nowIso();
        const order: Order = { id: `ord_${uuid()}`, userId: r.data.userId, email: r.data.email, lines, ...totals(lines), status: 'pending', createdAt: at, updatedAt: at, idempotencyKey: key };
        await db.orders.add(order);
        if (usingCart) await db.cart.clear();
        await db.audit.add({ at, entity: 'order', entityId: order.id, action: 'create', detail: { idempotencyKey: key } });
        result = HttpResponse.json(order, { status: 201 });
      });
      return result!;
    }),

    // Support tickets — idempotent via Idempotency-Key used as the ticket id.
    http.post('*/api/tickets', async ({ request }) => {
      const key = request.headers.get('Idempotency-Key');
      const db = getDb();
      if (key) { const dup = await db.tickets.get(key); if (dup) return HttpResponse.json(dup, { status: 200 }); }
      const r = await parse(TicketCreate, request); if ('res' in r) return r.res;
      const at = nowIso();
      const ticket = { id: key ?? `tkt_${uuid()}`, ...r.data, status: 'open' as const, createdAt: at, updatedAt: at };
      await db.tickets.add(ticket);
      return HttpResponse.json(ticket, { status: 201 });
    }),

    // Newsletter — naturally idempotent on email.
    http.post('*/api/newsletter', async ({ request }) => {
      const r = await parse(NewsletterCreate, request); if ('res' in r) return r.res;
      const db = getDb();
      const existing = await db.newsletter.get(r.data.email);
      if (existing) return HttpResponse.json(existing, { status: 200 });
      const row = { email: r.data.email, subscribedAt: nowIso() };
      await db.newsletter.add(row);
      return HttpResponse.json(row, { status: 201 });
    }),

    // Content
    http.get('*/api/blog', async () => HttpResponse.json(await getDb().posts.orderBy('publishedAt').reverse().toArray())),
    http.get('*/api/blog/:slug', async ({ params }) => {
      const p = await getDb().posts.get(String(params.slug));
      return p ? HttpResponse.json(p) : bad('Post not found', 404);
    }),
    http.get('*/api/faqs', async ({ request }) => {
      const category = new URL(request.url).searchParams.get('category');
      const db = getDb();
      return HttpResponse.json(category ? await db.faqs.where('category').equals(category).toArray() : await db.faqs.toArray());
    }),
  ];
}
