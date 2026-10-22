"""Research runner for the upside-capture study (see EXPERIMENTS.md).

    python run_research.py diagnose                 # where is the upside lost vs 80/15/5?
    python run_research.py grid <family>            # full grid + walk-forward for experiments/<family>.py
    python run_research.py lookahead <family|all>   # perturb-the-future check on every config
    python run_research.py frontier [family ...]    # CAGR vs MaxDD across families, Pareto set

Flags: --synthetic (offline smoke test; numbers are meaningless), --refresh.
Writes markdown + csv to research_results/ (tracked, so results are reviewable).
Real data needs FRED_API_KEY and network access to Yahoo + FRED.
"""
import argparse
import importlib
import pkgutil
from pathlib import Path

import numpy as np
import pandas as pd

import experiments
from regime_alloc.research import (LAG_YEARS, OBJECTIVES, OOS_START, ONE_AT_A_TIME, STAT_COLS, Lab,
                                   criteria, decompose, full_stats, lookahead_check,
                                   per_year, recovery_table, walk_forward)

PCT = {"CAGR", "Vol", "MaxDD", "AvgExp", "falling", "recovery", "normal", "total",
       "bench DD", "strat DD", "bench recov", "strat recov", "exp @trough", "avg exp 0-63d"}


def md(df: pd.DataFrame, pct_cols=PCT, pct_all: bool = False) -> str:
    def fmt(c, v):
        if isinstance(v, (bool, np.bool_)):
            return "✓" if v else "✗"
        if isinstance(v, (float, np.floating)):
            if np.isnan(v):
                return ""
            if pct_all or c in pct_cols:
                return f"{v:+.1%}" if c not in {"Vol", "AvgExp", "exp @trough", "avg exp 0-63d"} else f"{v:.1%}"
            return f"{v:.0f}" if c == "Rebal/yr" else f"{v:.2f}"
        return str(v)
    cols = [str(df.index.name or "")] + [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for i, row in df.iterrows():
        lines.append("| " + " | ".join([str(i)] + [fmt(c, v) for c, v in row.items()]) + " |")
    return "\n".join(lines)


def family(name: str):
    return importlib.import_module(f"experiments.{name}")


def all_families():
    return [m.name for m in pkgutil.iter_modules(experiments.__path__) if not m.name.startswith("_")]


def window(r: pd.Series, start=None):
    """`start`: a year (int) or a Timestamp; None = everything."""
    if start is None:
        return r
    return r[r.index >= (pd.Timestamp(f"{start}-01-01") if isinstance(start, int) else start)]


def stats_table(lab, runs, start=None, wf: dict | None = None):
    rows = {}
    for n, res in runs.items():
        r = window(res["returns"], start)
        rows[n] = full_stats(r, res["bench"], lab.rf, res)
    any_res = next(iter(runs.values()))
    b = window(any_res["bench"], start)
    rows["static 80/15/5"] = full_stats(b, any_res["bench"], lab.rf)
    for n, r in (wf or {}).items():
        rows[f"WF[{n}]"] = full_stats(r, any_res["bench"], lab.rf)
    return pd.DataFrame(rows).T.reindex(columns=STAT_COLS)


def lag_table(runs, wf: dict | None = None):
    any_res = next(iter(runs.values()))
    cols = {n: per_year(res["returns"]) for n, res in runs.items()}
    cols["static 80/15/5"] = per_year(any_res["bench"])
    for n, r in (wf or {}).items():
        cols[f"WF[{n}]"] = per_year(r)
    t = pd.DataFrame(cols).T
    return t[[y for y in LAG_YEARS if y in t.columns]]


# ---------------------------------------------------------------- commands
def cmd_diagnose(lab, out: Path):
    L = ["# Diagnosis: where the upside is lost vs static 80/15/5", ""]
    for start in [None, OOS_START]:
        wf, st = decompose(lab, start=f"{start}-01-01" if start else None)
        tag = f"{start}+ (walk-forward window)" if start else "full period"
        L += [f"## Waterfall, {tag}", "",
              "Annualized log-return gap added by each step, split by benchmark phase "
              "(falling = peak→trough of a >10% benchmark drawdown, recovery = trough→new high). "
              "The recovery column is (c) slow re-risking.", "",
              md(wf), "", f"### Layer stats, {tag}", "", md(st), ""]
        wf.to_csv(out / f"diagnose_waterfall_{start or 'full'}.csv")
    runs = {n: lab.run(cfg) for n, cfg in ONE_AT_A_TIME.items()}
    L += ["## One-at-a-time removals from the full system (full period)", "",
          md(stats_table(lab, runs)), "",
          "## Per-year returns in the lag years", "", md(lag_table(runs), pct_all=True), "",
          "## Benchmark drawdown episodes (>10%): how fast does the system re-risk?", "",
          md(recovery_table(lab, runs["full system"]).set_index("trough")), ""]
    (out / "diagnose.md").write_text("\n".join(L))
    print("\n".join(L))


def cmd_grid(lab, fam: str, out: Path):
    mod = family(fam)
    runs = {n: lab.run(cfg) for n, cfg in mod.GRID.items()}
    wf, picks = {}, []
    for obj in OBJECTIVES:
        wf[obj], p = walk_forward(runs, lab.rf, obj)
        picks.append(p)
    full = stats_table(lab, runs)
    wf_start = wf["sharpe"].index[0]          # >= OOS_START; later if training is too short
    oos = stats_table(lab, runs, wf_start, wf)
    base = oos.loc["baseline"]
    crit = pd.DataFrame({n: criteria(s, base) for n, s in oos.iterrows()
                         if n != "static 80/15/5"}).T
    L = [f"# Grid: {fam}", "", mod.__doc__.strip(), "",
         f"## Walk-forward window {wf_start.date()}+ (grid cells are fixed configs; WF[...] rows re-select "
         "the cell each Jan 1 on the expanding window by that objective)", "", md(oos), "",
         "### Success criteria (walk-forward window, vs baseline)", "", md(crit), "",
         "### Walk-forward picks per year", "", md(pd.concat(picks, axis=1)), "",
         "## Full period (in-sample)", "", md(full), "",
         "## Lag years", "", md(lag_table(runs, wf), pct_all=True), ""]
    (out / f"grid_{fam}.md").write_text("\n".join(L))
    oos.to_csv(out / f"grid_{fam}_oos.csv"); full.to_csv(out / f"grid_{fam}_full.csv")
    print("\n".join(L))


def cmd_lookahead(lab, fams):
    bad = []
    for fam in fams:
        for n, cfg in family(fam).GRID.items():
            d = lookahead_check(lab, cfg)
            print(f"{fam:14} {n:40} max|Δtarget| before cut = {d:.2e}  {'PASS' if d == 0 else 'FAIL'}")
            if d:
                bad.append((fam, n))
    print("ALL PASS" if not bad else f"FAILURES: {bad}")
    return not bad


def pareto(df: pd.DataFrame) -> pd.Series:
    """Efficient on (higher CAGR, shallower MaxDD)."""
    eff = []
    for i, r in df.iterrows():
        dom = ((df["CAGR"] >= r["CAGR"]) & (df["MaxDD"] >= r["MaxDD"]) &
               ((df["CAGR"] > r["CAGR"]) | (df["MaxDD"] > r["MaxDD"]))).any()
        eff.append(not dom)
    return pd.Series(eff, index=df.index)


def cmd_frontier(lab, fams, out: Path):
    runs = {}
    for fam in fams:
        for n, cfg in family(fam).GRID.items():
            key = "baseline" if n == "baseline" else f"{fam}:{n}"
            runs.setdefault(key, lab.run(cfg))
    wf, picks = {}, []
    for obj in OBJECTIVES:
        wf[obj], p = walk_forward(runs, lab.rf, obj)
        picks.append(p)
    wf_start = wf["sharpe"].index[0]
    oos = stats_table(lab, runs, wf_start, wf)
    full = stats_table(lab, runs)
    fixed = ~oos.index.str.startswith("WF[")
    oos["efficient"] = False
    oos.loc[fixed, "efficient"] = pareto(oos[fixed])
    keep = oos["efficient"] | oos.index.isin(["baseline", "static 80/15/5"]) | ~fixed
    t = oos[keep].sort_values("MaxDD", ascending=False)
    t["CAGR full"] = full["CAGR"].reindex(t.index)
    t["MaxDD full"] = full["MaxDD"].reindex(t.index)
    crit = pd.DataFrame({n: criteria(s, oos.loc["baseline"]) for n, s in t.iterrows()}).T
    L = [f"# Frontier ({', '.join(fams)}): walk-forward window {wf_start.date()}+", "",
         "Pareto-efficient fixed configs on (CAGR, MaxDD), plus baseline, benchmark, and WF[...] rows "
         "that re-select among *all* configs each Jan 1 on the expanding window (the honest number: "
         "fixed cells are picked with hindsight).", "",
         md(t.drop(columns="efficient"), pct_cols=PCT | {"CAGR full", "MaxDD full"}), "",
         "## Criteria", "", md(crit), "",
         "## Walk-forward picks per year", "", md(pd.concat(picks, axis=1)), "",
         "## Lag years", "", md(lag_table({k: runs[k] for k in t.index if k in runs}, wf), pct_all=True), "",
         "## All configs (walk-forward window)", "", md(oos), ""]
    (out / "frontier.md").write_text("\n".join(L))
    oos.to_csv(out / "frontier_oos.csv")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["diagnose", "grid", "lookahead", "frontier"])
    ap.add_argument("families", nargs="*")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--out", default="research_results")
    a = ap.parse_args()
    out = Path(a.out) / ("synthetic" if a.synthetic else "")
    out.mkdir(parents=True, exist_ok=True)
    lab = Lab.load(synthetic=a.synthetic, refresh=a.refresh)
    fams = all_families() if not a.families or a.families == ["all"] else a.families
    if a.cmd == "diagnose":
        cmd_diagnose(lab, out)
    elif a.cmd == "grid":
        for f in fams:
            cmd_grid(lab, f, out)
    elif a.cmd == "lookahead":
        raise SystemExit(0 if cmd_lookahead(lab, fams) else 1)
    else:
        cmd_frontier(lab, fams, out)
