# Como funciona `app.py` (dashboard Streamlit)

Nota de estudo — não é documentação de projeto, é pra entender a fundo o que cada linha faz. Referência: [Streamlit docs](https://docs.streamlit.io).

## O modelo de execução (a peça-chave pra entender tudo o resto)

Streamlit não é um framework de rotas/handlers como Flask ou FastAPI. **O script inteiro roda do topo até o final a cada interação** na página — um clique, mudar um filtro, um F5 no navegador. Não existe "callback só do botão X"; o Python inteiro reexecuta, de cima a baixo, toda vez.

Consequência direta: qualquer coisa "cara" (tipo bater num banco de dados) precisa de cache, senão roda de novo a cada interação — é exatamente o problema que o `@st.cache_data` resolve mais abaixo.

## Arquivo linha a linha

```python
import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
```
Mesmas libs e mesmo padrão do `etl_estoque.py`: `load_dotenv()` lê o `.env` local e injeta as variáveis no `os.environ`. **Só funciona localmente** — no Streamlit Community Cloud, quem faz esse papel é o secret cadastrado no painel deles (a chamada `load_dotenv()` simplesmente não encontra arquivo e não faz nada, sem erro).

```python
st.set_page_config(page_title="Posição de Estoque", layout="wide")
```
Configura a aba do navegador (`page_title`) e o layout da página. `layout="wide"` usa a largura inteira da tela em vez do padrão centralizado-estreito do Streamlit. **Regra da lib:** precisa ser a primeira chamada `st.*` do script, senão dá erro.

```python
@st.cache_data(ttl=600)
def load_gold():
    engine = create_engine(os.environ["SUPABASE_URL"])
    return pd.read_sql("select * from dw_gold.posicao_estoque", engine)
```
O decorator `@st.cache_data` é o mecanismo de cache do Streamlit pra **dados** (existe também `@st.cache_resource`, pra objetos tipo conexões — não usamos aqui, criamos a `engine` nova a cada chamada, o que é barato pro SQLAlchemy).

- `ttl=600` = tempo de vida do cache em segundos (10 min). Depois disso, a próxima chamada reconsulta o Supabase de verdade.
- A **chave do cache** é baseada nos argumentos da função (aqui, nenhum) + o código-fonte da função. Ou seja: sem esse decorator, `load_gold()` bateria no banco a cada interação do usuário na página (lembra do "roda tudo de novo a cada clique" lá de cima) — com ele, só bate de fato uma vez a cada 10 min, não importa quantas vezes o script inteiro reexecute nesse intervalo.

```python
st.title("Posição de Estoque")
st.caption("Dados consumidos direto do schema dw_gold (Medalhão) no Supabase.")
```
`st.title` desenha o `<h1>` da página. `st.caption` é um texto pequeno e discreto (estilo legenda), útil pra dar contexto sem competir visualmente com o título.

```python
df = load_gold()
```
Chama a função cacheada. Esse `df` é o dataframe cru do Gold: uma linha por combinação `cod_loja` + `categoria`, com `qtd_entradas`, `qtd_saidas`, `saldo`, `valor_saldo` (é a mesma tabela que o `etl_estoque.py` grava — o dashboard não faz nenhuma lógica de negócio nova, só lê e reapresenta).

```python
col1, col2, col3 = st.columns(3)
col1.metric("Saldo total (unid.)", f"{df['saldo'].sum():,.0f}")
col2.metric("Valor total em estoque", f"R$ {df['valor_saldo'].sum():,.2f}")
col3.metric("Lojas", df["cod_loja"].nunique())
```
`st.columns(3)` divide a largura da página em 3 colunas lado a lado; cada `colN` é um "container" onde você desenha elementos independentes (aqui, cada um recebe só um `st.metric`).

`st.metric(label, value)` desenha aquele card de número grande com rótulo pequeno em cima — o KPI. Repare que `.sum()` e `.nunique()` são agregações em cima do `df` inteiro (todas as lojas/categorias juntas) — são os totais gerais, diferente dos gráficos abaixo que quebram por dimensão.

```python
st.subheader("Saldo por loja")
saldo_loja = df.groupby("cod_loja", as_index=True)["saldo"].sum()
st.bar_chart(saldo_loja)
```
`st.subheader` = `<h2>`, título de seção.

O `groupby` é pandas puro — o Gold já vem por `cod_loja` + `categoria`, então aqui é só "somar as categorias dentro de cada loja" pra ter um número por loja. `as_index=True` mantém `cod_loja` como índice da Series resultante (em vez de virar coluna normal).

`st.bar_chart()` aceita uma Series/DataFrame pandas diretamente e desenha um gráfico de barras usando o **índice** como eixo X e o(s) **valor(es)** como eixo Y — por isso o `as_index=True` importa: é o que vira o rótulo de cada barra (`L001`, `L002`, ...).

```python
st.subheader("Valor em estoque por categoria")
valor_categoria = df.groupby("categoria", as_index=True)["valor_saldo"].sum()
st.bar_chart(valor_categoria)
```
Mesma lógica do bloco anterior, trocando a dimensão de agrupamento (`categoria` em vez de `cod_loja`) e a métrica (`valor_saldo` em vez de `saldo`).

```python
st.subheader("Detalhe (loja x categoria)")
st.dataframe(df, width="stretch")
```
`st.dataframe()` desenha uma tabela **interativa** (dá pra ordenar clicando no cabeçalho da coluna, redimensionar colunas, copiar) — diferente de `st.table()`, que é uma tabela estática. `width="stretch"` faz ela ocupar a largura total disponível (é a sintaxe nova; versões antigas do Streamlit usavam `use_container_width=True`, hoje deprecado).

Esse é o `df` cru, sem nenhum `groupby` — é o "vai fundo" pra quem quer ver linha a linha depois de olhar os KPIs e gráficos resumidos.

## A régua de ouro do Medalhão, aplicada aqui

Repare que `load_gold()` é a **única** função que toca o banco, e ela lê **só** `dw_gold.posicao_estoque` — nunca `dw_silver` nem `dw_bronze`. O dashboard não sabe (e não precisa saber) que essas outras camadas existem. Toda a lógica de limpeza, regras de negócio e agregação já foi resolvida rio acima, no `etl_estoque.py`; aqui é puramente apresentação.

## Resumindo o fluxo de uma visita à página

1. Usuário abre a URL → Streamlit roda o script inteiro, do topo ao fim.
2. `load_gold()` é chamada: se já tem cache válido (< 10 min), retorna na hora sem tocar o Supabase; senão, consulta de verdade.
3. Cada `st.*` desenha um elemento na página, na ordem em que aparece no código (é literalmente top-to-bottom).
4. Qualquer interação do usuário (mudar algo, ou até um F5) → volta pro passo 1.
