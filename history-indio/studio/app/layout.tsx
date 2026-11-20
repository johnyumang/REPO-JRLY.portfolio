import type {Metadata} from 'next';
import './globals.css';

export const metadata: Metadata = {title: 'Indio Studio', description: 'Stills to moving shots, shot by shot.'};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
