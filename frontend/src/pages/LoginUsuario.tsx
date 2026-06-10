import { FormEvent, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export function LoginUsuario() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [baseId, setBaseId] = useState('base-1')
  const [error, setError] = useState('')
  const { company, login, loading } = useAuth()
  const navigate = useNavigate()

  const bases = useMemo(() => company?.bases ?? [], [company])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    try {
      await login({ username, password, baseId })
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha no login')
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-7xl items-center px-4 py-8">
      <section className="grid w-full gap-8 lg:grid-cols-[0.8fr_1.2fr]">
        <form onSubmit={handleSubmit} className="glass rounded-[2rem] p-8 shadow-glow">
          <p className="text-xs uppercase tracking-[0.35em] text-gold-400">Etapa 2</p>
          <h1 className="mt-3 text-2xl font-semibold text-white">Login do usuário</h1>
          <p className="mt-2 text-sm text-slate-400">Credenciais validadas na base configurada da empresa.</p>

          <label className="mt-8 block">
            <span className="mb-2 block text-sm text-slate-300">Usuário</span>
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none transition focus:border-gold-400/50"
            />
          </label>

          <label className="mt-4 block">
            <span className="mb-2 block text-sm text-slate-300">Senha</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none transition focus:border-gold-400/50"
            />
          </label>

          <label className="mt-4 block">
            <span className="mb-2 block text-sm text-slate-300">Base</span>
            <select
              value={baseId}
              onChange={(event) => setBaseId(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none transition focus:border-gold-400/50"
            >
              {bases.map((base) => (
                <option key={base.id} value={base.id}>
                  {base.name}
                </option>
              ))}
            </select>
          </label>

          {error ? <p className="mt-4 rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p> : null}

          <button
            type="submit"
            disabled={loading}
            className="mt-8 w-full rounded-2xl bg-gold-400 px-4 py-3 font-semibold text-ink-950 transition hover:bg-gold-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Entrando...' : 'Acessar dashboard'}
          </button>
        </form>

        <div className="glass rounded-[2rem] p-8 shadow-glow">
          <p className="text-sm uppercase tracking-[0.35em] text-gold-400">Contexto carregado</p>
          <h2 className="mt-3 text-3xl font-semibold text-white">{company?.name ?? 'Empresa Demo'}</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {bases.map((base) => (
              <div key={base.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm text-white">{base.name}</p>
                <p className="mt-1 text-xs text-slate-400">{base.host}:{base.port}</p>
                <p className="mt-1 text-xs text-slate-500">Status: {base.status}</p>
              </div>
            ))}
          </div>
          <div className="mt-8 rounded-3xl border border-dashed border-gold-400/30 bg-gold-400/5 p-5 text-sm text-slate-200">
            O frontend nunca recebe caminho da base .FDB nem credenciais Firebird. Só trabalha com o token e o JWT.
          </div>
        </div>
      </section>
    </main>
  )
}
