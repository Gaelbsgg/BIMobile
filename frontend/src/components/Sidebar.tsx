import { NavLink } from 'react-router-dom'
import { dashboardCopy } from '../content/stitchContent'
import { MaterialSymbol } from './MaterialSymbol'

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-50 hidden h-full w-[256px] flex-col border-r border-outline-variant bg-surface py-6 px-4 lg:flex">
      <div className="mb-8 flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-white">
          <MaterialSymbol icon="business" className="text-[20px]" />
        </div>
        <div>
          <h2 className="text-headline-md font-bold text-primary">Enterprise Admin</h2>
          <p className="text-label-sm text-on-surface-variant">Multi-Org Console</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1">
        {dashboardCopy.nav.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            end={item.href === '/dashboard'}
            className={({ isActive }) =>
              [
                'flex items-center gap-3 rounded-lg px-4 py-3 transition-transform duration-150',
                isActive
                  ? 'border-r-4 border-primary bg-surface-container-high text-primary font-bold scale-[0.98]'
                  : 'text-on-surface-variant hover:bg-surface-container-high',
              ].join(' ')
            }
          >
            <MaterialSymbol icon={item.icon} className="text-[20px]" filled={item.active} />
            <span className="text-label-md">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto border-t border-outline-variant pt-4">
        <a className="flex items-center gap-3 rounded-lg px-4 py-3 text-on-surface-variant transition-colors hover:bg-surface-container-high" href="#">
          <MaterialSymbol icon="help" className="text-[20px]" />
          <span className="text-label-md">Help Center</span>
        </a>
      </div>
    </aside>
  )
}
