import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

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
      navigate('/login')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao validar token da empresa')
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-7xl items-center px-4 py-8">
      <section className="grid w-full gap-8 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="glass rounded-[2rem] p-8 shadow-glow">
          <p className="text-sm uppercase tracking-[0.35em] text-gold-400">Dashboard Web Multiempresa</p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight text-white sm:text-5xl">
            A camada web centraliza a leitura analítica sem tocar no Firebird diretamente.
          </h1>
          <p className="mt-6 max-w-2xl text-lg text-slate-300">
            Primeiro o agente valida o token da empresa. Depois o usuário entra com login e senha, e a API escolhe a base
            correta para retornar módulos e KPIs permitidos.
          </p>
          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            {['Token da empresa', 'Login em 2 etapas', 'Permissões por usuário'].map((item) => (
              <div key={item} className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200">
                {item}
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="glass rounded-[2rem] p-8 shadow-glow">
          <p className="text-xs uppercase tracking-[0.35em] text-gold-400">Etapa 1</p>
          <h2 className="mt-3 text-2xl font-semibold text-white">Token da empresa</h2>
          <p className="mt-2 text-sm text-slate-400">Use o código fornecido pelo Agent/API instalada localmente.</p>

          <label className="mt-8 block">
            <span className="mb-2 block text-sm text-slate-300">Token</span>
            <input
              value={token}
              onChange={(event) => setToken(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none ring-0 transition placeholder:text-slate-500 focus:border-gold-400/50"
              placeholder="EMP-001"
            />
          </label>

          {error ? <p className="mt-4 rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p> : null}

          <button
            type="submit"
            disabled={loading}
            className="mt-8 w-full rounded-2xl bg-gold-400 px-4 py-3 font-semibold text-ink-950 transition hover:bg-gold-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Validando...' : 'Continuar'}
          </button>

          <p className="mt-4 text-xs text-slate-500">
            Modo inicial com mocks ativo para não depender do Firebird enquanto a API local ainda está em preparação.
          </p>
        </form>
      </section>
    </main>
  )
}
