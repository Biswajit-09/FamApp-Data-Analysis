# PeakPulse Product Analysis — Subscriber Retention Deep Dive

**Author:** Biswa
**Context:** Product Analyst take-home assignment — analysis of PeakPulse (a
recovery/strain/sleep fitness wearable) user and subscription data to identify
the biggest issue affecting business goals, quantify its impact, and
recommend fixes.

## TL;DR

- **Retention collapses in the first 30 days.** 98% of subscribers survive the
  first week, but only **56.8%** make it to day 30 — far short of the
  business's 85% renewal target. **74% of all churn happens within that first
  30-day window**, concentrated right around the first renewal charge
  (median cancellation: day 25).
- **App engagement predicts retention — health metrics and community features
  don't.** Retained users open the app 85% more often than churned users
  (the strongest signal found, r = 0.29). Recovery/sleep/strain scores,
  device-wear time, and team membership all show ~0 correlation with
  retention.
- **Annual and biannual plans churn 2–3x harder than monthly plans** — the
  opposite of the usual subscription pattern, and worth investigating further.
- **Business impact:** ~$894K/yr in forfeited recurring revenue from users
  who have already churned; ~$691K/yr in opportunity from closing the gap to
  the 85% retention target, $698K/yr of which sits in the first-30-days
  window alone.

Full findings, business-impact quantification, and 3 data-backed
recommendations are in [`presentation/PeakPulse_Retention_Analysis.pdf`](presentation/PeakPulse_Retention_Analysis.pdf).

## Repo structure

```
├── analysis/               Python analysis scripts (run in order, 01→06)
│   ├── 01_explore.py            Data loading, shapes, null rates
│   ├── 02_retention.py          D7/D30/D90 retention curves, cohort & plan churn
│   ├── 03_onboarding_funnel.py  Onboarding drop-off funnel
│   ├── 04_features_vs_retention.py  Feature correlation, retained vs. churned
│   ├── 05_anomalies.py          Data quality checks + trend anomalies
│   ├── 06_business_impact.py    Revenue-at-risk quantification
│   └── METHODOLOGY.md           How to run the scripts + every assumption made
└── presentation/            Final deliverable (5-7 slide deck)
    ├── PeakPulse_Retention_Analysis.pdf
    └── PeakPulse_Retention_Analysis.pptx
```

## Dataset

The assignment's `Dataset_problem.zip` (11 CSVs: users, app_sessions,
app_events, subscriptions, daily_scores, sleep_data, activity_data, hrv_data,
journal_entries, teams, team_memberships — ~5,000 users) is not included here
since it was provided directly by the company and isn't mine to redistribute.
To reproduce: unzip it into `analysis/Dataset_problem/` and follow
[`analysis/METHODOLOGY.md`](analysis/METHODOLOGY.md).

## Key assumptions

- No free tier exists in the data — every user already holds a subscription —
  so the "free → premium conversion funnel" task was reinterpreted as an
  onboarding → active-subscriber funnel.
- Annual/biannual plan term lengths aren't stored explicitly; I assumed a
  12-month term for annual ($300/yr) and 24-month term for biannual ($240),
  based on relative pricing. This feeds the revenue figures above — see
  `METHODOLOGY.md` for the full reasoning.
- A sharp cancellation spike in the final two weeks of the data window is
  flagged as an anomaly, not treated as a confirmed trend (see
  `analysis/05_anomalies.py` and the presentation's methodology slide).

Full assumption list and methodology notes: [`analysis/METHODOLOGY.md`](analysis/METHODOLOGY.md).
