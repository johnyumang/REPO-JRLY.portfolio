import fs from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { collections, products, variantsOf } from '@/content/catalog';
import { faqs, orders, posts, reviews, totals, users } from '@/content/seed';
import { verifyPassword, hashPassword } from '@/lib/crypto';
import { seedDatabase } from '@/lib/seed-db';
import { freshDb } from './helpers';

const stock = new Set(fs.readdirSync(path.resolve(__dirname, '../../public/stock')));

describe('seed data (MASTER-PROMPT §6 counts)', () => {
  it('has 8 collections, 48 products, 6 posts, 30 FAQs, 20 reviews, 5 orders, 3 users', () => {
    expect([collections.length, products.length, posts.length, faqs.length, reviews.length, orders.length, users.length]).toEqual([8, 48, 6, 30, 20, 5, 3]);
  });

  it('has unique slugs and ids', () => {
    for (const list of [products.map((p) => p.slug), collections.map((c) => c.slug), faqs.map((f) => f.id), reviews.map((r) => r.id), orders.map((o) => o.id), users.map((u) => u.email)])
      expect(new Set(list).size).toBe(list.length);
  });

  it('every product has variants, valid collections, and images that exist in public/stock', () => {
    for (const p of products) {
      const v = variantsOf(p);
      expect(v.length).toBe(p.colors.length * p.sizes.length);
      expect(new Set(v.map((x) => x.sku)).size).toBe(v.length);
      for (const c of p.collections) expect(collections.some((x) => x.slug === c)).toBe(true);
      for (const img of [...p.images]) {
        expect(stock.has(`${img}-800.webp`), img).toBe(true);
        expect(stock.has(`${img}-1400.webp`), img).toBe(true);
      }
    }
    for (const c of collections) expect(stock.has(`${c.image}-800.webp`)).toBe(true);
  });

  it('sold-out sizes have zero stock and others are in stock', () => {
    for (const p of products) for (const v of variantsOf(p)) expect(v.stock === 0).toBe(!!p.soldOut?.includes(v.size));
  });

  it('variant stock is deterministic', () => {
    expect(variantsOf(products[0])).toEqual(variantsOf(products[0]));
  });

  it('orders, reviews and posts reference real products / images; order totals add up', () => {
    for (const o of orders) {
      for (const l of o.lines) expect(products.find((p) => p.slug === l.slug)?.price).toBe(l.unitPrice);
      expect(o).toMatchObject(totals(o.lines));
    }
    for (const r of reviews) expect(products.some((p) => p.slug === r.productSlug)).toBe(true);
    for (const p of posts) expect(stock.has(`${p.image}-800.webp`)).toBe(true);
  });

  it('applies shipping below the free threshold only', () => {
    expect(totals([{ qty: 1, unitPrice: 19 }])).toEqual({ subtotal: 19, shipping: 4.95, total: 23.95 });
    expect(totals([{ qty: 2, unitPrice: 25 }])).toEqual({ subtotal: 50, shipping: 0, total: 50 });
    expect(totals([])).toEqual({ subtotal: 0, shipping: 0, total: 0 });
  });

  it('copy stays in template mode', () => {
    for (const p of products) expect(p.description).toMatch(/^\[PRODUCT DESCRIPTION\]/);
    for (const u of users) expect(u.name).toMatch(/^\[.*\]$/);
  });
});

describe('passwords', () => {
  it('seeded users store PBKDF2 hashes that verify against the documented demo passwords', async () => {
    const demo: Record<string, string> = { customer: 'Customer-Demo-2026!', support: 'Support-Demo-2026!', admin: 'Admin-Demo-2026!' };
    for (const u of users) {
      expect(u.passwordHash).toMatch(/^pbkdf2\$sha256\$210000\$/);
      expect(await verifyPassword(demo[u.role], u.passwordHash)).toBe(true);
      expect(await verifyPassword('wrong-password', u.passwordHash)).toBe(false);
    }
  });

  it('hashPassword salts every hash', async () => {
    const [a, b] = [await hashPassword('same', 1000), await hashPassword('same', 1000)];
    expect(a).not.toBe(b);
    expect(await verifyPassword('same', a)).toBe(true);
  });

  it('rejects unknown hash formats', async () => {
    expect(await verifyPassword('x', 'md5$abc')).toBe(false);
  });
});

describe('seedDatabase', () => {
  it('loads every table and is idempotent', async () => {
    const db = await freshDb();
    const counts = async () => Promise.all([db.products.count(), db.collections.count(), db.posts.count(), db.faqs.count(), db.reviews.count(), db.orders.count(), db.users.count()]);
    expect(await counts()).toEqual([48, 8, 6, 30, 20, 5, 3]);
    expect(await seedDatabase(db)).toBe(false);
    expect(await counts()).toEqual([48, 8, 6, 30, 20, 5, 3]);
    expect((await db.products.get(products[0].slug))?.variants.length).toBeGreaterThan(0);
  });

  it('finds products by collection via the multi-entry index', async () => {
    const db = await freshDb();
    const dresses = await db.products.where('collections').equals('dresses').toArray();
    expect(dresses.length).toBe(products.filter((p) => p.collections.includes('dresses')).length);
    expect(dresses.length).toBeGreaterThan(0);
  });
});
