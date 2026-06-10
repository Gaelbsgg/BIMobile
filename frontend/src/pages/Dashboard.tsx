import { useEffect, useMemo, useState } from 'react'
import { Sidebar } from '../components/Sidebar'
import { Header } from '../components/Header'
import { FiltersBar } from '../components/FiltersBar'
import { KpiCard } from '../components/KpiCard'
import { ChartCard } from '../components/ChartCard'
import { useAuth } from '../contexts/AuthContext'
import { loadDashboard } from '../services/api'
import { DashboardPayload } from '../types/dashboard'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'

function DashboardModule({ moduleName }: { moduleName: string }) {
  const { accessToken, user } = useAuth()
  const [payload, setPayload] = useState<DashboardPayload | null>(null)
  const [period, setPeriod] = useState('30 dias')

  useEffect(() => {
    if (!accessToken) return
    loadDashboard(moduleName, accessToken).then(setPayload)
  }, [accessToken, moduleName])

  const allowed = user?.permissions.modules ?? []
  if (moduleName !== 'overview' && !allowed.includes(moduleName) && !user?.roles.includes('admin')) {
    return <Navigate to="/dashboard" replace />
  }

  const kpis = useMemo(
    () => payload?.kpis.filter((kpi) => user?.permissions.kpis?.includes(kpi.key) || user?.roles.includes('admin')) ?? [],
    [payload, user],
  )

  if (moduleName === 'configuracoes') {
    return (
      <div className="glass rounded-3xl p-6">
        <h3 className="text-2xl font-semibold text-white">Configurações</h3>
        <p className="mt-2 max-w-2xl text-sm text-slate-300">
          Área reservada para administração de integrações, bases cadastradas, permissões e parâmetros locais da API.
        </p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
            <p className="text-sm text-slate-400">Status</p>
            <p className="mt-2 text-lg text-white">Em preparação</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
            <p className="text-sm text-slate-400">Fonte</p>
            <p className="mt-2 text-lg text-white">JSON local ou SQLite local</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <FiltersBar periods={['Hoje', '7 dias', '30 dias', '90 dias']} selected={period} onChange={setPeriod} />
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <KpiCard key={kpi.key} label={kpi.label} value={kpi.value} delta={kpi.delta} />
        ))}
      </section>
      <section className="grid gap-6 xl:grid-cols-2">
        {payload?.charts.map((chart) => <ChartCard key={chart.title} chart={chart} />)}
      </section>
    </div>
  )
}

export function Dashboard() {
  const { user } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const moduleName = location.pathname.endsWith('/vendas')
    ? 'vendas'
    : location.pathname.endsWith('/financeiro')
      ? 'financeiro'
      : location.pathname.endsWith('/estoque')
        ? 'estoque'
        : location.pathname.endsWith('/funcionarios')
          ? 'funcionarios'
          : location.pathname.endsWith('/configuracoes')
            ? 'configuracoes'
            : 'overview'

  return (
    <main className="mx-auto max-w-7xl px-4 py-4 lg:py-6">
      <div className="grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
        <Sidebar />
        <div className="space-y-6">
          <Header />
          <div className="glass rounded-3xl p-4 lg:hidden">
            <select
              value={location.pathname}
              onChange={(event) => navigate(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none"
            >
              <option value="/dashboard">Visão Geral</option>
              {user?.permissions.modules.includes('vendas') ? <option value="/dashboard/vendas">Vendas</option> : null}
              {user?.permissions.modules.includes('financeiro') ? <option value="/dashboard/financeiro">Financeiro</option> : null}
              {user?.permissions.modules.includes('estoque') ? <option value="/dashboard/estoque">Estoque</option> : null}
              {user?.permissions.modules.includes('funcionarios') ? <option value="/dashboard/funcionarios">Funcionários</option> : null}
            </select>
          </div>
          <DashboardModule moduleName={moduleName} />
        </div>
      </div>
    </main>
  )
}
