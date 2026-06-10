import axios from 'axios'
import { AuthCompany, AuthUser } from '../types/auth'
import { DashboardPayload } from '../types/dashboard'
import { mockCompany, mockDashboards, mockUsers } from './mockData'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 4000,
})

const useMocks = import.meta.env.VITE_USE_MOCKS === 'true'

type EmpresaChallengeResponse = {
  empresa_token: string
  company: AuthCompany
}

type LoginResponse = {
  access_token: string
  token_type: string
  user: AuthUser
  company: AuthCompany
}

async function tryRequest<T>(fn: () => Promise<T>, fallback: () => Promise<T>): Promise<T> {
  if (useMocks) return fallback()
  try {
    return await fn()
  } catch {
    return fallback()
  }
}

export async function requestCompanyChallenge(token: string): Promise<EmpresaChallengeResponse> {
  return tryRequest(
    async () => {
      const { data } = await api.post<EmpresaChallengeResponse>('/auth/empresa', { token })
      return data
    },
    async () => ({
      empresa_token: `mock-company-token:${token}`,
      company: mockCompany,
    }),
  )
}

export async function loginUser(params: {
  empresa_token: string
  username: string
  password: string
  base_id?: string
}): Promise<LoginResponse> {
  return tryRequest(
    async () => {
      const { data } = await api.post<LoginResponse>('/auth/login', params)
      return data
    },
    async () => {
      const matched = mockUsers[params.username]
      if (!matched || matched.password !== params.password) {
        throw new Error('Credenciais inválidas')
      }
      return {
        access_token: `mock-access-token:${matched.user.username}`,
        token_type: 'bearer',
        user: matched.user,
        company: mockCompany,
      }
    },
  )
}

export async function loadMe(token: string) {
  return tryRequest(
    async () => {
      const { data } = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      })
      return data
    },
    async () => ({
      user: mockUsers[token.split(':').pop() || 'admin']?.user ?? mockUsers.admin.user,
      company: mockCompany,
    }),
  )
}

export async function loadDashboard(moduleName: string, token: string): Promise<DashboardPayload> {
  return tryRequest(
    async () => {
      const { data } = await api.get(`/dashboard/${moduleName}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      return data
    },
    async () => mockDashboards[moduleName] ?? mockDashboards.overview,
  )
}
