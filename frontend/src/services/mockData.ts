import { AuthCompany, AuthUser } from '../types/auth'
import { DashboardPayload } from '../types/dashboard'

export const mockCompany: AuthCompany = {
  id: 'demo-company',
  name: 'Empresa Demo',
  token: 'EMP-001',
  bases: [
    { id: 'base-1', name: 'Matriz', alias: 'matriz', host: '127.0.0.1', port: 3050, charset: 'UTF8', status: 'mock' },
    { id: 'base-2', name: 'Filial Sul', alias: 'filial-sul', host: '127.0.0.1', port: 3050, charset: 'UTF8', status: 'mock' },
  ],
}

export const mockUsers: Record<string, { password: string; user: AuthUser }> = {
  admin: {
    password: 'admin123',
    user: {
      id: 'user-admin',
      name: 'Administrador',
      username: 'admin',
      roles: ['admin'],
      permissions: {
        modules: ['overview', 'vendas', 'financeiro', 'estoque', 'funcionarios', 'configuracoes'],
        kpis: ['vendas', 'pedidos', 'margem', 'tickets', 'estoque', 'funcionarios'],
      },
      base_id: 'base-1',
    },
  },
  vendas: {
    password: 'vendas123',
    user: {
      id: 'user-gestor-vendas',
      name: 'Gestor de Vendas',
      username: 'vendas',
      roles: ['user'],
      permissions: {
        modules: ['overview', 'vendas'],
        kpis: ['vendas', 'tickets'],
      },
      base_id: 'base-1',
    },
  },
}

const overview: DashboardPayload = {
  module: 'overview',
  title: 'Visão Geral',
  company: mockCompany.name,
  base: mockCompany.bases[0].name,
  kpis: [
    { label: 'Vendas', value: 'R$ 248.430', delta: '+12,4%', key: 'vendas' },
    { label: 'Pedidos', value: '1.284', delta: '+5,1%', key: 'pedidos' },
    { label: 'Margem', value: '31,8%', delta: '+1,7%', key: 'margem' },
    { label: 'Estoque', value: '92%', delta: '-0,8%', key: 'estoque' },
  ],
  charts: [
    {
      type: 'area',
      title: 'Faturamento mensal',
      data: [
        { name: 'Jan', value: 180 },
        { name: 'Fev', value: 220 },
        { name: 'Mar', value: 190 },
        { name: 'Abr', value: 260 },
        { name: 'Mai', value: 320 },
        { name: 'Jun', value: 310 },
      ],
    },
  ],
}

const vendas: DashboardPayload = {
  module: 'vendas',
  title: 'Vendas',
  kpis: [
    { label: 'Faturamento', value: 'R$ 124.900', delta: '+9,8%', key: 'faturamento' },
    { label: 'Conversão', value: '18,2%', delta: '+0,9%', key: 'conversao' },
  ],
  charts: [
    {
      type: 'bar',
      title: 'Vendas por canal',
      data: [
        { name: 'Loja', value: 84 },
        { name: 'WhatsApp', value: 52 },
        { name: 'Representantes', value: 36 },
      ],
    },
  ],
}

const financeiro: DashboardPayload = {
  module: 'financeiro',
  title: 'Financeiro',
  kpis: [
    { label: 'Recebimentos', value: 'R$ 98.120', delta: '+7,2%', key: 'recebimentos' },
    { label: 'Inadimplência', value: '2,4%', delta: '-0,3%', key: 'inadimplencia' },
  ],
  charts: [
    {
      type: 'line',
      title: 'Fluxo de caixa',
      data: [
        { name: 'Sem 1', value: 80 },
        { name: 'Sem 2', value: 74 },
        { name: 'Sem 3', value: 91 },
        { name: 'Sem 4', value: 88 },
      ],
    },
  ],
}

const estoque: DashboardPayload = {
  module: 'estoque',
  title: 'Estoque',
  kpis: [
    { label: 'SKUs', value: '3.482', delta: '+2,1%', key: 'skus' },
    { label: 'Ruptura', value: '1,1%', delta: '-0,4%', key: 'ruptura' },
  ],
  charts: [
    {
      type: 'area',
      title: 'Cobertura de estoque',
      data: [
        { name: 'A', value: 35 },
        { name: 'B', value: 52 },
        { name: 'C', value: 48 },
        { name: 'D', value: 61 },
      ],
    },
  ],
}

const funcionarios: DashboardPayload = {
  module: 'funcionarios',
  title: 'Funcionários',
  kpis: [
    { label: 'Ativos', value: '128', delta: '+4', key: 'ativos' },
    { label: 'Turnover', value: '3,2%', delta: '-0,7%', key: 'turnover' },
  ],
  charts: [
    {
      type: 'bar',
      title: 'Produtividade por equipe',
      data: [
        { name: 'Comercial', value: 78 },
        { name: 'Financeiro', value: 61 },
        { name: 'Logística', value: 69 },
      ],
    },
  ],
}

export const mockDashboards: Record<string, DashboardPayload> = {
  overview,
  vendas,
  financeiro,
  estoque,
  funcionarios,
}
