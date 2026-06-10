# Manual API Tests

## Pré-requisitos

1. Abrir um terminal no Windows.
2. Entrar na pasta `backend`.
3. Instalar dependências:

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Opcional, apenas para ambiente com Firebird real:

```powershell
pip install fdb
```

4. Iniciar a API:

```powershell
python run.py
```

## Alternativa de execução

```powershell
uvicorn app.main:app --reload
```

## Testes

### 1. Health

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
```

Resultado esperado:

```json
{
  "status": "ok",
  "app": "Dashboard Web Multiempresa API"
}
```

### 2. Validar empresa

```powershell
$body = @{ token = "001" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/auth/empresa" -ContentType "application/json" -Body $body
```

Resultado esperado:

- Retorna `empresa_token`
- Retorna `company.name`
- Retorna `company.cnpj`
- Retorna `company.base_id`

Não deve retornar:

- caminho `.FDB`
- usuário Firebird
- senha Firebird

### 3. Login mock

```powershell
$body = @{
  token = "001"
  login = "admin"
  senha = "admin123"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/auth/login" -ContentType "application/json" -Body $body
```

Resultado esperado:

- `access_token`
- `user`
- `company`
- `permissions`

### 4. Meu usuário

Use o `access_token` retornado no login:

```powershell
$token = "COLE_AQUI_O_ACCESS_TOKEN"
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/auth/me" -Headers @{ Authorization = "Bearer $token" }
```

### 5. Dashboard overview

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/dashboard/overview/resumo" -Headers @{ Authorization = "Bearer $token" }
```

### 6. Dashboard vendas

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/dashboard/vendas/resumo" -Headers @{ Authorization = "Bearer $token" }
```

### 7. Dashboard financeiro

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/dashboard/financeiro/resumo" -Headers @{ Authorization = "Bearer $token" }
```

### 8. Dashboard estoque

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/dashboard/estoque/resumo" -Headers @{ Authorization = "Bearer $token" }
```

### 9. Dashboard funcionários

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/dashboard/funcionarios/resumo" -Headers @{ Authorization = "Bearer $token" }
```

### 10. Dashboard configurações

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/dashboard/configuracoes/resumo" -Headers @{ Authorization = "Bearer $token" }
```

## Usuários mock

- `admin / admin123`
- `vendas / vendas123`
- `GERENTE / 123456`

## Observações

- O frontend não acessa Firebird diretamente.
- O frontend não recebe caminho `.FDB`.
- O frontend não recebe usuário/senha Firebird.
- As respostas do dashboard são mockadas nesta fase.
