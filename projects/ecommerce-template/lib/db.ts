// IndexedDB schema (Dexie). The same shapes back the MSW mock API and the future live API.
import Dexie, { type Table } from 'dexie';
import type { Product, Variant } from '@/content/catalog';
import type { Faq, Order, Post, Review, User } from '@/content/seed';

export type ProductRow = Product & { variants: Variant[] };
export type CollectionRow = { slug: string; title: string; image: string };
export type CartLine = { id: string; slug: string; color: string; size: string; qty: number; updatedAt: string };
export type WishlistRow = { slug: string; addedAt: string };
export type Ticket = {
  id: string; email: string; subject: string; message: string; orderId?: string;
  status: 'open' | 'pending' | 'resolved'; createdAt: string; updatedAt: string;
};
export type ChatMessage = { id?: number; sessionId: string; role: 'user' | 'bot' | 'agent'; text: string; at: string };
export type NewsletterRow = { email: string; subscribedAt: string };
export type OutboxStatus = 'pending' | 'failed';
export type OutboxItem = {
  id: string; // doubles as the Idempotency-Key sent on replay
  type: 'order' | 'ticket' | 'newsletter';
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  path: string;
  body: unknown;
  status: OutboxStatus;
  attempts: number;
  nextAttemptAt: number; // epoch ms
  lastError?: string;
  createdAt: string;
};
export type AuditEntry = { id?: number; at: string; entity: string; entityId: string; action: string; detail?: unknown };
export type MetaRow = { key: string; value: unknown };

export class TemplateDB extends Dexie {
  products!: Table<ProductRow, string>;
  collections!: Table<CollectionRow, string>;
  cart!: Table<CartLine, string>;
  wishlist!: Table<WishlistRow, string>;
  orders!: Table<Order, string>;
  users!: Table<User, string>;
  posts!: Table<Post, string>;
  faqs!: Table<Faq, string>;
  reviews!: Table<Review, string>;
  tickets!: Table<Ticket, string>;
  chat!: Table<ChatMessage, number>;
  newsletter!: Table<NewsletterRow, string>;
  outbox!: Table<OutboxItem, string>;
  audit!: Table<AuditEntry, number>;
  meta!: Table<MetaRow, string>;

  constructor(name = 'tpl-store') {
    super(name);
    this.version(1).stores({
      products: 'slug, *collections, price, createdAt',
      collections: 'slug',
      cart: 'id, slug',
      wishlist: 'slug',
      orders: 'id, userId, createdAt, status, &idempotencyKey',
      users: 'id, &email, role',
      posts: 'slug, publishedAt, *tags',
      faqs: 'id, category',
      reviews: 'id, productSlug, createdAt',
      tickets: 'id, email, status, createdAt',
      chat: '++id, sessionId, at',
      newsletter: 'email',
      outbox: 'id, status, nextAttemptAt, createdAt',
      audit: '++id, at, entity, entityId, action',
      meta: 'key',
    });
  }
}

let shared: TemplateDB | undefined;
export const getDB = () => (shared ??= new TemplateDB());

export const cartLineId = (l: { slug: string; color: string; size: string }) => `${l.slug}|${l.color}|${l.size}`;
export const nowIso = () => new Date().toISOString();
