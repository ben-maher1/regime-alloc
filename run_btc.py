"""Bitcoin treatment: production vs fixed BTC sleeves vs static 60/30/10 (EXPERIMENTS.md 2026-10-23).

    python run_btc.py      # writes research_results/btc.md
"""
from pathlib import Path
import numpy as np, pandas as pd
from regime_alloc.research import Lab, PRODUCTION
from regime_alloc.backtest import run, build_targets
from regime_alloc.signals import vol_adjusted_momentum, reentry_score
from regime_alloc import config as C
lab=Lab.load()
R=lab.prices[list(C.ASSETS)].pct_change(); last=R.index[(R.fillna(0)!=0).any(axis=1)][-1]
P=lab.prices.loc[:last]; rets=P.pct_change()
cash_r=rets[C.CASH].fillna(0)
prod=run(P, lab.targets(PRODUCTION).loc[:last].dropna(), band=C.REBALANCE_BAND)['returns']
# strategy on VT/GLDM only (BTC removed from the universe)
P2=P.drop(columns='IBIT')
t2=build_targets(P2, lab.exposure({}).loc[:last], {k:v for k,v in PRODUCTION.items() if k!='band'}).dropna()
exb=run(P2, t2, band=C.REBALANCE_BAND)['returns']
# BTC timed alone: in when production-style score > 0 or 20d breakout on, else cash
sc=vol_adjusted_momentum(P[['IBIT']])
sc=reentry_score(P[['IBIT']], sc, C.SIGNAL_CAP, breakout_high=20, breakout_strength=1.0)
on=(sc['IBIT']>0).astype(float).where(sc['IBIT'].notna())
tb=pd.DataFrame({'IBIT':on, C.CASH:1-on}).dropna()
btc_timed=run(P[['IBIT',C.CASH]], tb, band=C.REBALANCE_BAND)['returns']
def yearly(sleeves, w):
    df=pd.DataFrame(sleeves).dropna()
    out=[]
    for y,g in df.groupby(df.index.year):
        v=(1+g).cumprod().mul(pd.Series(w))
        tot=v.sum(axis=1); out.append(tot/tot.shift(1).fillna(1.0)-1)
    return pd.concat(out)
def stats(r):
    r=r.dropna(); e=(1+r).cumprod(); rf=cash_r.reindex(r.index).fillna(0)
    return dict(CAGR=e.iloc[-1]**(252/len(r))-1, Vol=r.std()*252**.5, Sharpe=(r-rf).mean()/r.std()*252**.5, MaxDD=(e/e.cummax()-1).min())
V={'production':prod,
   'production, IBIT cap 0.3':run(P, lab.targets({**PRODUCTION,'max_weight':{'VT':1,'GLDM':.6,'IBIT':.3}}).loc[:last].dropna(), band=C.REBALANCE_BAND)['returns']}
for b in [0.05,0.10,0.15]:
    V[f'VT/GLDM timed + BTC fixed {b:.0%}']=yearly({'s':exb,'b':rets['IBIT']},{'s':1-b,'b':b})
V['VT/GLDM timed 90% + BTC timed 10%']=yearly({'s':exb,'b':btc_timed},{'s':0.9,'b':0.1})
V['VT/GLDM timed only (no BTC)']=exb
V['static 60/30/10 yearly']=yearly({'VT':rets['VT'],'GLDM':rets['GLDM'],'IBIT':rets['IBIT']},{'VT':.6,'GLDM':.3,'IBIT':.1})
V['static 67/33/0 yearly (no BTC)']=yearly({'VT':rets['VT'],'GLDM':rets['GLDM']},{'VT':2/3,'GLDM':1/3})
V['BTC buy & hold']=rets['IBIT']; V['BTC timed alone']=btc_timed
pd.set_option('display.width',250)
L=['# Bitcoin treatment (pre-tax, sleeves rebalanced yearly)','']
for a,b in [('2015-01-01',None),('2015-01-01','2019-12-31'),('2020-01-01',None)]:
    rows={n:stats(r.loc[a:b]) for n,r in V.items()}
    t=pd.DataFrame(rows).T; print(f'\n== {a[:4]} to {(b or str(last.date()))[:4]}'); print(t.round(3).to_string())
    L+=[f'## {a[:4]} to {(b or str(last.date()))[:4]}','',t.map(lambda v: f"{v:.2f}" if abs(v)>1.5 and False else f"{v:.3f}").to_markdown(),'']
# BTC timing value: how much of BTC's up/down did the timing keep
w=lab.run({**PRODUCTION}) ; hw=w['weights']['IBIT'].loc['2015':last]
print('\nproduction avg IBIT weight 2015+:', round(float(hw.mean()),3), '| share of days IBIT=0:', round(float((hw<0.005).mean()),2))

L+=[f'production average IBIT weight 2015+: {float(hw.mean()):.3f}; share of days at 0: {float((hw<0.005).mean()):.2f}','']
Path('research_results/btc.md').write_text('\n'.join(L)); print('wrote research_results/btc.md')
