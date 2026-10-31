// Loads placeholder content into IndexedDB once per SEED_VERSION. Safe to call on every page load.
import { collections, products, variantsOf } from '@/content/catalog';
import { faqs, orders, posts, reviews, SEED_VERSION, users } from '@/content/seed';
import type { TemplateDB } from './db';

export async function seedDatabase(db: TemplateDB) {
  const current = await db.meta.get('seedVersion');
  if (current?.value === SEED_VERSION) return false;
  await db.transaction('rw', [db.products, db.collections, db.users, db.posts, db.faqs, db.reviews, db.orders, db.meta], async () => {
    await db.products.bulkPut(products.map((p) => ({ ...p, variants: variantsOf(p) })));
    await db.collections.bulkPut(collections.map((c) => ({ ...c })));
    await db.users.bulkPut(users);
    await db.posts.bulkPut(posts);
    await db.faqs.bulkPut(faqs);
    await db.reviews.bulkPut(reviews);
    await db.orders.bulkPut(orders);
    await db.meta.put({ key: 'seedVersion', value: SEED_VERSION });
  });
  return true;
}
