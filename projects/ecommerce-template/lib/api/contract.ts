// REST contract shared by the MSW mock API (offline) and the live backend (Phase 3+).
import { z } from 'zod';

export const ProductQuery = z.object({
  collection: z.string().max(64).optional(),
  q: z.string().trim().max(100).optional(),
  sort: z.enum(['new', 'price-asc', 'price-desc']).default('new'),
  limit: z.coerce.number().int().min(1).max(100).default(24),
  offset: z.coerce.number().int().min(0).default(0),
});

export const CartAdd = z.object({
  slug: z.string().min(1).max(100),
  color: z.string().min(1).max(64),
  size: z.string().min(1).max(32),
  qty: z.number().int().min(1).max(10).default(1),
});
export const CartPatch = z.object({ qty: z.number().int().min(0).max(10) });

const Email = z.string().trim().toLowerCase().pipe(z.email().max(254));

// Client sends only what it wants; prices are always recomputed from the catalogue.
export const OrderCreate = z.object({
  email: Email,
  userId: z.string().max(64).nullable().default(null),
  lines: z.array(CartAdd.extend({ qty: z.number().int().min(1).max(10) })).min(1).max(50).optional(), // omit → use stored cart
});

export const TicketCreate = z.object({
  email: Email,
  subject: z.string().trim().min(3).max(140),
  message: z.string().trim().min(10).max(5000),
  orderId: z.string().max(64).optional(),
});

export const NewsletterCreate = z.object({ email: Email });

export type ApiError = { error: string; issues?: z.core.$ZodIssue[] };

export const API = {
  collections: '/api/collections',
  products: '/api/products',
  product: (slug: string) => `/api/products/${encodeURIComponent(slug)}`,
  reviews: (slug: string) => `/api/products/${encodeURIComponent(slug)}/reviews`,
  cart: '/api/cart',
  cartLine: (id: string) => `/api/cart/${encodeURIComponent(id)}`,
  wishlist: '/api/wishlist',
  wishlistItem: (slug: string) => `/api/wishlist/${encodeURIComponent(slug)}`,
  orders: '/api/orders',
  tickets: '/api/tickets',
  newsletter: '/api/newsletter',
  posts: '/api/blog',
  post: (slug: string) => `/api/blog/${encodeURIComponent(slug)}`,
  faqs: '/api/faqs',
} as const;
