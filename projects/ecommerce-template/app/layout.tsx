import type { Metadata, Viewport } from 'next';
import './globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import Motion from '@/components/Motion';
import { BagProvider } from '@/components/Bag';
import { themeScript } from '@/components/ThemeToggle';
import { BRAND } from '@/content/catalog';
import SW from '@/components/SW';

export const metadata: Metadata = {
  title: { default: `${BRAND} — New Collection`, template: `%s · ${BRAND}` },
  description: '[BRAND] offline-first e-commerce template.',
  manifest: '/manifest.webmanifest',
};
export const viewport: Viewport = {
  themeColor: [{ media: '(prefers-color-scheme: dark)', color: '#0B0F1A' }, { media: '(prefers-color-scheme: light)', color: '#FFFFFF' }],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <head><script dangerouslySetInnerHTML={{ __html: themeScript }} /></head>
      <body>
        <BagProvider>
          <Header />
          <main id="main">{children}</main>
          <Footer />
        </BagProvider>
        <Motion />
        <SW />
      </body>
    </html>
  );
}
