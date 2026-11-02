/* eslint-disable @next/next/no-img-element */
'use client';
import { useState } from 'react';

const FALLBACK =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 4"><rect width="3" height="4" fill="#121829"/><path d="M1.2 1.7h.6v.6h-.6z" fill="#4169E1" opacity=".5"/></svg>'
  );

type Props = { name: string; alt: string; className?: string; sizes?: string; priority?: boolean };

/** Local stock image with responsive WebP and an offline-safe SVG fallback. */
export default function Img({ name, alt, className = '', sizes = '(min-width: 768px) 25vw, 50vw', priority }: Props) {
  const [failed, setFailed] = useState(false);
  if (failed) return <img src={FALLBACK} alt={alt} className={className} />;
  return (
    <img
      src={`/stock/${name}-800.webp`}
      srcSet={`/stock/${name}-800.webp 800w, /stock/${name}-1400.webp 1400w`}
      sizes={sizes}
      alt={alt}
      loading={priority ? 'eager' : 'lazy'}
      fetchPriority={priority ? 'high' : 'auto'}
      decoding="async"
      onError={() => setFailed(true)}
      className={className}
    />
  );
}
