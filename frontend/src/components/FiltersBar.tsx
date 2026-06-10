import { dashboardCopy } from '../content/stitchContent'

export function FiltersBar() {
  return (
    <section className="mb-8 rounded-xl border border-outline-variant bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-end gap-4">
        <div className="min-w-[200px] flex-1">
          <label className="mb-1.5 block text-label-sm uppercase tracking-wider text-on-surface-variant">Filial</label>
          <select className="h-10 w-full rounded-lg border border-outline-variant bg-surface text-body-md font-body-md outline-none focus:border-primary focus:ring-primary">
            {dashboardCopy.filters.branch.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </div>
        <div className="w-40">
          <label className="mb-1.5 block text-label-sm uppercase tracking-wider text-on-surface-variant">Data Inicial</label>
          <input className="h-10 w-full rounded-lg border border-outline-variant bg-surface text-body-md font-body-md outline-none" type="date" value="2023-10-01" readOnly />
        </div>
        <div className="w-40">
          <label className="mb-1.5 block text-label-sm uppercase tracking-wider text-on-surface-variant">Data Final</label>
          <input className="h-10 w-full rounded-lg border border-outline-variant bg-surface text-body-md font-body-md outline-none" type="date" value="2023-10-31" readOnly />
        </div>
        <div className="w-40">
          <label className="mb-1.5 block text-label-sm uppercase tracking-wider text-on-surface-variant">Tipo de Data</label>
          <select className="h-10 w-full rounded-lg border border-outline-variant bg-surface text-body-md font-body-md outline-none">
            {dashboardCopy.filters.dateType.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </div>
        <button className="flex h-10 items-center gap-2 rounded-lg bg-primary px-8 text-label-md text-white transition-opacity hover:opacity-90" type="button">
          Atualizar
        </button>
      </div>
    </section>
  )
}
