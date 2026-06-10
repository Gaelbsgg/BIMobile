import { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Sidebar } from '../components/Sidebar'
import { Header } from '../components/Header'
import { FiltersBar } from '../components/FiltersBar'
import { KpiCard } from '../components/KpiCard'
import { ChartCard } from '../components/ChartCard'
import { MaterialSymbol } from '../components/MaterialSymbol'
import { useAuth } from '../contexts/AuthContext'
import { loadDashboard } from '../services/api'
import { dashboardCopy } from '../content/stitchContent'

function FakeAreaBars() {
  return (
    <div className="relative flex h-64 items-end justify-between gap-1 group">
      {dashboardCopy.salesByDay.map((item, index) => (
        <div
          key={`${index}-${item.percent}`}
          className={[
            'relative flex-1 rounded-t-sm transition-all',
            index === 8 ? 'bg-primary/30 hover:bg-primary/50' : index === 3 || index === 6 ? 'bg-primary/20 hover:bg-primary/40' : 'bg-primary/10 hover:bg-primary/30',
          ].join(' ')}
          style={{ height: `${item.percent}%` }}
          title={item.tooltip}
        />
      ))}
    </div>
  )
}

function DashboardModule({ moduleName }: { moduleName: string }) {
  const { accessToken } = useAuth()

  useEffect(() => {
    if (!accessToken) return
    void loadDashboard(moduleName, accessToken)
  }, [accessToken, moduleName])

  if (!['overview', 'vendas', 'financeiro', 'estoque', 'funcionarios', 'configuracoes'].includes(moduleName)) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="space-y-6">
      <FiltersBar />

      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {dashboardCopy.kpis.map((item) => (
          <KpiCard
            key={item.title}
            title={item.title}
            value={item.value}
            note={item.note}
            icon={item.icon}
            tone={item.tone as 'primary' | 'secondary' | 'tertiary' | 'error'}
            accent={item.accent}
          />
        ))}
      </div>

      <div className="grid grid-cols-12 gap-6">
        <ChartCard
          title="Vendas por Dia"
          headerRight={
            <div className="flex gap-2">
              <button className="rounded-full bg-surface-container-high px-3 py-1 text-xs font-semibold" type="button">
                Semana
              </button>
              <button className="rounded-full bg-primary px-3 py-1 text-xs font-semibold text-white" type="button">
                Mês
              </button>
            </div>
          }
          className="col-span-12 lg:col-span-8"
        >
          <FakeAreaBars />

          <div className="mt-4 flex justify-between text-[10px] font-medium text-on-surface-variant">
            <span>OUT 01</span>
            <span>OUT 07</span>
            <span>OUT 14</span>
            <span>OUT 21</span>
            <span>OUT 28</span>
            <span>OUT 31</span>
          </div>
        </ChartCard>

        <ChartCard title="Vendas por Filial" className="col-span-12 lg:col-span-4">
          <div className="space-y-4">
            {dashboardCopy.salesByBranch.map((item) => (
              <div key={item.name}>
                <div className="mb-1 flex justify-between text-body-md">
                  <span className="font-medium">{item.name}</span>
                  <span className="text-on-surface-variant">{item.value}</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-surface-container">
                  <div
                    className={`h-full rounded-full ${item.name === 'Matriz - SP' ? 'bg-primary' : item.name === 'Filial RJ' ? 'bg-primary/70' : 'bg-primary/50'}`}
                    style={{ width: `${item.percent}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 rounded-lg border border-dashed border-outline-variant bg-surface-container-low p-4">
            <p className="text-center text-[11px] italic text-on-surface-variant">As filiais do sul apresentaram crescimento de 8% este mês.</p>
          </div>
        </ChartCard>

        <ChartCard
          title="Top Vendedores"
          headerRight={<MaterialSymbol icon="more_vert" className="cursor-pointer text-primary" />}
          className="col-span-12 md:col-span-6"
        >
          <div className="space-y-4">
            {dashboardCopy.topSellers.map((seller) => (
              <div key={seller.name} className="flex items-center justify-between rounded-lg p-3 transition-colors hover:bg-surface-container-low">
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                      seller.tone === 'secondary'
                        ? 'bg-secondary-fixed text-on-secondary-fixed'
                        : seller.tone === 'tertiary'
                          ? 'bg-tertiary-fixed text-on-tertiary-fixed'
                          : 'bg-primary-fixed text-on-primary-fixed'
                    }`}
                  >
                    {seller.initials}
                  </div>
                  <div>
                    <p className="text-body-md font-semibold">{seller.name}</p>
                    <p className="text-[11px] text-on-surface-variant">{seller.unit}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-body-md font-bold text-on-secondary-container">{seller.value}</p>
                  <p className="text-[10px] text-on-surface-variant">{seller.meta}</p>
                </div>
              </div>
            ))}
          </div>
        </ChartCard>

        <ChartCard
          title="Top Produtos"
          headerRight={<MaterialSymbol icon="sort" className="cursor-pointer text-primary" />}
          className="col-span-12 md:col-span-6"
        >
          <div className="overflow-hidden">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-outline-variant">
                  <th className="pb-3 text-label-md uppercase text-on-surface-variant">Produto</th>
                  <th className="pb-3 text-label-md uppercase text-right text-on-surface-variant">Qtd</th>
                  <th className="pb-3 text-label-md uppercase text-right text-on-surface-variant">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30">
                {dashboardCopy.topProducts.map((product) => (
                  <tr key={product.name}>
                    <td className="py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 overflow-hidden rounded-md bg-surface-container">
                          <img alt="Produto" className="h-full w-full object-cover" src={product.image} />
                        </div>
                        <span className="text-body-md font-medium">{product.name}</span>
                      </div>
                    </td>
                    <td className="py-4 text-right text-body-md">{product.qty}</td>
                    <td className="py-4 text-right text-body-md font-bold">{product.total}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex justify-center">
            <button className="text-label-md text-primary hover:underline" type="button">
              Ver relatório completo
            </button>
          </div>
        </ChartCard>
      </div>
    </div>
  )
}

export function Dashboard() {
  const location = useLocation()

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
    <main className="min-h-screen bg-background text-on-surface">
      <Sidebar />
      <Header />

      <div className="min-h-screen px-gutter pb-12 pt-24 lg:ml-[256px]">
        <DashboardModule moduleName={moduleName} />
      </div>
    </main>
  )
}
