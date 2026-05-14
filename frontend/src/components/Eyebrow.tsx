interface EyebrowProps {
  children: React.ReactNode;
}

export function Eyebrow({ children }: EyebrowProps) {
  return <span className="label-eyebrow">{children}</span>;
}
