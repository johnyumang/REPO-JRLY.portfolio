import { ShieldIcon, TruckIcon, ReturnIcon, StarIcon, MoneyIcon } from './Icons';
import { FREE_SHIPPING_OVER, CURRENCY } from '@/content/catalog';

const ALL = [
  { id: 'secure', Icon: ShieldIcon, title: 'Secure checkout', text: 'SSL encrypted payments' },
  { id: 'shipping', Icon: TruckIcon, title: 'Free shipping', text: `On orders over ${FREE_SHIPPING_OVER} ${CURRENCY}` },
  { id: 'returns', Icon: ReturnIcon, title: '30-day returns', text: 'Free and easy' },
  { id: 'guarantee', Icon: MoneyIcon, title: 'Money-back guarantee', text: 'Full refund, no questions' },
  { id: 'reviews', Icon: StarIcon, title: 'Verified reviews', text: '4.8 / 5 from [N] customers' },
];

export function TrustBadges({ compact = false, only }: { compact?: boolean; only?: string[] }) {
  const items = only ? ALL.filter((b) => only.includes(b.id)) : ALL;
  if (compact)
    return (
      <ul className="grid grid-cols-1 gap-3 border-t border-line pt-5 sm:grid-cols-3" aria-label="Why shop with us">
        {items.map(({ id, Icon, title }) => (
          <li key={id} className="flex items-center gap-3 text-[12px] text-muted"><Icon /><span>{title}</span></li>
        ))}
      </ul>
    );
  return (
    <ul className="grid grid-cols-2 gap-y-10 border-y border-line py-12 md:grid-cols-5" aria-label="Why shop with us">
      {items.map(({ id, Icon, title, text }) => (
        <li key={id} className="reveal flex flex-col items-center gap-3 px-3 text-center">
          <Icon />
          <span className="label">{title}</span>
          <span className="text-[12px] text-muted">{text}</span>
        </li>
      ))}
    </ul>
  );
}

export function PaymentIcons() {
  const methods = ['VISA', 'MASTERCARD', 'AMEX', 'PAYPAL', 'APPLE PAY', 'GOOGLE PAY'];
  return (
    <ul className="flex flex-wrap gap-2" aria-label="Accepted payment methods">
      {methods.map((m) => (
        <li key={m} className="border border-line px-2 py-1 text-[9px] font-semibold tracking-label text-muted">{m}</li>
      ))}
    </ul>
  );
}
