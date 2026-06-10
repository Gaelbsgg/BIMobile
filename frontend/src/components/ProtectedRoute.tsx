import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { accessToken } = useAuth()
  if (!accessToken) {
    return <Navigate to="/login-empresa" replace />
  }
  return <>{children}</>
}
