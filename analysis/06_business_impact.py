"""
Part 2, Task: Quantify the business impact of the churn issue
"""
import pandas as pd
import numpy as np

DATA = "./Dataset_problem"  # place the unzipped Dataset_problem folder next to this script
subs = pd.read_csv(f"{DATA}/subscriptions.csv", parse_dates=["subscription_start_date", "subscription_end_date", "cancellation_date"])
users = pd.read_csv(f"{DATA}/users.csv", parse_dates=["created_at"])

print("Pricing by plan_type:")
print(subs.groupby('plan_type')[['initial_price','renewal_price']].agg(['mean','count']))

# Normalize to a monthly value for comparability.
# ASSUMPTION (schema has no explicit term-length field, stated per submission
# guidelines): initial_price by plan is monthly=$30, annual=$300, biannual=$240.
# We read "annual" as a 12-month term ($300/yr = $25/mo) and "biannual" as a
# 24-month term ($240/24mo = $10/mo), consistent with deeper discounts for
# longer commitment. subscription_end_date is only populated for monthly
# plans in this dataset, so term length for annual/biannual can't be verified
# directly from the data and this is treated as an explicit assumption.
plan_monthly_value = {
    'monthly': 30.0,
    'annual': 300.0 / 12,   # $25/mo
    'biannual': 240.0 / 24  # $10/mo
}
print("\nAssumed monthly-equivalent value:", plan_monthly_value)

subs['monthly_value'] = subs['plan_type'].map(plan_monthly_value)

# total subs / users
total_users = users['user_id'].nunique()
canceled = subs[subs['is_canceled']]
retained_subs = subs[~subs['is_canceled']]

print(f"\nTotal subscribers in dataset: {len(subs)}")
print(f"Canceled: {len(canceled)} ({len(canceled)/len(subs):.1%})")
print(f"Currently retained: {len(retained_subs)} ({len(retained_subs)/len(subs):.1%})")

# Monthly recurring revenue currently retained
current_mrr = retained_subs['monthly_value'].sum()
print(f"\nCurrent MRR from retained subscribers: ${current_mrr:,.0f}/mo")

# Lost MRR from churned users (what they WOULD be contributing if retained)
lost_mrr = canceled['monthly_value'].sum()
print(f"MRR forfeited from churned subscribers: ${lost_mrr:,.0f}/mo -> ${lost_mrr*12:,.0f}/yr")

# Gap to 85% renewal target
actual_renewal_rate = 1 - subs['is_canceled'].mean()
target_renewal_rate = 0.85
gap = target_renewal_rate - actual_renewal_rate
print(f"\nActual renewal rate: {actual_renewal_rate:.1%}  |  Target: {target_renewal_rate:.0%}  |  Gap: {gap:.1%} pts")

users_that_would_be_retained_at_target = int(round(target_renewal_rate * len(subs)))
extra_retained_users_needed = users_that_would_be_retained_at_target - len(retained_subs)
print(f"Users retained today: {len(retained_subs)}  |  Users retained at 85% target: {users_that_would_be_retained_at_target}")
print(f"Additional users that would need to be retained: {extra_retained_users_needed}")

avg_monthly_value = subs['monthly_value'].mean()
annual_revenue_gap = extra_retained_users_needed * avg_monthly_value * 12
print(f"Average monthly value per subscriber: ${avg_monthly_value:.2f}")
print(f"Estimated ANNUAL revenue opportunity from closing the gap to 85% target: ${annual_revenue_gap:,.0f}")

# Device revenue already captured (one-time $300), so churn doesn't erase that, only subscription revenue
print("\n(Note: $300 one-time device revenue is already captured at purchase and is NOT at risk from subscription churn;")
print(" only recurring subscription revenue is at risk, though churned users are unlikely to buy a 2nd device / referrals.)")

# Early churn specifically (first 30 days) - the cliff we found
canceled2 = canceled.copy()
canceled2['duration_days'] = (canceled2['cancellation_date'] - canceled2['subscription_start_date']).dt.days
early_churn = canceled2[canceled2['duration_days'] <= 30]
print(f"\nUsers who churned within first 30 days: {len(early_churn)} ({len(early_churn)/len(subs):.1%} of all subscribers)")
print(f"That's {len(early_churn)/len(canceled2):.1%} of ALL churned users -- the dominant churn window")
lost_mrr_early = early_churn['monthly_value'].sum()
print(f"MRR forfeited from early (<=30 day) churners alone: ${lost_mrr_early:,.0f}/mo -> ${lost_mrr_early*12:,.0f}/yr")
