# Dashboard Web Multiempresa - API local

API local em FastAPI para autenticação, permissões e entrega de dados mockados do dashboard multiempresa.

## Estrutura

- `app/auth`: login em duas etapas com token da empresa e login/senha
- `app/admin`: cadastro de bases e permissões por base
- `app/dashboard`: módulos independentes por aba
- `app/database`: camada preparada para Firebird 2.5
- `data`: arquivos JSON locais para configuração inicial

## Requisitos

- Python 3.11+
- Firebird driver opcional para a fase real

## Instalação

### Windows

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação do ambiente virtual:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Alternativa com CMD

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Se for conectar ao Firebird real depois, instale o driver opcional:

```powershell
pip install fdb
```

## Configuração

1. Copie `.env.example` para `.env`.
2. Ajuste:
   - `SECRET_KEY`
   - `CORS_ORIGINS`
   - `BASES_CONFIG_PATH`
   - `PERMISSIONS_CONFIG_PATH`
3. Edite os arquivos em `data/` para cadastrar bases e permissões locais.

## Execução local

### Opção 1

```powershell
python run.py
```

### Opção 2

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints principais

- `POST /auth/empresa`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`
- `GET /admin/bases`
- `POST /admin/bases`
- `PUT /admin/bases/{base_id}`
- `DELETE /admin/bases/{base_id}`
- `POST /admin/bases/{base_id}/test-connection`
- `GET /admin/permissions/{base_id}`
- `PUT /admin/permissions/{base_id}/{login}`
- `GET /dashboard/overview`
- `GET /dashboard/overview/resumo`
- `GET /dashboard/vendas`
- `GET /dashboard/vendas/resumo`
- `GET /dashboard/vendas/top-produtos`
- `GET /dashboard/vendas/por-vendedor`
- `GET /dashboard/financeiro`
- `GET /dashboard/financeiro/resumo`
- `GET /dashboard/financeiro/contas-receber`
- `GET /dashboard/financeiro/contas-pagar`
- `GET /dashboard/estoque`
- `GET /dashboard/estoque/resumo`
- `GET /dashboard/estoque/baixo-minimo`
- `GET /dashboard/funcionarios`
- `GET /dashboard/funcionarios/resumo`
- `GET /dashboard/configuracoes`
- `GET /dashboard/configuracoes/resumo`

## Fluxo de autenticação

1. O frontend envia o token da empresa para `POST /auth/empresa`.
2. A API local encontra a base configurada e retorna nome, CNPJ e `base_id`.
3. O frontend envia `empresa_token`, `username` e `password` para `POST /auth/login`.
4. A API valida as credenciais locais, gera JWT e devolve as permissões.
5. As rotas `/dashboard/*` exigem JWT e validam permissões por módulo.

> A API também aceita o formato `token`, `login` e `senha` para compatibilidade com integrações futuras.

### Credenciais de demo

- Empresa/token: `001`
- Login admin: `admin` / `admin123`
- Login vendas: `vendas` / `vendas123`
- Login gerente: `GERENTE` / `123456`

## Firebird

O módulo `app/database/firebird.py` já está preparado para conexão real.

- `get_connection(base_config)`
- `test_connection(base_config)`
- `execute_query(base_config, sql, params)`

Se o driver não estiver instalado, a API continua funcionando em modo mock.

## Netlify

O frontend continua separado e pode apontar para esta API local via `VITE_API_URL`.

Exemplo:

```env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCKS=false
```

No Netlify, mantenha o build apenas do frontend e aponte a variável de ambiente para a API local ou para a API publicada no servidor do cliente.

## Próximos passos

- Conectar `execute_query` aos SQLs reais do Firebird.
- Migrar o armazenamento JSON para SQLite, se necessário.
- Trocar os mocks por consultas por módulo sem alterar a arquitetura.
