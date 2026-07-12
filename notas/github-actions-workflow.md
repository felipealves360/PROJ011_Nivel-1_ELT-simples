# Como funciona `.github/workflows/etl.yml`

Nota de estudo — não é documentação de projeto, é pra entender a fundo o que cada linha faz. Referência: [GitHub Actions docs](https://docs.github.com/actions).

## A regra geral

Qualquer arquivo `.yml`/`.yaml` dentro de `.github/workflows/`, na branch padrão do repo (aqui, `main`), vira um **workflow** automaticamente. O GitHub varre essa pasta sozinho — não existe passo de "ativação" além do arquivo existir e estar commitado. Um repo pode ter vários workflows (vários arquivos), cada um independente.

## Arquivo linha a linha

```yaml
name: ETL Estoque
```
Nome exibido na aba **Actions** do GitHub, só um rótulo pra humano identificar entre vários workflows. Não afeta comportamento.

```yaml
on:
  workflow_dispatch: {}
  schedule:
    - cron: "0 9 * * *"  # 09:00 UTC = 06:00 -03
```
`on:` define **quando** o workflow roda. Aqui tem dois gatilhos independentes (não é "ou um ou outro" — os dois ficam sempre ativos ao mesmo tempo):

- **`workflow_dispatch: {}`** — habilita o botão **"Run workflow"** manual na aba Actions. O `{}` vazio significa "sem inputs customizados" (dá pra declarar campos de formulário aqui, tipo dropdown ou texto, se o workflow precisasse receber parâmetros do usuário).
- **`schedule:`** — lista de agendamentos cron. Cada `- cron: "..."` é uma expressão cron padrão de 5 campos:

  ```
  ┌───────────── minuto (0-59)
  │ ┌───────────── hora (0-23)
  │ │ ┌───────────── dia do mês (1-31)
  │ │ │ ┌───────────── mês (1-12)
  │ │ │ │ ┌───────────── dia da semana (0-6, dom-sáb)
  │ │ │ │ │
  0 9 * * *
  ```
  `0 9 * * *` = minuto 0, hora 9, qualquer dia/mês/dia-da-semana → todo dia às 09:00. **O cron do GitHub Actions roda em UTC sempre** (não dá pra mudar fuso na sintaxe), por isso o comentário traduzindo pra -03.

  ⚠️ **Detalhe importante:** o GitHub não garante o horário exato — em picos de uso, pode atrasar alguns minutos. E, mais relevante: **repositórios sem nenhum commit/push por ~60 dias têm os workflows agendados pausados automaticamente** (o `workflow_dispatch` continua funcionando normalmente). Basta um push ou reativação manual na aba Actions pra voltar.

```yaml
jobs:
  run-etl:
    runs-on: ubuntu-latest
```
`jobs:` — um workflow pode ter vários jobs (rodando em paralelo ou em sequência, se configurado). Aqui só tem um, chamado `run-etl` (nome arbitrário, escolhido por nós).

`runs-on: ubuntu-latest` — a **máquina virtual efêmera** que o GitHub sobe do zero pra rodar esse job. "Efêmera" quer dizer: nasce vazia (sem nosso código, sem Python instalado) só pra essa execução, e é destruída no final. Por isso os primeiros steps sempre são "buscar o código" e "instalar as ferramentas" — nada persiste entre execuções.

```yaml
steps:
  - uses: actions/checkout@v4
```
Cada `step` roda em sequência, na mesma máquina. `uses:` importa uma **action reutilizável** — código publicado por alguém (aqui, pelo próprio time do GitHub) no formato `owner/repo@versão`. `actions/checkout@v4` clona o conteúdo do seu repo dentro da VM (sem isso, a VM está vazia e nem `etl_estoque.py` existiria nela).

```yaml
  - uses: actions/setup-python@v5
    with:
      python-version: "3.12"
```
Outra action reutilizável: instala o Python 3.12 na VM e configura o PATH. `with:` passa parâmetros pra action (aqui, a versão desejada).

```yaml
  - run: pip install -r requirements.txt
```
`run:` (em vez de `uses:`) executa um comando de shell diretamente, como se fosse digitado no terminal da VM. Instala as dependências do projeto a partir do `requirements.txt` — mesma lógica de rodar localmente.

```yaml
  - run: python etl_estoque.py
    env:
      SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
```
Roda o script. `env:` injeta variáveis de ambiente só pra esse step. `${{ secrets.SUPABASE_URL }}` é a sintaxe de interpolação do Actions (`${{ }}`) pra referenciar o valor do secret cadastrado em Settings → Secrets and variables → Actions — o valor nunca aparece em texto puro no arquivo nem nos logs (o GitHub mascara automaticamente qualquer secret que aparecer no output).

## Resumindo o fluxo de uma execução

1. Gatilho dispara (manual ou cron).
2. GitHub sobe uma VM Ubuntu nova e vazia.
3. `checkout` clona o repo dentro dela.
4. `setup-python` instala Python 3.12.
5. `pip install` instala as libs.
6. `python etl_estoque.py` roda o ETL de verdade, com o secret injetado só nesse processo.
7. VM é destruída. Nada fica salvo além do que o script gravou no Supabase (que é externo à VM).
