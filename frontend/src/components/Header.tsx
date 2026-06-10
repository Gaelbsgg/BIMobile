import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { dashboardCopy } from '../content/stitchContent'
import { MaterialSymbol } from './MaterialSymbol'

export function Header() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="fixed top-0 right-0 left-0 z-40 flex h-16 items-center justify-between border-b border-outline-variant bg-surface-container-lowest px-gutter shadow-sm lg:left-[256px]">
      <div className="flex items-center gap-6">
        <div>
          <h1 className="text-headline-md font-extrabold text-primary">{dashboardCopy.company}</h1>
          <p className="text-[10px] leading-none text-on-surface-variant">{dashboardCopy.cnpj}</p>
        </div>
        <div className="ml-4 hidden gap-4 md:flex">
          <a className="text-label-md text-on-surface-variant transition-colors hover:text-primary" href="#">
            Branch Portal
          </a>
          <a className="text-label-md text-on-surface-variant transition-colors hover:text-primary" href="#">
            Global Reports
          </a>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="mr-2 flex flex-col items-end">
          <span className="text-label-md font-semibold text-primary">{dashboardCopy.userName}</span>
          <span className="text-label-sm text-on-surface-variant">{dashboardCopy.userRole}</span>
        </div>
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-full bg-surface-container transition-colors hover:bg-surface-container-high"
        >
          <MaterialSymbol icon="notifications" className="text-primary" />
        </button>
        <button
          type="button"
          onClick={() => {
            logout()
            navigate('/login-empresa')
          }}
          className="flex items-center gap-2 rounded-lg border border-outline-variant px-4 py-2 text-label-md text-primary transition-all hover:bg-surface-container"
        >
          <MaterialSymbol icon="logout" className="text-[18px]" />
          Logout
        </button>
      </div>
    </header>
  )
}
