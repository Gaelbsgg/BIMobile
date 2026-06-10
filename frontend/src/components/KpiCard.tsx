export function KpiCard({ label, value, delta }: { label: string; value: string; delta: string }) {
  return (
    <article className="glass rounded-3xl p-5 shadow-glow">
      <p className="text-sm text-slate-400">{label}</p>
      <div className="mt-3 flex items-end justify-between gap-4">
        <strong className="text-3xl font-semibold tracking-tight text-white">{value}</strong>
        <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-300">{delta}</span>
      </div>
    </article>
  )
}
