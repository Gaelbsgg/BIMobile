import { NavLink } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const items = [
  { to: '/dashboard', label: 'Visão Geral', module: 'overview' },
  { to: '/dashboard/vendas', label: 'Vendas', module: 'vendas' },
  { to: '/dashboard/financeiro', label: 'Financeiro', module: 'financeiro' },
  { to: '/dashboard/estoque', label: 'Estoque', module: 'estoque' },
  { to: '/dashboard/funcionarios', label: 'Funcionários', module: 'funcionarios' },
  { to: '/dashboard/configuracoes', label: 'Configurações', module: 'configuracoes' },
]

export function Sidebar() {
  const { user, company } = useAuth()
  const permissions = user?.permissions?.modules ?? []

  return (
    <aside className="glass hidden min-h-[calc(100vh-2rem)] w-72 flex-col rounded-3xl p-5 shadow-glow lg:flex">
      <div className="mb-8 rounded-2xl border border-white/10 bg-white/5 p-4">
        <p className="text-xs uppercase tracking-[0.25em] text-gold-400">Multiempresa</p>
        <h1 className="mt-2 text-xl font-semibold text-white">{company?.name ?? 'Dashboard'}</h1>
        <p className="mt-1 text-sm text-slate-300">Portal analítico com base local Firebird</p>
      </div>
      <nav className="space-y-2">
        {items
          .filter((item) => permissions.includes(item.module) || item.module === 'overview')
          .map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/dashboard'}
              className={({ isActive }) =>
                [
                  'block rounded-2xl px-4 py-3 text-sm transition',
                  isActive ? 'bg-gold-400/15 text-gold-400 ring-1 ring-gold-400/30' : 'text-slate-300 hover:bg-white/5 hover:text-white',
                ].join(' ')
              }
            >
              {item.label}
            </NavLink>
          ))}
      </nav>
      <div className="mt-auto rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-300">
        Permissões vindas do JWT. Menus sem acesso não aparecem.
      </div>
    </aside>
  )
}
