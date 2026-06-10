import { useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export function Header() {
  const { user, company, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="glass flex flex-wrap items-center justify-between gap-4 rounded-3xl px-5 py-4 shadow-glow">
      <div>
        <p className="text-xs uppercase tracking-[0.25em] text-gold-400">Dashboard</p>
        <h2 className="text-2xl font-semibold text-white">Operação multiempresa</h2>
        <p className="text-sm text-slate-300">
          {company?.name ?? 'Empresa'} · {user?.name ?? 'Usuário'}
        </p>
      </div>
      <button
        type="button"
        onClick={() => {
          logout()
          navigate('/login-empresa')
        }}
        className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 transition hover:bg-white/10"
      >
        <LogOut size={16} />
        Sair
      </button>
    </header>
  )
}
