interface StatCardProps {
  label: string;
  value: number;
  accent: string;
}

export function StatCard({ label, value, accent }: StatCardProps) {
  return (
    <article className="glass-panel p-5">
      <div className={`h-2 w-16 rounded-full ${accent}`} />
      <p className="mt-4 text-sm uppercase tracking-[0.2em] text-slate">{label}</p>
      <p className="mt-2 font-display text-5xl text-ink">{value}</p>
    </article>
  );
}
