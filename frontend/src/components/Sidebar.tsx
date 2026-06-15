import { NavLink } from 'react-router-dom'
import { dashboardCopy } from '../content/stitchContent'
import { MaterialSymbol } from './MaterialSymbol'

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-50 hidden h-full w-[72px] flex-col border-r border-white/10 bg-[#040814]/95 px-2 py-3 text-slate-100 backdrop-blur lg:flex">
      <div className="mb-4 flex justify-center">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-white/10 bg-white text-[#07111f] shadow-[0_0_0_1px_rgba(0,0,0,0.25)]">
          <MaterialSymbol icon="assessment" className="text-[18px]" filled />
        </div>
      </div>

      <button
        type="button"
        className="mb-4 flex h-9 w-9 items-center justify-center self-center rounded-full border border-white/10 bg-[#0a1220] text-slate-300 transition-colors hover:bg-[#132035] hover:text-white"
      >
        <MaterialSymbol icon="chevron_right" className="text-[18px]" />
      </button>

      <nav className="flex-1 space-y-3">
        {dashboardCopy.nav.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            end={item.href === '/dashboard'}
            title={item.label}
            className={({ isActive }) =>
              [
                'flex h-11 w-11 items-center justify-center rounded-2xl border transition-all duration-150',
                isActive
                  ? 'border-sky-400/20 bg-[#0d1b31] text-sky-400 shadow-[0_0_0_1px_rgba(56,189,248,0.08)]'
                  : 'border-transparent text-slate-400 hover:border-white/10 hover:bg-[#0d1526] hover:text-slate-100',
              ].join(' ')
            }
          >
            <MaterialSymbol icon={item.icon} className="text-[20px]" filled={item.active} />
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto flex flex-col items-center gap-3 pb-2">
        <a
          className="flex h-9 w-9 items-center justify-center rounded-full border border-white/10 text-slate-400 transition-colors hover:bg-[#0d1526] hover:text-white"
          href="#"
          title={dashboardCopy.helpLabel}
        >
          <MaterialSymbol icon="help" className="text-[18px]" />
        </a>
        <button
          type="button"
          className="flex h-9 w-9 items-center justify-center rounded-full border border-white/10 text-slate-400 transition-colors hover:bg-[#0d1526] hover:text-white"
          title="Tema"
        >
          <MaterialSymbol icon="dark_mode" className="text-[18px]" />
        </button>
      </div>
    </aside>
  )
}
