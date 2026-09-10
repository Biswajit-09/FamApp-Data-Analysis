# PeakPulse Product Analyst Assignment — Analysis Code

Author: Biswa

## How to run

Requirements: Python 3, `pandas`, `numpy` (install with `pip install pandas numpy --break-system-packages` if needed).

1. Unzip `Dataset_problem.zip` so that its CSVs sit in a folder named `Dataset_problem/`
   next to these scripts (or edit the `DATA` path at the top of each script).
2. Run scripts in order — each one is self-contained and prints its findings to
   stdout; later scripts don't depend on earlier ones except `04_features_vs_retention.py`,
   which writes `user_features.csv` (a per-user feature table used only within that script).

```bash
python3 01_explore.py                  # shapes, date ranges, null rates, high-level counts
python3 02_retention.py                # Task 1 & 3: retention curves, cohort/plan churn, cancellation timing
python3 03_onboarding_funnel.py        # Task 5: onboarding drop-off funnel
python3 04_features_vs_retention.py    # Task 2 & 6 & 7: feature correlation, retained-vs-churned, segments
python3 05_anomalies.py                # Task 4: data quality checks + trend anomalies
python3 06_business_impact.py          # Part 2: revenue-at-risk quantification
```

## Methodology notes / assumptions

- **"Retained" is defined as `subscriptions.is_canceled == False`** as of the data
  snapshot (latest `subscription_start_date` in the data: 2023-06-08). This dataset
  has no free tier — every user already holds a subscription — so Part 1's "free →
  premium conversion funnel" question was reinterpreted as an **onboarding →
  active-subscriber funnel** (account creation → first app session → calibration
  complete → first daily score → currently active). This is called out explicitly
  because it departs from the literal wording of the assignment task.
- **Plan pricing terms are assumed, not verified.** `subscription_end_date` is only
  populated for `monthly` plans in this dataset. For `annual` ($300) and `biannual`
  ($240) plans there's no explicit term-length field, so I assumed a 12-month term
  for annual and a 24-month term for biannual (consistent with biannual being the
  cheaper plan per dollar, i.e. a bulk-commitment discount). This assumption feeds
  directly into the monthly-recurring-revenue and business-impact numbers in
  `06_business_impact.py` — if the real term lengths differ, those dollar figures
  should be recalculated.
- **D7/D30/D90 retention** in `02_retention.py` is computed as a survival rate:
  for each window, only subscriptions old enough to have been observable for that
  full window are included in the denominator (an "eligible cohort"), and a
  subscription counts as churned within the window if its `cancellation_date` falls
  inside it. D180 could not be computed — no subscription in the data is yet old
  enough to be observed for a full 180 days.
- **Correlation values** (`04_features_vs_retention.py`) are simple Pearson
  correlations between each numeric feature and a 0/1 retained indicator
  (equivalent to point-biserial correlation) — a reasonable first pass for ranking
  candidate features, not a causal claim.
- **One data anomaly is flagged but deliberately not explained or corrected**:
  weekly cancellation volume spikes sharply in the final two weeks of the data
  window (422 and 335 cancellations respectively) even though new-subscription
  volume had nearly stopped by then. This could reflect a real business event or a
  data export/cutoff artifact — `05_anomalies.py` surfaces it, but I did not treat
  it as ground truth in the business-impact or recommendation numbers.

## Output

The findings from these scripts feed directly into
`PeakPulse_Retention_Analysis.pdf` / `.pptx` (the Part 3 presentation).
