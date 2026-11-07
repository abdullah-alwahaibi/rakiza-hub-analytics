"""Rakiza hub analytics: recompute every statistic in the dashboard from the raw CSVs in data/.

Run:  pip install -r requirements.txt  then  python analysis.py
Each line prints the rebuilt value next to the figure the original model reports.
"""
import numpy as np
import pandas as pd
from scipy import stats

read = lambda name: pd.read_csv(f"data/{name}.csv")
hub, kpi = read("fact_hub_month"), read("kpi").iloc[0]
corr, scen = read("dim_corridor"), read("fact_scenario_year")
claims, elig = read("claims_audit"), read("eligible_scenarios")
rows = []

def check(name, rebuilt, model, tol=1e-6):
    rows.append((name, model, rebuilt, "PASS" if abs(rebuilt - model) < tol else "FAIL"))

# 1. Revenue and cost as straight lines in utilization (OLS on 240 hub-months)
u = hub.utilization
rev = stats.linregress(u, hub.revenue)
cost = stats.linregress(u, hub.cost)
gap = rev.slope - cost.slope                      # extra profit per unit of utilization

# 2. Break-even: where the two lines cross
breakeven = (cost.intercept - rev.intercept) / gap
check("Break-even utilization", breakeven, kpi.breakeven_util)

# 3. 12% return bar: profit per hub-month needed to earn 12% a year on $5M
need = 0.12 * kpi.build_mid_m * 1e6 / 12
bar = breakeven + need / gap
check("12% return utilization", bar, kpi.wacc_bar_util)

# 4. One-sample t-test of each corridor's hub-level mean utilization against break-even
hub_means = hub.groupby(["corridor", "hub_id"]).utilization.mean().reset_index()
for name, g in hub_means.groupby("corridor"):
    if len(g) > 2:
        p = stats.ttest_1samp(g.utilization, breakeven).pvalue
        check(f"p-value, {name}", p, corr.set_index("corridor").p_value_two_sided[name])

# 5. Wilson 95% interval for the share of trucks above the low threshold
n, z = int(kpi.n_trucks), 1.96
ph = kpi.share_above_low
centre = (ph + z**2 / (2 * n)) / (1 + z**2 / n)
half = z * np.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
check("Wilson lower bound", centre - half, kpi.share_low_ci_lower)
check("Wilson upper bound", centre + half, kpi.share_low_ci_upper)

# 6. Cumulative cash in the 12% return scenario: running total of profit minus build capex
s = scen[scen.scenario.str.startswith("Cost-of-capital")].sort_values("year_no")
cash = (s.hub_operating_profit_m - s.build_capex_m).cumsum()
check("Peak funding need ($M)", -cash.min(), -s.cumulative_net_cash_m.min())

# 7. Utilization the plan implies in Year 5 (reverse the revenue line)
hubs5 = s.avg_hubs.iloc[-1]
planned = (kpi.plan_y5_charging_rev_m * 1e6 / (hubs5 * 12) - rev.intercept) / rev.slope
check("Plan-implied utilization", planned, claims.set_index("claim_no").observed[3], 1e-5)

# 8. Plan revenue against the electrifiable pool (point estimate)
pool = kpi.pool_total_m * elig.eligible_share.iloc[0]
check("Plan revenue / eligible pool", kpi.plan_y5_charging_rev_m / pool, claims.set_index("claim_no").observed[4], 1e-4)

print(pd.DataFrame(rows, columns=["Check", "Model", "Rebuilt", "Result"]).to_string(index=False))
print(f"\nRevenue = {rev.intercept:,.0f} + {rev.slope:,.0f} u  (R2 {rev.rvalue**2:.3f})")
print(f"Cost    = {cost.intercept:,.0f} + {cost.slope:,.0f} u  (R2 {cost.rvalue**2:.3f})")
