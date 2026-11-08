# Rakiza hub analytics: does the plan hold up?

An analysis and interactive dashboard that tests a charging-hub business plan against hub-level data.

**Live dashboard:** open `https://abdullah-alwahaibi.github.io/rakiza-hub-analytics/` in any browser (no install, works offline).

## Headline findings
- Break-even utilization is **60.1%**; a 12% return needs **73.8%**; the sample average is **60.9%**.
- The Year-5 plan implies **81.4%** utilization in every hub, above the 12% return level and close to the best corridor (85.9%).
- Building 45 hubs costs about **$225M** against **$120M** of capital; peak funding need in the 12% scenario is **$168.3M**.
- Plan Year-5 revenue is **2.8x** the point-estimate electrifiable demand pool.
- In a 10,000-draw bootstrap of the 20 sampled hubs, fleet-average utilization never reached the 12% return level.

## What is in the dashboard
| Tab | Content |
|---|---|
| Hub economics | Scenario selector, KPI cards, corridor utilization with significance, revenue vs plan, build cost vs capital, monthly utilization, recommendations |
| Claims audit | Eight management claims tested, each shown against its benchmark |
| Calculations | 11 worked calculations with formulas and working, plus the revenue/cost scatter |
| Simulator | What-if sliders for utilization, build cost and capital, plus the bootstrap risk analysis |
| Process | How it was built, data inventory, key inputs, 12 validation checks, review of the original report, every DAX measure |

## Repository
```
index.html        the dashboard
analysis.py       recomputes every statistic from the CSVs and prints a pass/fail table
requirements.txt  numpy, pandas, scipy
data/             the 10 model tables as CSV
```

## Reproduce
```
pip install -r requirements.txt
python analysis.py
```

## Method summary
1. **Regression:** revenue and cost per hub-month fitted as straight lines in utilization (240 hub-months).
2. **Break-even:** the utilization where the two lines cross; the 12% return level adds the profit needed to earn 12% a year on $5M per hub.
3. **Corridor tests:** one-sample t-test of each corridor's hub-level mean utilization against break-even (2 to 6 hubs per corridor, so small samples are labelled).
4. **Confidence interval:** Wilson interval for the share of trucks above the low threshold (1 of 20).
5. **Funding:** cumulative cash = running total of operating profit minus build capex; peak funding need is its lowest point.
6. **Risk:** bootstrap of the 20 hub means, assuming future hubs resemble the sample.

## Host it on GitHub Pages
Upload the files, then **Settings -> Pages**, choose the main branch, and save. The dashboard appears at `https://<username>.github.io/<repo>/`.

## Built with
Power BI (original data model and measures), Python (extraction, regression, t-tests, Wilson interval), and vanilla HTML/CSS/JS with inline SVG charts.

## Data note
The CSVs come from the hackathon case data. Confirm you are allowed to publish them before making the repository public.
