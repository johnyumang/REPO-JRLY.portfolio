import Link from 'next/link';
export default function NotFound() {
  return (
    <section className="mx-auto flex min-h-[60vh] max-w-xl flex-col items-center justify-center px-4 text-center">
      <h1 className="display text-7xl">404</h1>
      <p className="mt-6 text-sm text-muted">This page doesn&apos;t exist.</p>
      <Link href="/" className="btn-secondary mt-10">Back home</Link>
    </section>
  );
}
