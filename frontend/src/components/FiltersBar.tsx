export function FiltersBar({
  periods,
  selected,
  onChange,
}: {
  periods: string[]
  selected: string
  onChange: (value: string) => void
}) {
  return (
    <div className="glass flex flex-wrap items-center gap-3 rounded-3xl p-4">
      <span className="text-sm text-slate-400">Período</span>
      <div className="flex flex-wrap gap-2">
        {periods.map((period) => (
          <button
            key={period}
            type="button"
            onClick={() => onChange(period)}
            className={[
              'rounded-full px-4 py-2 text-sm transition',
              selected === period ? 'bg-gold-400 text-ink-950 font-semibold' : 'bg-white/5 text-slate-300 hover:bg-white/10',
            ].join(' ')}
          >
            {period}
          </button>
        ))}
      </div>
    </div>
  )
}
