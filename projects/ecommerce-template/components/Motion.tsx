'use client';
import { useEffect } from 'react';
import { usePathname } from 'next/navigation';

/** Subtle GSAP scroll reveals (skills pack: gsap-scrolltrigger). Respects reduced motion. */
export default function Motion() {
  const path = usePathname();
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { document.documentElement.classList.add('reduced'); return; }
    let ctx: { revert: () => void } | undefined;
    let cancelled = false;
    (async () => {
      const { gsap } = await import('gsap');
      const { ScrollTrigger } = await import('gsap/ScrollTrigger');
      if (cancelled) return;
      gsap.registerPlugin(ScrollTrigger);
      ctx = gsap.context(() => {
        gsap.utils.toArray<HTMLElement>('.hero-line').forEach((el, i) =>
          gsap.fromTo(el, { yPercent: 110 }, { yPercent: 0, duration: 1.2, ease: 'expo.out', delay: 0.15 + i * 0.12 }));
        gsap.utils.toArray<HTMLElement>('.parallax').forEach((el) =>
          gsap.fromTo(el, { yPercent: -6 }, { yPercent: 6, ease: 'none', scrollTrigger: { trigger: el.parentElement, scrub: true } }));
        ScrollTrigger.batch('.reveal', {
          start: 'top 92%',
          onEnter: (els) => gsap.to(els, { opacity: 1, y: 0, duration: 0.9, ease: 'power3.out', stagger: 0.07, overwrite: true }),
        });
      });
      ScrollTrigger.refresh();
    })();
    return () => { cancelled = true; ctx?.revert(); };
  }, [path]);
  return null;
}
