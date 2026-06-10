import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { companyAuthCopy } from '../content/stitchContent'
import { MaterialSymbol } from '../components/MaterialSymbol'
import { companyIdentity } from '../content/stitchContent'

export function LoginEmpresa() {
  const [token, setToken] = useState('EMP-001')
  const [error, setError] = useState('')
  const { setCompanyChallenge, loading } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    try {
      await setCompanyChallenge(token)
      navigate('/login-usuario')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao validar token da empresa')
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background p-gutter">
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute right-[-10%] top-[-10%] h-[40%] w-[40%] rounded-full bg-primary-fixed opacity-20 blur-[120px]" />
        <div className="absolute bottom-[-5%] left-[-5%] h-[30%] w-[30%] rounded-full bg-primary-container opacity-5 blur-[100px]" />
      </div>

      <div className="stitch-enter relative z-10 w-full max-w-[440px]">
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary shadow-[0_10px_15px_-3px_rgba(9,20,38,0.2)]">
            <MaterialSymbol icon="shield_person" className="text-[28px] text-white" filled />
          </div>
          <h1 className="text-headline-md tracking-tight text-primary">{companyAuthCopy.title}</h1>
          <p className="mt-1 text-label-md uppercase text-on-surface-variant">{companyAuthCopy.subtitle}</p>
        </div>

        <div className="glass-card overflow-hidden rounded-xl border border-outline-variant">
          <div className="p-8 md:p-10">
            <div className="mb-8 text-center">
              <h2 className="mb-2 text-headline-md text-on-surface">{companyAuthCopy.heading}</h2>
              <p className="text-body-md text-on-surface-variant">{companyAuthCopy.description}</p>
            </div>

            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <label className="ml-1 block text-label-md text-on-surface-variant" htmlFor="token">
                  {companyAuthCopy.tokenLabel}
                </label>
                <div className="relative group focused-input">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-outline group-focus-within:text-primary transition-colors">
                    <MaterialSymbol icon="vpn_key" className="text-[20px]" />
                  </div>
                  <input
                    id="token"
                    value={token}
                    onChange={(event) => setToken(event.target.value)}
                    className="h-12 w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-4 pl-11 text-body-md font-body-md text-on-surface outline-none transition-all placeholder:text-outline-variant focus:border-primary focus:ring-2 focus:ring-primary-fixed"
                    placeholder={companyIdentity.tokenPlaceholder}
                    type="text"
                  />
                </div>
                <p className="ml-1 flex items-center gap-1.5 pt-1 text-label-sm text-outline-variant">
                  <MaterialSymbol icon="info" className="text-[14px]" />
                  {companyAuthCopy.tokenHint}
                </p>
              </div>

              {error ? <div className="rounded-lg border border-error/20 bg-error-container px-4 py-3 text-sm text-error">{error}</div> : null}

            <button
                className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-primary text-white font-body-md font-semibold shadow-sm transition-all hover:opacity-90 active:scale-[0.98]"
                type="submit"
                disabled={loading}
              >
                {loading ? <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/30 border-t-white" /> : companyAuthCopy.cta}
                {!loading ? <MaterialSymbol icon="arrow_forward" className="text-[20px]" /> : null}
              </button>
            </form>

            <div className="mt-8 flex flex-col items-center gap-4 border-t border-outline-variant pt-8">
              <div className="flex items-center gap-4 text-outline">
                {companyAuthCopy.links.map((link, index) => (
                  <span key={link} className="flex items-center gap-4">
                    <a className="text-label-md text-outline hover:text-primary transition-colors" href="#">
                      {link}
                    </a>
                    {index === 0 ? <span className="h-1 w-1 rounded-full bg-outline-variant" /> : null}
                  </span>
                ))}
              </div>
              <div className="flex items-center gap-2 rounded-full border border-outline-variant/30 bg-surface-container px-3 py-1.5">
                <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-on-secondary-container" />
                <span className="text-label-sm text-on-surface-variant">{companyAuthCopy.badge}</span>
              </div>
            </div>
          </div>
        </div>

        <p className="mt-8 text-center text-body-md text-on-surface-variant">
          {companyAuthCopy.footerPrefix}{' '}
          <a className="font-semibold text-primary hover:underline" href="#">
            {companyAuthCopy.footerAction}
          </a>
        </p>
      </div>

      <div className="fixed bottom-0 left-0 z-0 hidden p-gutter opacity-20 md:block">
        <div className="flex flex-col gap-2">
          <div className="flex gap-2">
            <div className="h-3 w-3 rounded-sm bg-primary-fixed" />
            <div className="h-3 w-3 rounded-sm bg-outline-variant" />
          </div>
          <div className="flex gap-2">
            <div className="h-3 w-3 rounded-sm bg-outline-variant" />
            <div className="h-3 w-3 rounded-sm bg-primary-fixed" />
          </div>
        </div>
      </div>

    </main>
  )
}
