# PROJ011 — Nível 1: ETL de Estoque (Bronze/Silver/Gold)

Pipeline simples de estoque: dois Excel brutos → limpeza em Python (pandas) → Supabase (Postgres) em 3 camadas (Bronze/Silver/Gold) → agendamento via GitHub Actions → dashboard em Streamlit consumindo só a camada Gold.

Dashboard no ar: https://proj011n-vel-1elt-simples-fzlriquhvbemgnfmufvkfl.streamlit.app/

Contexto completo do aprendizado (o que foi feito, bugs encontrados, decisões) está em `PROGRESSO.md`. Runbook de reconstrução do projeto do zero e documentação de estudo detalhada do workflow e do dashboard estão em `notas/`.

## Arquitetura

```
data/*.xlsx  →  etl_estoque.py  →  Supabase (dw_bronze / dw_silver / dw_gold)  →  app.py (Streamlit)
                      ▲
                      └── disparado por .github/workflows/etl.yml (manual ou cron diário)
```

- **Bronze** (`dw_bronze.movimentacao`): cópia fiel do Excel bruto, só para inspeção.
- **Silver** (`dw_silver.movimentacao`): dados limpos (datas normalizadas, código de loja padronizado, categoria via join com produtos, valores nulos/negativos tratados).
- **Gold** (`dw_gold.posicao_estoque`): agregado por loja + categoria (entradas, saídas, saldo, valor em estoque) — é a única camada que o dashboard lê.

## Rodar local

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Criar um `.env` na raiz (nunca commitar — já está no `.gitignore`) com:

```
SUPABASE_URL=postgresql://postgres.<projeto>:<senha>@aws-<n>-<regiao>.pooler.supabase.com:5432/postgres
```

Use a connection string do modo **Session pooler** (Supabase → Project Settings → Database → Connection string), não a "Direct connection" — a direta resolve pra IPv6 e falha em ambientes de nuvem sem saída IPv6 (GitHub Actions, Streamlit Cloud). Ver `.env.example`.

Rodar o ETL:
```powershell
python etl_estoque.py
```

Rodar o dashboard:
```powershell
streamlit run app.py
```

## Como o agendamento funciona

`.github/workflows/etl.yml` roda o `etl_estoque.py` no GitHub Actions:
- **Manual:** aba **Actions** do repo → workflow "ETL Estoque" → **Run workflow**.
- **Automático:** todo dia às 09:00 UTC (06:00 -03), via `cron`.

Detalhamento linha a linha em `notas/github-actions-workflow.md`. Nota: repositório sem push por ~60 dias tem o agendamento automático pausado pelo GitHub (o disparo manual continua funcionando).

## Onde ficam os segredos

`SUPABASE_URL` (connection string via session pooler) precisa estar cadastrada em **3 lugares independentes**, cada um no seu próprio mecanismo de secret — nunca em texto puro no código:

| Ambiente | Onde cadastrar |
|---|---|
| Local | `.env` (raiz do projeto, gitignored) |
| GitHub Actions | Settings → Secrets and variables → Actions → `SUPABASE_URL` |
| Streamlit Community Cloud | App → Settings → Secrets (formato TOML: `SUPABASE_URL = "..."`) |

## Limitações conhecidas (entrada para o Nível 2)

- **Fonte ainda é Excel manual** — sem contrato de schema, sem validação de tipo/formato na origem; qualquer mudança na estrutura do arquivo quebra o `extract()`.
- **Sem testes automatizados de dados** (ex.: dbt tests, Great Expectations) — os bugs de qualidade (datas mistas, loja não padronizada, duplicatas) foram pegos manualmente lendo os dados, não por um teste que falha no CI.
- **`load()` faz `replace`/`truncate` + reload completo** a cada execução — não há carga incremental nem versionamento histórico do dado (se um Excel tiver um erro, sobrescreve o estado anterior sem trilha de auditoria).
- **Orquestração é um único step linear** — GitHub Actions não modela dependência entre tarefas, retries granulares, nem paralelismo; qualquer pipeline com mais de um script real precisaria de um orquestrador (Airflow/Dagster).
- **Sem alertas de falha** — se o Actions falhar, ninguém é notificado automaticamente (só descobre olhando a aba Actions).
- **Cache do Streamlit é ingênuo** (`ttl=600` fixo) — não invalida sob demanda quando o dado muda, só expira por tempo.
