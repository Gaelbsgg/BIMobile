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
