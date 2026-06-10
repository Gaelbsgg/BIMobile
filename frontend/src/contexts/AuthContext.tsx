import type { ReactNode } from 'react'
import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { AuthCompany, AuthUser } from '../types/auth'
import { requestCompanyChallenge, loginUser, loadMe } from '../services/api'

type AuthState = {
  accessToken: string | null
  empresaToken: string | null
  company: AuthCompany | null
  user: AuthUser | null
}

type AuthContextValue = AuthState & {
  loading: boolean
  setCompanyChallenge: (token: string) => Promise<AuthCompany>
  login: (params: { username: string; password: string; baseId?: string | null }) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

const storageKey = 'dashboard-web-auth'

function readInitialState(): AuthState {
  const raw = localStorage.getItem(storageKey)
  if (!raw) return { accessToken: null, empresaToken: null, company: null, user: null }
  try {
    return JSON.parse(raw) as AuthState
  } catch {
    return { accessToken: null, empresaToken: null, company: null, user: null }
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => readInitialState())
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(state))
  }, [state])

  useEffect(() => {
    if (!state.accessToken) return
    loadMe(state.accessToken)
      .then((data) => {
        setState((current) => ({
          ...current,
          user: data.user,
          company: current.company ?? data.company,
        }))
      })
      .catch(() => {
        logout()
      })
  }, [state.accessToken])

  async function setCompanyChallenge(token: string) {
    setLoading(true)
    try {
      const result = await requestCompanyChallenge(token)
      setState((current) => ({ ...current, empresaToken: result.empresa_token, company: result.company }))
      return result.company
    } finally {
      setLoading(false)
    }
  }

  async function login(params: { username: string; password: string; baseId?: string | null }) {
    if (!state.empresaToken) {
      throw new Error('Informe o token da empresa primeiro.')
    }
    setLoading(true)
    try {
      const result = await loginUser({
        empresa_token: state.empresaToken,
        username: params.username,
        password: params.password,
        base_id: params.baseId ?? undefined,
      })
      setState((current) => ({
        ...current,
        accessToken: result.access_token,
        user: result.user,
        company: result.company,
      }))
    } finally {
      setLoading(false)
    }
  }

  function logout() {
    setState({ accessToken: null, empresaToken: null, company: null, user: null })
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      loading,
      setCompanyChallenge,
      login,
      logout,
    }),
    [state, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider')
  }
  return context
}
