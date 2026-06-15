export type Kpi = {
  label: string
  value: string
  delta: string
  key: string
}

export type ChartBlock = {
  type: 'area' | 'bar' | 'line'
  title: string
  data: Array<{ name: string; value: number }>
}

export type DashboardPayload = {
  module: string
  title: string
  company?: string
  base?: string
  kpis: Kpi[]
  charts: ChartBlock[]
  filters?: Record<string, string[]>
}

export type DashboardOverviewResumo = {
  total_geral_vendas: number
  lucro_bruto: number
  ticket_medio: number
  previsto_receber_mes: number
  os_em_servico: number
  os_encerradas: number
  os_canceladas: number
  previsto_pagar_mes: number
  numero_vendas: number
  devolucoes: number
  qtd_produtos_vendidos: number
  orcamentos: number
  autorizacoes_nf: number
  valor_total_estoque: number
  custo_total_estoque: number
  quantidade_total_estoque: number
  estoque_abaixo_minimo: number
  estoque_acima_maximo: number
}
