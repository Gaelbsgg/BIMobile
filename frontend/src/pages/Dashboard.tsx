import { useEffect, useState, type ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Sidebar } from '../components/Sidebar'
import { Header } from '../components/Header'
import { FiltersBar } from '../components/FiltersBar'
import { KpiCard } from '../components/KpiCard'
import { ChartCard } from '../components/ChartCard'
import { MaterialSymbol } from '../components/MaterialSymbol'
import { useAuth } from '../contexts/AuthContext'
import { loadDashboard, loadOverviewResumo } from '../services/api'
import { mockOverviewResumo } from '../services/mockData'
import { DashboardOverviewResumo } from '../types/dashboard'
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

type OverviewTone = 'positive' | 'info' | 'negative'

function formatCurrency(value: number) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 }).format(value)
}

function formatInteger(value: number) {
  return new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 }).format(value)
}

function OverviewKpiCard({
  title,
  value,
  description,
  icon,
  tone = 'info',
}: {
  title: string
  value: string
  description: string
  icon: string
  tone?: OverviewTone
}) {
  const toneStyles =
    tone === 'positive'
      ? {
          card: 'border-emerald-400/20 bg-emerald-500/10',
          icon: 'bg-emerald-500/15 text-emerald-300',
          title: 'text-emerald-200',
          value: 'text-emerald-100',
        }
      : tone === 'negative'
        ? {
            card: 'border-rose-400/20 bg-rose-500/10',
            icon: 'bg-rose-500/15 text-rose-300',
            title: 'text-rose-200',
            value: 'text-rose-50',
          }
        : {
            card: 'border-sky-400/20 bg-sky-500/10',
            icon: 'bg-sky-500/15 text-sky-300',
            title: 'text-sky-200',
            value: 'text-slate-50',
          }

  return (
    <article className={`rounded-2xl border p-5 shadow-[0_20px_60px_rgba(2,6,23,0.35)] backdrop-blur ${toneStyles.card}`}>
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${toneStyles.icon}`}>
          <MaterialSymbol icon={icon} className="text-[20px]" filled />
        </div>
      </div>
      <p className={`text-[11px] font-semibold uppercase tracking-[0.24em] ${toneStyles.title}`}>{title}</p>
      <p className={`mt-2 text-2xl font-extrabold tracking-tight ${toneStyles.value}`}>{value}</p>
      <p className="mt-2 text-sm leading-5 text-slate-300">{description}</p>
    </article>
  )
}

function OverviewSection({
  title,
  subtitle,
  columnsClass,
  children,
}: {
  title: string
  subtitle: string
  columnsClass: string
  children: ReactNode
}) {
  return (
    <section className="space-y-4">
      <div className="space-y-1">
        <h2 className="text-sm font-extrabold uppercase tracking-[0.28em] text-slate-100">{title}</h2>
        <p className="text-sm text-slate-400">{subtitle}</p>
      </div>
      <div className={`grid grid-cols-1 gap-4 md:grid-cols-2 ${columnsClass}`}>{children}</div>
    </section>
  )
}

function OverviewModule() {
  const { accessToken } = useAuth()
  const [overview, setOverview] = useState<DashboardOverviewResumo>(mockOverviewResumo)

  useEffect(() => {
    if (!accessToken) return
    void loadOverviewResumo(accessToken).then(setOverview)
  }, [accessToken])

  return (
    <div className="space-y-6">
      <div className="rounded-[32px] border border-white/10 bg-[#07111f] px-5 py-6 shadow-[0_40px_120px_rgba(0,0,0,0.4)] lg:px-6">
        <FiltersBar />

        <div className="mt-6 space-y-8">
          <OverviewSection title="KPIs CRÍTICOS" subtitle="Leitura rápida do negócio em segundos" columnsClass="xl:grid-cols-4">
            <OverviewKpiCard
              title="TOTAL GERAL DE VENDAS (R$)"
              value={formatCurrency(overview.total_geral_vendas)}
              description="Valor total vendido no período selecionado."
              icon="payments"
              tone="positive"
            />
            <OverviewKpiCard
              title="LUCRO BRUTO (R$)"
              value={formatCurrency(overview.lucro_bruto)}
              description="Diferença entre o valor vendido e o custo dos produtos ou serviços."
              icon="trending_up"
              tone="positive"
            />
            <OverviewKpiCard
              title="TICKET MÉDIO"
              value={formatCurrency(overview.ticket_medio)}
              description="Valor médio de cada venda realizada no período."
              icon="sell"
              tone="info"
            />
            <OverviewKpiCard
              title="PREVISTO A RECEBER (MÊS)"
              value={formatCurrency(overview.previsto_receber_mes)}
              description="Valor que a empresa ainda tem para receber dos clientes."
              icon="account_balance_wallet"
              tone="positive"
            />
            <OverviewKpiCard
              title="O.S EM SERVIÇO"
              value={formatInteger(overview.os_em_servico)}
              description="Ordens de Serviço que ainda estão em andamento."
              icon="construction"
              tone="info"
            />
            <OverviewKpiCard
              title="O.S ENCERRADAS"
              value={formatInteger(overview.os_encerradas)}
              description="Ordens de Serviço concluídas no período."
              icon="task_alt"
              tone="positive"
            />
            <OverviewKpiCard
              title="O.S CANCELADAS"
              value={formatInteger(overview.os_canceladas)}
              description="Ordens de Serviço canceladas no período."
              icon="cancel"
              tone="negative"
            />
            <OverviewKpiCard
              title="PREVISTO A PAGAR (MÊS)"
              value={formatCurrency(overview.previsto_pagar_mes)}
              description="Valor que a empresa ainda possui de compromissos financeiros a pagar."
              icon="payments"
              tone="negative"
            />
          </OverviewSection>

          <OverviewSection title="OPERACIONAL" subtitle="Indicadores de execução e volume" columnsClass="xl:grid-cols-5">
            <OverviewKpiCard
              title="NÚMERO DE VENDAS"
              value={formatInteger(overview.numero_vendas)}
              description="Quantidade total de Ordens de Serviço registradas no período."
              icon="point_of_sale"
              tone="info"
            />
            <OverviewKpiCard
              title="DEVOLUÇÕES"
              value={formatInteger(overview.devolucoes)}
              description="Quantidade de vendas devolvidas pelos clientes no período."
              icon="keyboard_return"
              tone="negative"
            />
            <OverviewKpiCard
              title="QTD. PRODUTOS VENDIDOS"
              value={formatNumber(overview.qtd_produtos_vendidos)}
              description="Quantidade total de itens vendidos no período."
              icon="inventory_2"
              tone="info"
            />
            <OverviewKpiCard
              title="ORÇAMENTOS"
              value={formatInteger(overview.orcamentos)}
              description="Quantidade de orçamentos registrados no período."
              icon="description"
              tone="info"
            />
            <OverviewKpiCard
              title="AUTORIZAÇÕES NF"
              value={formatInteger(overview.autorizacoes_nf)}
              description="Quantidade de notas fiscais autorizadas no período."
              icon="receipt_long"
              tone="positive"
            />
          </OverviewSection>

          <OverviewSection title="VALOR TOTAL DO ESTOQUE (R$)" subtitle="Indicadores" columnsClass="xl:grid-cols-5">
            <OverviewKpiCard
              title="VALOR TOTAL DO ESTOQUE (R$)"
              value={formatCurrency(overview.valor_total_estoque)}
              description="Valor de venda dos itens atualmente em estoque."
              icon="inventory"
              tone="info"
            />
            <OverviewKpiCard
              title="CUSTO TOTAL DO ESTOQUE (R$)"
              value={formatCurrency(overview.custo_total_estoque)}
              description="Custo de aquisição dos itens atualmente em estoque."
              icon="sell"
              tone="info"
            />
            <OverviewKpiCard
              title="QUANTIDADE TOTAL EM ESTOQUE"
              value={formatNumber(overview.quantidade_total_estoque)}
              description="Quantidade consolidada dos itens disponíveis."
              icon="view_in_ar"
              tone="info"
            />
            <OverviewKpiCard
              title="ESTOQUE ABAIXO DO MÍNIMO"
              value={formatInteger(overview.estoque_abaixo_minimo)}
              description="Itens que exigem atenção imediata de reposição."
              icon="warning"
              tone="negative"
            />
            <OverviewKpiCard
              title="ESTOQUE ACIMA DO MÁXIMO"
              value={formatInteger(overview.estoque_acima_maximo)}
              description="Itens com saldo acima do limite configurado."
              icon="north"
              tone="negative"
            />
          </OverviewSection>
        </div>
      </div>
    </div>
  )
}

function LegacyDashboardModule({ moduleName }: { moduleName: string }) {
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

      <div className={`min-h-screen px-gutter pb-12 pt-24 lg:ml-[256px] ${moduleName === 'overview' ? 'bg-[#07111f] text-slate-100' : ''}`}>
        {moduleName === 'overview' ? <OverviewModule /> : <LegacyDashboardModule moduleName={moduleName} />}
      </div>
    </main>
  )
}
