import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATA = os.path.join(os.path.dirname(__file__), "data")


# ---------- E X T R A C T ----------
def extract():
    mov = pd.read_excel(f"{DATA}/2026-06-26_dados-brutos_movimentacao-estoque.xlsx")
    prod = pd.read_excel(f"{DATA}/2026-06-26_dados-brutos_dim-produtos.xlsx")
    return mov, prod


# ---------- T R A N S F O R M ----------
def transform(mov, prod):
    # BRONZE: copia fiel do bruto (so para inspecao)
    bronze = mov.copy()

    # SILVER: limpeza observavel
    s = mov.copy()
    for col in ["cod_loja", "tipo_movimentacao", "sku"]:
        s[col] = s[col].astype(str).str.strip().str.upper()  # 1) espacos + caixa
    s["cod_loja"] = s["cod_loja"].str.replace("LOJA ", "L", regex=False)
    num_loja = s["cod_loja"].str.extract(r"(\d+)")[0].astype(int)
    s["cod_loja"] = "L" + num_loja.astype(str).str.zfill(3)  # 2) padroniza loja

    iso = s["data"].str.contains("-", na=False)
    data_iso = pd.to_datetime(s.loc[iso, "data"], format="%Y-%m-%d")
    data_br = pd.to_datetime(s.loc[~iso, "data"], dayfirst=True)
    s["data"] = pd.concat([data_iso, data_br]).sort_index()  # 3) datas mistas
    neg = (s["tipo_movimentacao"] == "ENTRADA") & (s["quantidade"] < 0)
    s.loc[neg, "quantidade"] = s.loc[neg, "quantidade"].abs()  # 4) regra de negocio
    s = s.dropna(subset=["quantidade", "valor_unitario"])  # 5) nulos criticos
    s = s.drop_duplicates(
        subset=["data", "cod_loja", "sku", "tipo_movimentacao", "quantidade"]
    )  # 6) duplicatas

    # dimensao de produtos: limpa e deduplica pela chave estavel (sku)
    p = prod.copy()
    p["sku"] = p["sku"].astype(str).str.strip().str.upper()
    p["categoria"] = (
        p["categoria"].fillna("SEM CATEGORIA").astype(str).str.strip().str.upper()
    )
    p = p.drop_duplicates(subset=["sku"], keep="first")

    silver = s.merge(p[["sku", "categoria"]], on="sku", how="left")
    silver["categoria"] = silver["categoria"].fillna("SEM CATEGORIA")

    # GOLD: agrega o KPI por loja + categoria
    silver["ent"] = silver["quantidade"].where(
        silver["tipo_movimentacao"] == "ENTRADA", 0
    )
    silver["sai"] = silver["quantidade"].where(
        silver["tipo_movimentacao"] == "SAIDA", 0
    )
    gold = silver.groupby(["cod_loja", "categoria"], as_index=False).agg(
        qtd_entradas=("ent", "sum"),
        qtd_saidas=("sai", "sum"),
        preco_medio=("valor_unitario", "mean"),
    )
    gold["saldo"] = gold["qtd_entradas"] - gold["qtd_saidas"]
    gold["valor_saldo"] = (gold["saldo"] * gold["preco_medio"]).round(2)
    gold = gold[
        ["cod_loja", "categoria", "qtd_entradas", "qtd_saidas", "saldo", "valor_saldo"]
    ]

    silver = silver.drop(columns=["ent", "sai"])  # remove colunas auxiliares
    return bronze, silver, gold


# ---------- L O A D ----------
def load(bronze, silver, gold):
    engine = create_engine(os.environ["SUPABASE_URL"])
    with engine.begin() as conn:  # begin() = tudo numa transacao
        bronze.to_sql(
            "movimentacao", conn, schema="dw_bronze", if_exists="replace", index=False
        )
        silver.to_sql(
            "movimentacao", conn, schema="dw_silver", if_exists="replace", index=False
        )
        conn.execute(text("truncate table dw_gold.posicao_estoque"))
        gold.to_sql(
            "posicao_estoque", conn, schema="dw_gold", if_exists="append", index=False
        )


def run():
    mov, prod = extract()
    bronze, silver, gold = transform(mov, prod)
    load(bronze, silver, gold)
    print(f"OK - bronze={len(bronze)} silver={len(silver)} gold={len(gold)}")


if __name__ == "__main__":
    run()
