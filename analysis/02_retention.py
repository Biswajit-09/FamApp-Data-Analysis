"""
Task 1: Analyze user retention patterns over the past 3 months
Task 3: Examine the conversion funnel (here: onboarding -> paid retention,
        since every user in this dataset already holds a subscription --
        there is no separate free tier in the data, so we treat the
        "conversion" funnel as onboarding completion -> active subscriber)
"""
import pandas as pd
import numpy as np

pd.set_option('display.width', 140)

DATA = "./Dataset_problem"  # place the unzipped Dataset_problem folder next to this script
users = pd.read_csv(f"{DATA}/users.csv", parse_dates=["created_at", "last_sync_date"])
subs = pd.read_csv(f"{DATA}/subscriptions.csv", parse_dates=["subscription_start_date", "subscription_end_date", "cancellation_date"])

MAX_DATE = subs['subscription_start_date'].max()
print("Latest subscription start date in data:", MAX_DATE)
print("Earliest:", subs['subscription_start_date'].min())

# ---- Overall churn ----
churn_rate = subs['is_canceled'].mean()
print(f"\nOverall cancellation rate across all subscriptions: {churn_rate:.1%}")

# ---- Retention by cohort month (based on subscription start / user signup month) ----
subs['start_month'] = subs['subscription_start_date'].dt.to_period('M')
cohort = subs.groupby('start_month').agg(
    n_subs=('subscription_id', 'count'),
    n_canceled=('is_canceled', 'sum')
)
cohort['cancel_rate'] = (cohort['n_canceled'] / cohort['n_subs']).round(3)
print("\nCancellation rate by subscription start-month cohort:")
print(cohort)

# ---- Retention by plan type ----
plan_cancel = subs.groupby('plan_type')['is_canceled'].agg(['count', 'mean'])
plan_cancel.columns = ['n', 'cancel_rate']
print("\nCancellation rate by plan type:")
print(plan_cancel.sort_values('cancel_rate', ascending=False))

# ---- Subscription duration (days) for canceled subs ----
canceled = subs[subs['is_canceled']].copy()
canceled['duration_days'] = (canceled['cancellation_date'] - canceled['subscription_start_date']).dt.days
print("\nDuration (days) before cancellation -- describe:")
print(canceled['duration_days'].describe().round(1))

# Bucket into classic retention windows
def bucket(d):
    if d <= 7: return '0-7 days (D7 churn)'
    if d <= 30: return '8-30 days (D30 churn)'
    if d <= 90: return '31-90 days (D90 churn)'
    if d <= 180: return '91-180 days (D180 churn)'
    return '180+ days'
canceled['bucket'] = canceled['duration_days'].apply(bucket)
print("\nWhen do canceled users churn?")
print(canceled['bucket'].value_counts().reindex([
    '0-7 days (D7 churn)', '8-30 days (D30 churn)', '31-90 days (D90 churn)',
    '91-180 days (D180 churn)', '180+ days']))

# ---- Cancellation reasons ----
print("\nCancellation reasons:")
print(canceled['cancellation_reason'].value_counts())
print("\nCancellation reasons (%):")
print((canceled['cancellation_reason'].value_counts(normalize=True) * 100).round(1))

# ---- classic D7/D30/D90 retention (survival curve) among all subs ----
# retained_at_X = subscription lasted at least X days (i.e. not canceled within X days), among subs old enough to be observed for X days
subs['end_or_now'] = subs['subscription_end_date'].fillna(MAX_DATE)
subs['is_canceled_bool'] = subs['is_canceled']
subs['observed_days'] = (subs['end_or_now'] - subs['subscription_start_date']).dt.days.clip(lower=0)
# for cancellations we know exact churn day; for still-active we only know they've survived 'observed_days' so far
canceled_only = subs[subs['is_canceled_bool']].copy()
canceled_only['days_to_churn'] = (canceled_only['cancellation_date'] - canceled_only['subscription_start_date']).dt.days

for window in [7, 30, 90, 180]:
    eligible = subs[subs['subscription_start_date'] <= MAX_DATE - pd.Timedelta(days=window)]
    churned_within = eligible['user_id'].isin(
        canceled_only[canceled_only['days_to_churn'] <= window]['user_id']
    )
    retention = 1 - churned_within.mean()
    print(f"D{window} retention (eligible cohort n={len(eligible)}): {retention:.1%}")
