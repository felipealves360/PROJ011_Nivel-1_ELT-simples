# Progresso — Nível 1 (2026-07-11)

Resumo da sessão de hoje, para retomar amanhã. Detalhes completos de cada etapa concluída estão em `01_panorama_nivel-1-pipeline-etapas.html` (seção "O que aconteceu na prática" de cada card).

## Concluído

- **Etapa 1 — ETL local:** venv criado, deps instaladas, `requirements.txt` congelado, bug do caminho de dados corrigido. Dois bugs de dados encontrados e corrigidos em `transform()`: datas ISO trocando dia/mês (`format="mixed", dayfirst=True`) e código de loja não totalmente padronizado (`L02` vs `L002`).
- **Etapa 2 — Supabase:** projeto criado, `.env` local com `SUPABASE_URL`, conexão testada via one-liner Python.
- **Etapa 3 — Schemas + carga:** `dw_bronze`, `dw_silver`, `dw_gold` criados; tabela `dw_gold.posicao_estoque` criada manualmente; `load()` reativado; `python etl_estoque.py` populando as 3 tabelas no Supabase.
- **Etapa 4 — GitHub:** repo criado em https://github.com/felipealves360/PROJ011_N-vel-1_ELT-simples, `.gitignore` e `.env.example` criados, commit/push feitos, confirmado que `.env` não subiu.

## Em andamento — Etapa 5 (GitHub Actions)

- Arquivo `.github/workflows/etl.yml` já criado localmente (não commitado ainda). Roda `checkout` → `setup-python` → `pip install -r requirements.txt` → `python etl_estoque.py`, com `SUPABASE_URL` vindo de `secrets.SUPABASE_URL`. Gatilhos: `workflow_dispatch` (manual) + `schedule` cron diário `"0 9 * * *"` (09:00 UTC = 06:00 -03).

### Próximos passos (retomar por aqui amanhã)

1. Cadastrar o secret `SUPABASE_URL` no GitHub: repo → Settings → Secrets and variables → Actions → New repository secret (mesmo valor do `.env` local).
2. Commit e push do workflow:
   ```
   git add .github/workflows/etl.yml
   git commit -m "Adiciona workflow de agendamento do ETL via GitHub Actions"
   git push
   ```
3. Disparar manualmente pela aba Actions e conferir os logs — critério de pronto da Etapa 5 é execução verde + dados atualizados no Supabase.
4. Depois seguir para Etapa 6 (Streamlit sobre o Gold) e Etapa 7 (fechar e revisar o ciclo).

## Notas úteis

- Terminal do Antigravity é **PowerShell**. Ativar venv: `.venv\Scripts\Activate.ps1`.
- `git config --global user.name/user.email` já configurados nesta máquina.
- Excel de origem em `data/` são sujos de propósito — nunca editar, a limpeza é toda em `transform()`.

## Instrução permanente para o professor (Claude)

Ao final de cada etapa concluída (critério de pronto atingido), atualizar `01_panorama_nivel-1-pipeline-etapas.html`:
- trocar a tag do card (`<span class="tag">`) para `✅ Concluído`;
- adicionar/editar o bloco `<div class="lbl">O que aconteceu na prática</div>` com uma lista do que realmente foi feito, incluindo desvios do roteiro original, bugs encontrados e comandos reais usados (sem segredos).
Manter esse padrão até a Etapa 7. Isso já vem sendo seguido nas Etapas 1–4; seguir replicando nas próximas.
