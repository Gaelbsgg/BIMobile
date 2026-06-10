# Dashboard Web Multiempresa

Arquitetura inicial de um dashboard multiempresa com:

- Frontend em `React + Vite + TypeScript`
- Estilização com `TailwindCSS`
- Gráficos com `Recharts`
- Backend em `FastAPI`
- Autenticação com `JWT`
- Configuração local da API por `JSON`
- Preparado para integrar com `Firebird 2.5` depois

## Objetivo desta etapa

Esta primeira entrega foca em:

- Estrutura limpa do monorepo
- Telas funcionais com dados mockados
- Endpoints FastAPI simulados
- Separação entre autenticação, permissões, dashboard e registro de SQL
- Base pronta para trocar os mocks pelo Firebird real sem refatoração grande

## Estrutura

```text
/backend
  app/
    api/
    core/
    data/
    modules/
    services/
/frontend
  src/
    components/
    modules/
    pages/
    routes/
    services/
    styles/
```

## Regras de segurança já respeitadas

- O frontend nunca acessa Firebird diretamente
- O frontend nunca recebe caminho `.FDB`
- O frontend nunca recebe usuário/senha do Firebird
- A API seleciona a base correta pelo token da empresa
- A API valida login e senha no banco configurado
- As permissões via JWT controlam o que o usuário vê
- Os SQLs ficam registrados no backend

## Backend

### Estrutura de ambiente

Crie `backend/.env` baseado em `backend/.env.example`.

Exemplo:

```env
APP_NAME=Dashboard Multiempresa API
JWT_SECRET=change-this-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=240
COMPANY_TOKEN_EXPIRE_MINUTES=30
STORE_PATH=app/data/local_store.json
CORS_ORIGINS=http://localhost:5173,https://seu-site.netlify.app
```

### Instalação local

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints principais

- `POST /auth/empresa`
- `POST /auth/login`
- `GET /auth/me`
- `GET /admin/bases`
- `POST /admin/bases`
- `PUT /admin/bases/{id}`
- `DELETE /admin/bases/{id}`
- `POST /admin/bases/{id}/test-connection`
- `GET /admin/permissions`
- `PUT /admin/permissions/{user_id}`
- `GET /dashboard/overview`
- `GET /dashboard/vendas`
- `GET /dashboard/financeiro`
- `GET /dashboard/estoque`
- `GET /dashboard/funcionarios`

## Frontend

### Variáveis de ambiente

Crie `frontend/.env` baseado em `frontend/.env.example`.

```env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCKS=true
```

### Instalação local

```bash
cd frontend
npm install
npm run dev
```

## Deploy no Netlify

O frontend foi preparado para deploy estático no Netlify.

### Build

- Base: `frontend`
- Command: `npm run build`
- Publish: `dist`

### Variáveis no Netlify

Configure:

- `VITE_API_URL` apontando para a API local ou para o ambiente que o cliente usar
- `VITE_USE_MOCKS=false` em produção quando a API estiver disponível

## Modo mock

O frontend foi preparado para funcionar com mocks no início, sem depender do Firebird.

Fluxo sugerido:

1. Informe o token da empresa
2. Faça login com um usuário mockado
3. Navegue pelo dashboard
4. Quando a API real estiver pronta, apenas troque a configuração da URL

## Próximos passos

1. Trocar o store JSON por SQLite local se for melhor para o servidor do cliente
2. Implementar os adaptadores reais do Firebird 2.5
3. Registrar SQLs reais no `sql_registry`
4. Evoluir o controle fino de permissões por módulo e KPI

