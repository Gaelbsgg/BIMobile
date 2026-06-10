export const companyIdentity = {
  name: 'Acme Indústria & Comércio',
  cnpj: 'CNPJ: 12.345.678/0001-90',
  tokenPlaceholder: 'Ex: ENT-000-XXXXX',
  userPlaceholder: 'ex: joao.silva',
}

export const companyLoginCopy = {
  title: 'Login do Usuário',
  heading: 'Login do Usuário',
  description: 'Por favor, insira suas credenciais de acesso para continuar.',
  cta: 'Conectar ao Dashboard',
  secondary: 'Trocar Empresa',
  footerLeft: 'Ambiente Seguro SSL',
  footerRight: 'Criptografia de Ponta',
  footerNote: '© 2024 Acme Corp HQ. Todos os direitos reservados.',
}

export const companyAuthCopy = {
  title: 'Enterprise Admin',
  subtitle: 'Multi-Org Console',
  heading: 'Acesso ao Sistema',
  description: 'Insira as credenciais da sua organização para autenticação segura.',
  tokenLabel: 'Código da Empresa / Token',
  tokenHint: 'O token foi enviado pelo administrador da conta.',
  cta: 'Continuar',
  links: ['Ajuda', 'Privacidade'],
  badge: 'Conexão Criptografada SSL',
  footerPrefix: 'Não possui um código?',
  footerAction: 'Solicite acesso',
}

export const dashboardCopy = {
  company: companyIdentity.name,
  cnpj: companyIdentity.cnpj,
  nav: [
    { label: 'Visão Geral', icon: 'dashboard', href: '/dashboard', active: true },
    { label: 'Vendas', icon: 'payments', href: '/dashboard/vendas' },
    { label: 'Financeiro', icon: 'account_balance', href: '/dashboard/financeiro' },
    { label: 'Inventário', icon: 'inventory_2', href: '/dashboard/estoque' },
    { label: 'Funcionários', icon: 'badge', href: '/dashboard/funcionarios' },
    { label: 'Configurações', icon: 'settings', href: '/dashboard/configuracoes' },
  ],
  helpLabel: 'Ajuda',
  logoutLabel: 'Sair',
  filters: {
    branch: ['Todas as Filiais', 'Matriz - São Paulo', 'Filial 01 - Rio de Janeiro', 'Filial 02 - Curitiba'],
    dateType: ['Emissão', 'Vencimento', 'Pagamento'],
  },
  kpis: [
    {
      title: 'Total Geral de Vendas',
      value: 'R$ 1.284.500,00',
      note: '+12.5% em relação ao mês anterior',
      icon: 'trending_up',
      tone: 'secondary',
    },
    { title: 'Ticket Médio', value: 'R$ 450,22', tone: 'primary' },
    { title: 'Quantidade de Vendas', value: '2.854', note: 'Meta: 3.000 (95%)', tone: 'primary' },
    { title: 'Total a Receber', value: 'R$ 342.120,50', note: '450 títulos pendentes', tone: 'primary' },
    {
      title: 'Total a Pagar',
      value: 'R$ 185.400,00',
      note: 'Atenção: 12 títulos vencidos',
      icon: 'warning',
      tone: 'error',
    },
    { title: 'Recebido no Período', value: 'R$ 954.200,00', note: 'Inadimplência: 3.2%', tone: 'secondary' },
    { title: 'Pago no Período', value: 'R$ 720.000,00', note: 'Saldo Líquido: + R$ 234k', tone: 'tertiary' },
    { title: 'Valor do Estoque', value: 'R$ 4.520.000,00', note: 'Giro de estoque: 1.5x/mês', tone: 'primary' },
    {
      title: 'Produtos Abaixo do Mínimo',
      value: '42 Itens',
      note: 'Urgente: Reposição necessária',
      tone: 'error',
      accent: true,
    },
  ],
  salesByDay: [
    { percent: 40, tooltip: 'Dia 01: R$ 42k' },
    { percent: 55, tooltip: 'Dia 02: R$ 58k' },
    { percent: 48, tooltip: 'Dia 03: R$ 51k' },
    { percent: 65, tooltip: 'Dia 04: R$ 72k' },
    { percent: 35, tooltip: 'Dia 05: R$ 38k' },
    { percent: 42, tooltip: 'Dia 06: R$ 45k' },
    { percent: 80, tooltip: 'Dia 07: R$ 92k' },
    { percent: 60, tooltip: 'Dia 08: R$ 65k' },
    { percent: 95, tooltip: 'Dia 09: R$ 108k' },
    { percent: 70, tooltip: 'Dia 10: R$ 78k' },
    { percent: 40, tooltip: 'Dia 11: R$ 42k' },
    { percent: 55, tooltip: 'Dia 12: R$ 58k' },
    { percent: 48, tooltip: 'Dia 13: R$ 51k' },
    { percent: 65, tooltip: 'Dia 14: R$ 72k' },
  ],
  salesByBranch: [
    { name: 'Matriz - SP', value: 'R$ 580k', percent: 75 },
    { name: 'Filial RJ', value: 'R$ 410k', percent: 55 },
    { name: 'Filial PR', value: 'R$ 294k', percent: 40 },
  ],
  topSellers: [
    { initials: 'RM', name: 'Ricardo Mendes', unit: 'Unidade São Paulo', value: 'R$ 142.500', meta: '32 vendas', tone: 'secondary' },
    { initials: 'AO', name: 'Ana Oliveira', unit: 'Unidade Curitiba', value: 'R$ 128.900', meta: '28 vendas', tone: 'primary' },
    { initials: 'CP', name: 'Carlos Pereira', unit: 'Unidade Rio de Janeiro', value: 'R$ 98.200', meta: '41 vendas', tone: 'tertiary' },
  ],
  topProducts: [
    {
      name: 'Motor Ind. G-900',
      qty: '145',
      total: 'R$ 242k',
      image:
        'https://lh3.googleusercontent.com/aida-public/AB6AXuCdYXBxWYhPNla6LRepvOtSfNnitPTWoj1i7qzTCWKZMtrjJWuUDRvOBR4D45lTHf4E7Id232c78lLhKsk3peIrU2xWyH-UdWEcerTXtSjUA3pMvpTxUSU5pMXRDjda0EF0qKp1bis2b8iaVn-GGWQfv1h83oe6c1uK0-bAvQN-j2kqnYklKgvNdkIM1CKrhCb_l6DsxqS_6FynVIlJ7HfPAL6GThGLaxnnOeIKYl8GA-VZaq0sTfxwHC6j0kxjsoZ-3AuhkSXVekQ',
    },
    {
      name: 'Controlador Lógico X1',
      qty: '89',
      total: 'R$ 158k',
      image:
        'https://lh3.googleusercontent.com/aida-public/AB6AXuCPAEsDmThsdfa6e8vmXN28srX0aSR-8BCy-_UQCTo290zyukOYkpWaS3Lvg8AqrZlw4nVJH0f7tXCkHStAijoJv5M5MHnfTMbPMdK_q8_Uxy08Do8fvUvzrwLYg1IW6gJvdP36NdmYXujTP6wW5pl8eK6L_vXVxLR1ylWcvYfuWTexidMyq_Yo_0nNjd1p59tNDQr5yuxc52oly-KCxn_jPBpiEJyVhn1k7YU65Ih1nvhP6CRsPaWVKD0qlCTjUu8vQy_kwQdqDTw',
    },
    {
      name: 'Válvula de Fluxo V-2',
      qty: '212',
      total: 'R$ 94k',
      image:
        'https://lh3.googleusercontent.com/aida-public/AB6AXuBWoLzcdouF3BgfSbQBcF-JTwOYa4VK6ao2o5jEUVesh3Lgk6uBNjahGdWsqXcLcZ2T-8kSEakOO3XfnO8o6g7lg8mu8b1v2ykS3-uO7ogpZqvMUQiYhGDdFMeYr6-rrvpKM6gXjAUIwlG550ODtR_hBEdF1IO9XIJV__KSUC-eetBF55LjlJrwHW2arFnUSOu4NYbTzguBTDpnxghf9lpBLmPp6wfl0EjjYEJ4EXtgNutzt3anV0RR-EwCpwNWa9BVB34sY_JN7pY',
    },
  ],
}
