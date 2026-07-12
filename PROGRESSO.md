# Progresso — Nível 1 (2026-07-12) — ✅ CONCLUÍDO

Nível 1 fechado: pipeline Excel → GitHub Actions → Supabase → Streamlit funcionando de ponta a ponta, na nuvem, sem passos manuais no meio. Detalhes completos de cada etapa estão neste arquivo, no runbook `notas/01_passo-a-passo_nivel-1-do-zero.html` (reconstrução do zero, com comandos e armadilhas) e em `README.md`.

## Concluído

- **Etapa 1 — ETL local:** venv criado, deps instaladas, `requirements.txt` congelado, bug do caminho de dados corrigido. Dois bugs de dados encontrados e corrigidos em `transform()`: datas ISO trocando dia/mês (`format="mixed", dayfirst=True`) e código de loja não totalmente padronizado (`L02` vs `L002`).
- **Etapa 2 — Supabase:** projeto criado, `.env` local com `SUPABASE_URL`, conexão testada via one-liner Python.
- **Etapa 3 — Schemas + carga:** `dw_bronze`, `dw_silver`, `dw_gold` criados; tabela `dw_gold.posicao_estoque` criada manualmente; `load()` reativado; `python etl_estoque.py` populando as 3 tabelas no Supabase.
- **Etapa 4 — GitHub:** repo criado em https://github.com/felipealves360/PROJ011_Nivel-1_ELT-simples, `.gitignore` e `.env.example` criados, commit/push feitos, confirmado que `.env` não subiu.
- **Etapa 5 — GitHub Actions:** workflow `.github/workflows/etl.yml` commitado e pushado, secret `SUPABASE_URL` cadastrado. Dois erros encontrados e corrigidos:
  - Secret malformado na 1ª tentativa (`Could not parse SQLAlchemy URL`) — recadastrado só com a URI pura.
  - `Network is unreachable` (IPv6) na 2ª tentativa — runners do GitHub Actions não têm saída IPv6 e a conexão direta do Supabase resolve pra IPv6. Resolvido trocando para **Session pooler** (IPv4) no Supabase, atualizando a string tanto no `.env` local quanto no secret do GitHub.
  - 3ª tentativa: execução manual (`workflow_dispatch`) ficou **verde**.
  - Nota adicional: repo sem push por ~60 dias tem o `schedule` pausado automaticamente pelo GitHub (`workflow_dispatch` continua ativo).
- **Etapa 6 — Streamlit sobre o Gold:** `app.py` criado (KPIs, gráficos por loja/categoria, tabela de detalhe, só lê `dw_gold.posicao_estoque`), testado local com `streamlit run app.py`, `requirements.txt` regenerado (e corrigido de UTF-16 pra UTF-8). Deploy feito no Streamlit Community Cloud com o secret `SUPABASE_URL` (session pooler) — app no ar em https://proj011n-vel-1elt-simples-fzlriquhvbemgnfmufvkfl.streamlit.app/.
  - Também criadas notas de estudo detalhadas em `notas/` (`github-actions-workflow.md` e `app-streamlit-dashboard.md`), com comentários inline correspondentes em `etl.yml` e `app.py`.
- **Etapa 7 — Fechar o ciclo:** linha nova adicionada manualmente no Excel de origem (loja `L03`, SKU novo `ARM-777`), commit/push, Actions disparado manualmente, Supabase recebeu a linha (`L003 / ARMACAO PREMIUM`). Primeira checagem no Streamlit não refletiu a mudança por causa do `@st.cache_data(ttl=600)` — resolvido esperando o TTL expirar (ou "Clear cache"). Ciclo completo confirmado. `README.md` criado na raiz; `.env.example` corrigido para o formato via session pooler.

## Nível 1 fechado — próximo passo é o Nível 2

Lista de limitações levantadas na Etapa 7 (ver `README.md` para a versão completa) que viram entrada do Nível 2:
- Fonte ainda é Excel manual, sem validação de schema.
- Sem testes automatizados de dados.
- `load()` é replace/truncate total, sem carga incremental nem trilha de auditoria.
- Orquestração é um único step linear (sem dependência entre tarefas, sem retries granulares) — candidato a Airflow/Dagster.
- Sem alertas de falha.

## Notas úteis

- Terminal do Antigravity é **PowerShell**. Ativar venv: `.venv\Scripts\Activate.ps1`.
- `git config --global user.name/user.email` já configurados nesta máquina.
- Excel de origem em `data/` são sujos de propósito — nunca editar sem necessidade; a limpeza é toda em `transform()` (exceção: adicionar linha de teste foi intencional na Etapa 7, para provar o ciclo ponta a ponta).
- **Supabase + qualquer ambiente na nuvem (GitHub Actions, Streamlit Cloud, etc.):** sempre usar a connection string do modo **Session pooler** (não "Direct connection") — evita o erro de rede IPv6 que já apareceu duas vezes neste projeto.
- Documentação de estudo (não é progresso de projeto, é material de referência) fica em `notas/`.
- Cache do Streamlit (`@st.cache_data(ttl=600)`) pode mascarar uma atualização recém-chegada no Supabase por até 10 min — útil lembrar ao debugar "por que não mudou".

## Instrução permanente para o professor (Claude)

O panorama HTML de acompanhamento por etapa (`01_panorama_nivel-1-pipeline-etapas.html`) foi removido do repo na faxina de 2026-07-12 — o material de referência do Nível 1 agora é o runbook `notas/01_passo-a-passo_nivel-1-do-zero.html` (estático, não é atualizado etapa a etapa) e este próprio arquivo. Ao final de cada etapa concluída, registrar o que aconteceu na prática diretamente na seção "Concluído" deste `PROGRESSO.md` (desvios do roteiro, bugs encontrados, comandos reais usados, sem segredos). Quando o usuário iniciar o Nível 2, criar um novo arquivo de progresso equivalente para essa fase.
