import { MaterialSymbol } from './MaterialSymbol'

export function KpiCard({
  title,
  value,
  note,
  icon,
  tone = 'primary',
  accent = false,
}: {
  title: string
  value: string
  note?: string
  icon?: string
  tone?: 'primary' | 'secondary' | 'tertiary' | 'error'
  accent?: boolean
}) {
  const toneClass =
    tone === 'secondary'
      ? 'text-on-secondary-container'
      : tone === 'tertiary'
        ? 'text-on-tertiary-container'
        : tone === 'error'
          ? 'text-error'
          : 'text-primary'

  const borderClass =
    tone === 'secondary'
      ? 'border-l-4 border-l-secondary'
      : tone === 'tertiary'
        ? 'border-l-4 border-l-tertiary'
        : tone === 'error'
          ? 'border-l-4 border-l-error'
          : 'border-l-4 border-l-transparent'

  return (
    <div className={`rounded-xl border border-outline-variant bg-white p-5 shadow-sm ${accent ? 'bg-error-container/20' : ''} ${borderClass}`}>
      <div className="mb-2 flex items-start justify-between gap-3">
        <p className="text-label-md text-on-surface-variant">{title}</p>
        {icon ? <MaterialSymbol icon={icon} className={toneClass} /> : null}
      </div>
      <h3 className={`text-headline-lg font-bold ${toneClass}`}>{value}</h3>
      {note ? <p className={`mt-1 text-label-sm ${tone === 'error' ? 'text-on-error-container' : 'text-on-surface-variant'}`}>{note}</p> : null}
    </div>
  )
}
