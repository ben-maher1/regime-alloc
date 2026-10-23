"""Taxable-account viability: the strategy vs static 60/30/10, after US taxes.

    python run_tax.py

Uses regime_alloc/tax.py (lot-level HIFO, ST/LT, GLDM as collectibles, wash
sales, netting, carryforward, VT dividends 2%/yr, cash interest, tax paid each
April from the account). Writes research_results/tax.md.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from regime_alloc import config as C
from regime_alloc.research import BENCH2, PRODUCTION, Lab
from regime_alloc.tax import TaxRates, simulate

STARTS = ["2005-01-03", "2010-01-04", "2015-01-02", "2020-01-02"]
SCENARIOS = {"24% / 15%": TaxRates(0.24, 0.15),
             "32% / 15% + NIIT": TaxRates(0.32, 0.15, 0.038),
             "37% / 20% + NIIT": TaxRates(0.37, 0.20, 0.038)}

lab = Lab.load()
R = lab.prices[list(C.ASSETS)].pct_change()
last = R.index[(R.fillna(0) != 0).any(axis=1)][-1]          # last day with real closes
idx = lab.prices.index
cols = list(C.ASSETS) + [C.CASH]
live = lab.prices[list(BENCH2)].notna()
tgt = pd.DataFrame(np.tile(list(BENCH2.values()), (len(idx), 1)), index=idx, columns=list(BENCH2)).where(live, 0.0)
tgt = tgt.div(tgt.sum(axis=1), axis=0)                      # pre-2014: no BTC -> 2/3 VT, 1/3 GLDM
tgt[C.CASH] = 0.0


def static(start, rebal):
    s = idx[(idx >= pd.Timestamp(start)) & (idx <= last)]
    days = {"yearly": s[np.r_[True, s.year[1:] != s.year[:-1]]], "daily": s}[rebal]
    tr = pd.DataFrame(0.0, index=idx, columns=cols)
    tr.loc[days] = 1.0
    return {"weights": tgt[cols], "trades": tr}


cagr = lambda w: w.iloc[-1] ** (252 / len(w)) - 1
mdd = lambda w: float((w / w.cummax() - 1).min())
prod = lab.run(PRODUCTION)
rows = []
for st in STARTS:
    for name, res in [("strategy", prod), ("60/30/10 yearly", static(st, "yearly")),
                      ("60/30/10 daily", static(st, "daily"))]:
        pre = simulate(lab.prices, res, TaxRates(0, 0), start=st, end=last, liquidate=False)["wealth"]
        row = {"start": st[:4], "portfolio": name, "pre-tax CAGR": cagr(pre), "pre-tax MaxDD": mdd(pre)}
        for sn, rt in SCENARIOS.items():
            s = simulate(lab.prices, res, rt, start=st, end=last)
            row[f"{sn} held"] = cagr(s["wealth"])
            row[f"{sn} liquidated"] = s["liquidated"] ** (252 / len(s["wealth"])) - 1
        rows.append(row)
        print(row["start"], name, f"{row['pre-tax CAGR']:.1%}", f"{row['32% / 15% + NIIT liquidated']:.1%}")
df = pd.DataFrame(rows).set_index(["start", "portfolio"])
book = simulate(lab.prices, prod, SCENARIOS["32% / 15% + NIIT"], start="2015-01-02", end=last, liquidate=False)["book"]

fmt = lambda d: d.map(lambda v: f"{v:+.1%}" if isinstance(v, float) else v)
out = Path("research_results"); out.mkdir(exist_ok=True)
(out / "tax.md").write_text("\n".join([
    f"# Taxable account: strategy vs static 60/30/10 (through {last.date()})", "",
    "CAGR before tax and after US federal tax (no state tax). `held` = account value with gains still "
    "unrealized; `liquidated` = everything sold at the end and the tax paid. Static mixes renormalize to "
    "2/3 VT, 1/3 GLDM before BTC data exists (2014).", "",
    fmt(df).to_markdown(), "",
    "## Strategy's realized income by type, 2015+ (multiples of the starting balance, 32%/15%+NIIT run)", "",
    book.round(3).to_markdown(), ""]))
df.to_csv(out / "tax.csv")
print(f"wrote {out / 'tax.md'}")
