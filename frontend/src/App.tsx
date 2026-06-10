import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { LoginEmpresa } from './pages/LoginEmpresa'
import { LoginUsuario } from './pages/LoginUsuario'
import { Dashboard } from './pages/Dashboard'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/login-empresa" replace />} />
        <Route path="/login-empresa" element={<LoginEmpresa />} />
        <Route path="/login" element={<LoginUsuario />} />
        <Route
          path="/dashboard/*"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </AuthProvider>
  )
}
