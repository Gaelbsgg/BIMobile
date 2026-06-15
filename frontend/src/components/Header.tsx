import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { dashboardCopy } from '../content/stitchContent'
import { MaterialSymbol } from './MaterialSymbol'

export function Header() {
  const { logout, user } = useAuth()
  const navigate = useNavigate()
  const displayName = user?.name || user?.username || 'Usuário'

  return (
    <header className="fixed top-0 right-0 left-0 z-40 flex h-16 items-center justify-between border-b border-white/10 bg-[#040814]/95 px-gutter text-slate-100 backdrop-blur lg:left-[72px]">
      <div className="flex items-center gap-6">
        <div>
          <h1 className="text-[14px] font-extrabold tracking-tight text-white">{dashboardCopy.company}</h1>
          <p className="text-[10px] leading-none text-slate-400">{dashboardCopy.cnpj}</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="mr-2 flex flex-col items-end">
          <span className="text-sm font-semibold text-slate-100">{displayName}</span>
        </div>
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-[#0a1220] text-slate-300 transition-colors hover:bg-[#132035] hover:text-white"
        >
          <MaterialSymbol icon="notifications" className="text-[20px]" />
        </button>
        <button
          type="button"
          onClick={() => {
            logout()
            navigate('/login-empresa')
          }}
          className="flex items-center gap-2 rounded-full border border-sky-400/15 bg-[#0b1a31] px-4 py-2 text-sm font-semibold text-sky-300 transition-all hover:bg-[#11284a]"
        >
          <MaterialSymbol icon="logout" className="text-[18px]" />
          {dashboardCopy.logoutLabel}
        </button>
      </div>
    </header>
  )
}
