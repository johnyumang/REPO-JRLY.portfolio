import Link from 'next/link';
export const metadata = { title: 'Account' };
export default function Account() {
  return (
    <section className="mx-auto flex min-h-[60vh] max-w-md flex-col justify-center px-4 py-24">
      <h1 className="display text-5xl">Log in</h1>
      <p className="mt-6 text-sm text-muted">Secure sign-in, roles and 2FA are built in Phase 3. This route is reserved so navigation never dead-ends.</p>
      <Link href="/collections/new-in/" className="btn-secondary mt-10 self-start">Continue shopping</Link>
    </section>
  );
}
