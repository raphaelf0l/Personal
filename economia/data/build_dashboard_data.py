"""
Regenera o bloco DATA embutido em dashboard.html a partir de data/transactions.json.

Le as transacoes normalizadas (que ja trazem 'bucket' e 'category'), agrega por
mes/categoria, acrescenta o gasto fixo mensal de Financiamento/Moradia (nao vem
de fatura de cartao, entao nao esta em transactions.json) e monta tambem a lista
de transacoes por categoria, usada pelo drill-down interativo do painel.

Uso: py data/build_dashboard_data.py > data/dashboard_data.json
"""
import json
from pathlib import Path

BASE = Path(__file__).parent
TXN_PATH = BASE / "transactions.json"

BUDGET = 7400.0
FIXED_CATEGORY = "Moradia/Financiamento"
FIXED_AMOUNT = 1600.0
FIXED_DESCRIPTION = "Financiamento imobiliario (fixo mensal)"

with open(TXN_PATH, encoding="utf-8") as f:
    txns = json.load(f)

months = sorted(set(t["month"] for t in txns))

# Ordem de exibicao original do painel (mantida para as cores baterem com o
# dashboard.html existente); fixo entra por ultimo, ja que e o maior gasto e
# fica mais facil de comparar visualmente contra o resto.
CATEGORY_ORDER = [
    "Mercado/Supermercado", "Transporte", "Alimentacao/Restaurantes",
    "Assinaturas", "Compras Online", "Saude/Farmacia", "Outros",
]
categories_seen = set(t["category"] for t in txns if t["bucket"] == "vida_real")
categories = [c for c in CATEGORY_ORDER if c in categories_seen] + [FIXED_CATEGORY]

monthly = {}
tx_by_category = {c: [] for c in categories}

for m in months:
    monthly[m] = {
        "vida_real_total": 0.0,
        "viagem_total": 0.0,
        "categories": {c: 0.0 for c in categories},
        "n_vida_real": 0,
        "n_viagem": 0,
        "budget": BUDGET,
        "remaining": 0.0,
    }

for t in txns:
    m = t["month"]
    d = monthly[m]
    if t["bucket"] == "vida_real":
        d["vida_real_total"] += t["amount_brl"]
        d["categories"][t["category"]] += t["amount_brl"]
        d["n_vida_real"] += 1
        tx_by_category[t["category"]].append({
            "date": t["date"], "month": m, "description": t["description"],
            "amount": round(t["amount_brl"], 2), "source": t["source"],
        })
    else:
        d["viagem_total"] += t["amount_brl"]
        d["n_viagem"] += 1

# Gasto fixo mensal (nao vem de transactions.json - pago fora do cartao).
for m in months:
    d = monthly[m]
    d["vida_real_total"] += FIXED_AMOUNT
    d["categories"][FIXED_CATEGORY] += FIXED_AMOUNT
    d["n_vida_real"] += 1
    tx_by_category[FIXED_CATEGORY].append({
        "date": f"{m}-01", "month": m, "description": FIXED_DESCRIPTION,
        "amount": FIXED_AMOUNT, "source": "fixo",
    })

for m in months:
    d = monthly[m]
    d["vida_real_total"] = round(d["vida_real_total"], 2)
    d["viagem_total"] = round(d["viagem_total"], 2)
    for c in categories:
        d["categories"][c] = round(d["categories"][c], 2)
    d["remaining"] = round(BUDGET - d["vida_real_total"], 2)

for c in categories:
    tx_by_category[c].sort(key=lambda x: x["date"])

total_viagem = round(sum(monthly[m]["viagem_total"] for m in months), 2)
total_vida_real = round(sum(monthly[m]["vida_real_total"] for m in months), 2)
n_transactions = len(txns) + len(months)  # +1 lancamento fixo sintetico por mes

edge_case_count = 1
edge_case_total = 117.62

DATA = {
    "budget": BUDGET,
    "months": months,
    "monthly": monthly,
    "total_viagem": total_viagem,
    "total_vida_real": total_vida_real,
    "categories": categories,
    "n_transactions": n_transactions,
    "edge_case_count": edge_case_count,
    "edge_case_total": edge_case_total,
    "transactions_by_category": tx_by_category,
}

print(json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
