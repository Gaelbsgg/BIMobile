import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { companyIdentity, companyLoginCopy } from '../content/stitchContent'
import { MaterialSymbol } from '../components/MaterialSymbol'

export function LoginUsuario() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const { company, login, loading } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    try {
      await login({ username, password })
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha no login')
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background p-gutter">
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-10%] h-[40%] w-[40%] rounded-full bg-primary-fixed opacity-20 blur-[120px]" />
        <div className="absolute bottom-[-5%] left-[-5%] h-[30%] w-[30%] rounded-full bg-primary-container opacity-5 blur-[100px]" />
      </div>

      <div className="stitch-enter relative z-10 w-full max-w-[440px]">
        <div className="glass-card overflow-hidden rounded-xl border border-outline-variant">
          <div className="bg-surface-container-low p-6 border-b border-outline-variant flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-on-primary">
              <MaterialSymbol icon="corporate_fare" className="text-[28px]" />
            </div>
            <div className="flex flex-col">
              <h2 className="text-headline-md text-primary leading-tight">{company?.name ?? companyIdentity.name}</h2>
              <p className="text-label-md uppercase tracking-wider text-on-surface-variant">{companyIdentity.cnpj}</p>
            </div>
          </div>

          <div className="p-8">
            <div className="mb-8 text-center md:text-left">
              <h1 className="mb-2 text-headline-lg text-primary">{companyLoginCopy.heading}</h1>
              <p className="text-body-md text-on-surface-variant">{companyLoginCopy.description}</p>
            </div>

            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <label className="flex items-center gap-1 text-label-md text-on-surface-variant" htmlFor="username">
                  <MaterialSymbol icon="person" className="text-[16px]" />
                  Usuário
                </label>
                <div className="relative group">
                  <input
                    id="username"
                    className="h-12 w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-4 text-body-md font-body-md text-on-surface outline-none transition-all placeholder:text-outline-variant focus:border-primary focus:ring-2 focus:ring-primary-fixed"
                    name="username"
                    onChange={(event) => setUsername(event.target.value)}
                    placeholder={companyIdentity.userPlaceholder}
                    type="text"
                    value={username}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-1 text-label-md text-on-surface-variant" htmlFor="password">
                    <MaterialSymbol icon="lock" className="text-[16px]" />
                    Senha
                  </label>
                  <a className="text-label-sm text-on-surface-variant transition-colors hover:text-primary" href="#">
                    Esqueceu a senha?
                  </a>
                </div>
                <div className="relative group">
                  <input
                    id="password"
                    className="h-12 w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-4 pr-12 text-body-md font-body-md text-on-surface outline-none transition-all placeholder:text-outline-variant focus:border-primary focus:ring-2 focus:ring-primary-fixed"
                    name="password"
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="••••••••"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                  />
                  <button
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant transition-colors hover:text-primary"
                    type="button"
                    onClick={() => setShowPassword((current) => !current)}
                  >
                    <MaterialSymbol icon={showPassword ? 'visibility_off' : 'visibility'} className="text-[20px]" />
                  </button>
                </div>
              </div>

              {error ? <div className="rounded-lg border border-error/20 bg-error-container px-4 py-3 text-sm text-error">{error}</div> : null}

              <button
                className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-primary text-white font-body-md font-semibold shadow-sm transition-all hover:opacity-90 active:scale-[0.98]"
                type="submit"
                disabled={loading}
              >
                {loading ? (
                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                ) : (
                  <>
                    {companyLoginCopy.cta}
                    <MaterialSymbol icon="arrow_forward" className="text-[20px]" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-8 border-t border-outline-variant pt-6 text-center">
              <button
                className="group inline-flex items-center gap-2 px-4 py-2 text-on-surface-variant transition-colors hover:text-primary"
                type="button"
                onClick={() => navigate('/login-empresa')}
              >
                <MaterialSymbol icon="switch_account" className="text-[18px]" />
                <span className="text-label-md">{companyLoginCopy.secondary}</span>
              </button>
            </div>
          </div>
        </div>

        <footer className="mt-8 space-y-4 text-center">
          <div className="flex items-center justify-center gap-6">
            <div className="flex items-center gap-2 text-on-surface-variant">
              <MaterialSymbol icon="verified_user" className="text-[16px]" filled />
              <span className="text-label-sm">{companyLoginCopy.footerLeft}</span>
            </div>
            <div className="flex items-center gap-2 text-on-surface-variant">
              <MaterialSymbol icon="shield" className="text-[16px]" filled />
              <span className="text-label-sm">{companyLoginCopy.footerRight}</span>
            </div>
          </div>
          <p className="text-label-sm text-on-surface-variant/60">{companyLoginCopy.footerNote}</p>
        </footer>
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

      <div className="hidden lg:block absolute right-0 top-0 h-full w-1/3 overflow-hidden">
        <img
          className="h-full w-full object-cover grayscale opacity-20 transition-opacity duration-1000 hover:opacity-30"
          data-alt="A modern architectural glass building reflecting a clear blue sky during sunset."
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuC1SBNhxANciEr4gZHFVCHefA81Ags-RtLnBZ3Pha8wxipMVDawo8smAx-UXyp9Z2e4j6u9_XnrpGm_G2dR7KJzgQy7kwNuHrLGLLcpG6wv3wsnz5rmZJhtsmPJ_fp3sgJWeT6Ae5FGfixxHqcGWXXu3H521JGKMHZugjzNCuwEnLnyygnyyXcqc638wpKDZErjIv6aMOGlTgcxjYbVK-vjOL0jlh9krprjZ7_69inpqQRIRBYy1T_ylUctpaOTLyBc8OrBW4elNr0"
          alt=""
        />
        <div className="absolute inset-0 bg-gradient-to-l from-transparent to-background" />
      </div>
    </main>
  )
}
