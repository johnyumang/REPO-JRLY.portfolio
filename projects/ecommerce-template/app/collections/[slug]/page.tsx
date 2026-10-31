import { notFound } from 'next/navigation';
import CollectionView from './CollectionView';
import { collections, inCollection } from '@/content/catalog';

export const dynamicParams = false;
export function generateStaticParams() { return collections.map((c) => ({ slug: c.slug })); }

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return { title: collections.find((c) => c.slug === slug)?.title ?? 'Collection' };
}

export default async function Collection({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const c = collections.find((x) => x.slug === slug);
  if (!c) notFound();
  return <CollectionView title={c.title} slug={c.slug} items={inCollection(c.slug)} />;
}
