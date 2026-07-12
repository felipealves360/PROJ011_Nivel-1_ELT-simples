# Ver notas/app-streamlit-dashboard.md para explicacao detalhada linha a linha.
# Modelo de execucao do Streamlit: o script inteiro roda de novo, do topo ao fim,
# a cada interacao na pagina (clique, filtro, F5) - por isso o cache abaixo importa.

import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()  # le o .env local; no Streamlit Cloud quem injeta as env vars e o secret do painel

st.set_page_config(page_title="Posição de Estoque", layout="wide")  # 1a chamada st.*, obrigatorio


@st.cache_data(ttl=600)  # cacheia o resultado por 10min p/ nao bater no banco a cada interacao
def load_gold():
    engine = create_engine(os.environ["SUPABASE_URL"])
    # so le o schema Gold (regra do Medalhao: dashboard nunca toca Bronze/Silver)
    return pd.read_sql("select * from dw_gold.posicao_estoque", engine)


st.title("Posição de Estoque")
st.caption("Dados consumidos direto do schema dw_gold (Medalhão) no Supabase.")

df = load_gold()

col1, col2, col3 = st.columns(3)  # 3 colunas lado a lado, cada uma vira um KPI card
col1.metric("Saldo total (unid.)", f"{df['saldo'].sum():,.0f}")
col2.metric("Valor total em estoque", f"R$ {df['valor_saldo'].sum():,.2f}")
col3.metric("Lojas", df["cod_loja"].nunique())

st.subheader("Saldo por loja")
# as_index=True mantem cod_loja como indice -> vira o eixo X do grafico
saldo_loja = df.groupby("cod_loja", as_index=True)["saldo"].sum()
st.bar_chart(saldo_loja)

st.subheader("Valor em estoque por categoria")
valor_categoria = df.groupby("categoria", as_index=True)["valor_saldo"].sum()
st.bar_chart(valor_categoria)

st.subheader("Detalhe (loja x categoria)")
st.dataframe(df, width="stretch")  # tabela interativa (ordenavel), df cru sem agregacao
