# Progresso — Nível 1 (2026-07-12)

Resumo da sessão de hoje, para retomar amanhã. Detalhes completos de cada etapa concluída estão em `01_panorama_nivel-1-pipeline-etapas.html` (seção "O que aconteceu na prática" de cada card).

## Concluído

- **Etapa 1 — ETL local:** venv criado, deps instaladas, `requirements.txt` congelado, bug do caminho de dados corrigido. Dois bugs de dados encontrados e corrigidos em `transform()`: datas ISO trocando dia/mês (`format="mixed", dayfirst=True`) e código de loja não totalmente padronizado (`L02` vs `L002`).
- **Etapa 2 — Supabase:** projeto criado, `.env` local com `SUPABASE_URL`, conexão testada via one-liner Python.
- **Etapa 3 — Schemas + carga:** `dw_bronze`, `dw_silver`, `dw_gold` criados; tabela `dw_gold.posicao_estoque` criada manualmente; `load()` reativado; `python etl_estoque.py` populando as 3 tabelas no Supabase.
- **Etapa 4 — GitHub:** repo criado em https://github.com/felipealves360/PROJ011_N-vel-1_ELT-simples, `.gitignore` e `.env.example` criados, commit/push feitos, confirmado que `.env` não subiu.
- **Etapa 5 — GitHub Actions:** workflow `.github/workflows/etl.yml` commitado e pushado, secret `SUPABASE_URL` cadastrado. Dois erros encontrados e corrigidos:
  - Secret malformado na 1ª tentativa (`Could not parse SQLAlchemy URL`) — recadastrado só com a URI pura.
  - `Network is unreachable` (IPv6) na 2ª tentativa — runners do GitHub Actions não têm saída IPv6 e a conexão direta do Supabase resolve pra IPv6. Resolvido trocando para **Session pooler** (IPv4) no Supabase, atualizando a string tanto no `.env` local quanto no secret do GitHub.
  - 3ª tentativa: execução manual (`workflow_dispatch`) ficou **verde**.

## Próximo — Etapa 6 (Streamlit sobre o Gold)

1. Criar `app.py` que conecta no Supabase (usar a mesma connection string via pooler) e faz `SELECT * FROM dw_gold.posicao_estoque`.
2. Exibir: tabela, saldo por loja, valor de saldo por categoria (`st.bar_chart` ou similar).
3. Rodar local com `streamlit run app.py` e validar visualmente.
4. Publicar no Streamlit Community Cloud (grátis), apontando pro repo e configurando o secret `SUPABASE_URL` lá também (mesma connection string com pooler).

Depois seguir para Etapa 7 (fechar e revisar o ciclo).

## Notas úteis

- Terminal do Antigravity é **PowerShell**. Ativar venv: `.venv\Scripts\Activate.ps1`.
- `git config --global user.name/user.email` já configurados nesta máquina.
- Excel de origem em `data/` são sujos de propósito — nunca editar, a limpeza é toda em `transform()`.
- **Supabase + GitHub Actions:** sempre usar a connection string do modo **Session pooler** (não "Direct connection") em qualquer ambiente sem garantia de saída IPv6 — vale para GitHub Actions e provavelmente para o Streamlit Cloud também.

## Instrução permanente para o professor (Claude)

Ao final de cada etapa concluída (critério de pronto atingido), atualizar `01_panorama_nivel-1-pipeline-etapas.html`:
- trocar a tag do card (`<span class="tag">`) para `✅ Concluído`;
- adicionar/editar o bloco `<div class="lbl">O que aconteceu na prática</div>` com uma lista do que realmente foi feito, incluindo desvios do roteiro original, bugs encontrados e comandos reais usados (sem segredos).
Manter esse padrão até a Etapa 7. Isso já vem sendo seguido nas Etapas 1–5; seguir replicando nas próximas.
