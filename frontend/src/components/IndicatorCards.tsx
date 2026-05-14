import { Eyebrow } from './Eyebrow';

interface IndicatorCardsProps {
  total: number;
  underReview: number;
  inProduction: number;
  overdue: number;
}

interface Card {
  label: string;
  value: number;
  accent?: boolean;
}

export function IndicatorCards({
  total,
  underReview,
  inProduction,
  overdue,
}: IndicatorCardsProps) {
  const cards: Card[] = [
    { label: 'Manuscripts on the desk', value: total },
    { label: 'Under review', value: underReview },
    { label: 'In production', value: inProduction },
    { label: 'Overdue items', value: overdue, accent: overdue > 0 },
  ];

  return (
    <div className="grid grid-cols-2 gap-px overflow-hidden border border-rule bg-rule sm:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="flex flex-col justify-between gap-3 bg-ink-800 px-6 py-5"
        >
          <Eyebrow>{card.label}</Eyebrow>
          <div
            className={`font-serif text-3xl leading-none ${
              card.accent ? 'text-accent' : 'text-parchment'
            }`}
          >
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
}
