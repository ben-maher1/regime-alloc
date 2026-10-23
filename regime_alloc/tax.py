"""After-tax simulation of a strategy in a US taxable account (research only).

Replays a backtest's trade days in dollars with lot-level accounting:
  - lots per sleeve, sold highest-cost-first (specific lot ID, "HIFO")
  - short-term (held <= 365 days) vs long-term gains; GLDM is a grantor
    trust holding bullion, so its long-term gains are "collectibles" (28% cap)
  - wash sales: a loss on a sale is disallowed to the extent the same sleeve
    was bought within 30 days before or after; it moves into the basis of the
    replacement lot
  - IRS netting of the ST / 28% / 15-20% buckets, losses carried forward
    (the $3,000 ordinary-income offset is ignored: it depends on account size)
  - VT dividends (qualified, `div_yield` a year) and cash interest are taxed
    in the year they arrive; adjusted prices already reinvest the dividends,
    so they are added to VT's basis
  - each year's tax is paid on the first trading day after Apr 15 of the next
    year by selling every holding pro rata (those sales are taxed too)
On a backtest's trade days the account rebalances to that day's held weights;
otherwise it drifts, so a zero-rate run reproduces the backtest's returns.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config as C

COLLECTIBLES = {"GLDM"}


@dataclass(frozen=True)
class TaxRates:
    ordinary: float            # federal marginal rate on ordinary income / ST gains
    ltcg: float                # federal long-term rate (qualified dividends too)
    niit: float = 0.0          # 3.8% net investment income tax, if it applies
    state: float = 0.0         # flat state rate on all investment income

    def st(self):   return self.ordinary + self.niit + self.state
    def lt(self):   return self.ltcg + self.niit + self.state
    def coll(self): return min(0.28, self.ordinary) + self.niit + self.state


def _net(st: float, lt: float, coll: float) -> tuple[float, float, float]:
    """IRS netting: a net loss in one bucket offsets the others (ST losses hit
    28% gains first, then 15/20%; LT losses hit 28% gains first, then ST).
    Returns taxable (st, lt, coll), any of them negative = carryforward."""
    if lt < 0:
        use = min(-lt, max(coll, 0)); coll -= use; lt += use
    if coll < 0:
        use = min(-coll, max(lt, 0)); lt -= use; coll += use
    if st < 0:
        use = min(-st, max(coll, 0)); coll -= use; st += use
        use = min(-st, max(lt, 0)); lt -= use; st += use
    for b in ("lt", "coll"):
        v = {"lt": lt, "coll": coll}[b]
        if v < 0 and st > 0:
            use = min(-v, st); st -= use
            if b == "lt": lt += use
            else: coll += use
    return st, lt, coll


def simulate(prices: pd.DataFrame, res: dict, rates: TaxRates, start=None, end=None,
             div_yield: dict | None = None, liquidate: bool = True) -> dict:
    div_yield = {"VT": 0.02} if div_yield is None else div_yield
    held, trades = res["weights"], res["trades"]
    idx = held.dropna().index
    idx = idx[(idx >= pd.Timestamp(start)) if start else slice(None)]
    if end is not None:
        idx = idx[idx <= pd.Timestamp(end)]
    sleeves = [c for c in held.columns if c != C.CASH]
    px = prices[sleeves].reindex(idx).ffill().fillna(0.0)     # 0 only where a sleeve has no data (and no weight) yet
    cash_r = prices[C.CASH].pct_change().reindex(idx).fillna(0.0)
    cost = pd.Series(C.COST_BPS).reindex(sleeves).fillna(0).values / 1e4
    traded = trades.reindex(idx).fillna(0.0).abs().max(axis=1) > 1e-9

    lots = {a: [] for a in sleeves}            # [shares, basis, buy_date]
    cash = 0.0
    year_book = {}                             # year -> dict of st, lt, coll, div, int
    pending_loss = []                          # [date, sleeve, loss_left, shares_left, year]
    carry = {"st": 0.0, "lt": 0.0, "coll": 0.0}
    taxes_paid, disallowed_total, wealth = 0.0, 0.0, []
    book = lambda y: year_book.setdefault(y, {"st": 0.0, "lt": 0.0, "coll": 0.0, "div": 0.0, "int": 0.0})

    def value(i):
        return cash + sum(sum(l[0] for l in lots[a]) * px.iloc[i][a] for a in sleeves)

    def buy(a, dollars, i):
        nonlocal cash
        d = idx[i]; p = px.iloc[i][a]
        lot = [dollars / p, dollars, d]
        # wash sale: a loss sold in the last 30 days moves into this lot's basis
        for pl in pending_loss:
            if pl[1] == a and pl[2] > 0 and (d - pl[0]).days <= 30:
                frac = min(lot[0] / pl[3], 1.0) if pl[3] > 0 else 0
                dis = pl[2] * frac
                book(pl[4])["st" if pl[5] else ("coll" if a in COLLECTIBLES else "lt")] += dis
                lot[1] += dis; pl[2] -= dis; pl[3] -= pl[3] * frac
                nonlocal_disallow(dis)
        lots[a].append(lot)
        cash -= dollars

    def nonlocal_disallow(x):
        nonlocal disallowed_total
        disallowed_total += x

    def sell(a, dollars, i):
        nonlocal cash
        d = idx[i]; p = px.iloc[i][a]
        need = dollars / p
        lots[a].sort(key=lambda l: l[1] / l[0], reverse=True)      # HIFO
        while need > 1e-15 and lots[a]:
            l = lots[a][0]
            q = min(need, l[0]); basis = l[1] * q / l[0]
            gain = q * p - basis
            short = (d - l[2]).days <= 365
            bucket = "st" if short else ("coll" if a in COLLECTIBLES else "lt")
            if gain < 0:
                # wash sale against shares bought in the prior 30 days that are still held
                recent = sum(x[0] for x in lots[a][1:] if (d - x[2]).days <= 30)
                frac = min(recent / q, 1.0) if q > 0 else 0
                dis = -gain * frac
                if dis > 0:
                    rec = [x for x in lots[a][1:] if (d - x[2]).days <= 30]
                    tot = sum(x[0] for x in rec)
                    for x in rec:
                        x[1] += dis * x[0] / tot
                    nonlocal_disallow(dis)
                book(d.year)[bucket] += gain + dis
                if -gain - dis > 0:
                    pending_loss.append([d, a, -gain - dis, q * (1 - frac), d.year, short])
            else:
                book(d.year)[bucket] += gain
            l[0] -= q; l[1] -= basis; need -= q
            if l[0] <= 1e-15:
                lots[a].pop(0)
        cash += dollars

    def rebalance(i, w):
        nonlocal cash
        V = value(i)
        cur = {a: sum(l[0] for l in lots[a]) * px.iloc[i][a] for a in sleeves}
        diff = {a: w[a] * V - cur[a] for a in sleeves}
        for k, a in enumerate(sleeves):                 # sells first, then buys
            if diff[a] < -1e-12:
                sell(a, -diff[a], i); cash -= -diff[a] * cost[k]
        for k, a in enumerate(sleeves):
            if diff[a] > 1e-12:
                buy(a, diff[a], i); cash -= diff[a] * cost[k]

    def pay_tax(i, year):
        nonlocal taxes_paid, cash
        b = book(year)
        st, lt, coll = _net(b["st"] + carry["st"], b["lt"] + carry["lt"], b["coll"] + carry["coll"])
        carry.update(st=min(st, 0), lt=min(lt, 0), coll=min(coll, 0))
        tax = (max(st, 0) * rates.st() + max(lt, 0) * rates.lt() + max(coll, 0) * rates.coll()
               + b["div"] * rates.lt() + b["int"] * rates.st())
        if tax <= 0:
            return
        V = value(i)
        f = min(tax / V, 1.0)
        for a in sleeves:                               # pro rata, keeps weights
            q = sum(l[0] for l in lots[a]) * px.iloc[i][a]
            if q > 0:
                sell(a, q * f, i)
        cash -= tax
        taxes_paid += tax

    # day 0: fund the account at 1.0 and buy the held weights
    cash = 1.0
    rebalance(0, held.loc[idx[0]])
    paid_for = set()
    for i in range(1, len(idx)):
        d = idx[i]
        interest = cash * cash_r.iloc[i]
        cash += interest
        book(d.year)["int"] += interest
        for a, y in div_yield.items():
            if a in lots and lots[a]:
                dv = sum(l[0] for l in lots[a]) * px.iloc[i - 1][a] * y / 252
                book(d.year)["div"] += dv
                tot = sum(l[0] for l in lots[a])
                for l in lots[a]:
                    l[1] += dv * l[0] / tot
        pending_loss[:] = [pl for pl in pending_loss if (d - pl[0]).days <= 30 and pl[2] > 1e-15]
        if d.month > 4 or (d.month == 4 and d.day > 15):
            y = d.year - 1
            if y >= idx[0].year and y not in paid_for:
                pay_tax(i, y); paid_for.add(y)
        if traded.iloc[i]:
            rebalance(i, held.loc[d])
        wealth.append((d, value(i)))

    w = pd.Series(dict(wealth))
    out = {"wealth": w, "taxes_paid": taxes_paid, "disallowed": disallowed_total,
           "book": pd.DataFrame(year_book).T}
    # liquidation: sell everything at the end and settle all open years
    if liquidate:
        i = len(idx) - 1
        y_end = idx[-1].year
        for y in sorted(set(year_book) - paid_for):
            if y < y_end:
                pay_tax(i, y); paid_for.add(y)
        for a in sleeves:
            q = sum(l[0] for l in lots[a]) * px.iloc[i][a]
            if q > 0:
                sell(a, q, i)
        pay_tax(i, y_end)
        out["liquidated"] = cash
    return out


def summary(sim: dict, pre_tax: pd.Series | None = None) -> pd.Series:
    w = sim["wealth"]
    yrs = len(w) / 252
    s = {"after-tax CAGR (held)": w.iloc[-1] ** (1 / yrs) - 1}
    if "liquidated" in sim:
        s["after-tax CAGR (liquidated)"] = sim["liquidated"] ** (1 / yrs) - 1
    if pre_tax is not None:
        r = pre_tax.reindex(w.index).dropna()
        s["pre-tax CAGR"] = (1 + r).prod() ** (252 / len(r)) - 1
    eq = w / w.cummax() - 1
    s["after-tax MaxDD"] = eq.min()
    s["taxes paid / start"] = sim["taxes_paid"]
    s["wash-sale disallowed / start"] = sim["disallowed"]
    return pd.Series(s)
