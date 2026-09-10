"""
Task 4: Investigate any anomalies or concerning trends in the data
"""
import pandas as pd
import numpy as np

DATA = "./Dataset_problem"  # place the unzipped Dataset_problem folder next to this script
users = pd.read_csv(f"{DATA}/users.csv", parse_dates=["created_at", "last_sync_date"])
sessions = pd.read_csv(f"{DATA}/app_sessions.csv", parse_dates=["session_start", "session_end"])
subs = pd.read_csv(f"{DATA}/subscriptions.csv", parse_dates=["subscription_start_date", "subscription_end_date", "cancellation_date"])
scores = pd.read_csv(f"{DATA}/daily_scores.csv", parse_dates=["date", "calculated_at"])
sleep = pd.read_csv(f"{DATA}/sleep_data.csv", parse_dates=["sleep_start", "sleep_end"])
hrv = pd.read_csv(f"{DATA}/hrv_data.csv", parse_dates=["date"])

print("1) Session anomalies")
print("Negative/zero duration sessions:", (sessions['session_duration_seconds'] <= 0).sum())
print("Extremely long sessions (>2 hrs):", (sessions['session_duration_seconds'] > 7200).sum())
print("Crash rate overall:", sessions['is_crashed'].mean().round(4))
print("Crash rate by platform:")
print(sessions.merge(users[['user_id','app_platform']], on='user_id').groupby('app_platform')['is_crashed'].mean().round(4))
print("Crash rate by app_version (top 8 by volume):")
vc = sessions['app_version'].value_counts().head(8).index
print(sessions[sessions['app_version'].isin(vc)].groupby('app_version')['is_crashed'].agg(['count','mean']).round(4))

print("\n2) Subscription price anomalies")
print("Distinct initial_price values:", sorted(subs['initial_price'].unique())[:10])
print("renewal_price > initial_price (price hike) count:", (subs['renewal_price'] > subs['initial_price']).sum())
subs['price_hike_pct'] = ((subs['renewal_price'] - subs['initial_price']) / subs['initial_price'] * 100).round(1)
print(subs.loc[subs['renewal_price'] > subs['initial_price'], 'price_hike_pct'].describe().round(1))
print("\nCancellation rate for price-hiked subs vs not:")
print(subs.groupby(subs['renewal_price'] > subs['initial_price'])['is_canceled'].mean().round(3))

print("\n3) Daily score anomalies")
print("recovery_score out of expected 0-100 range:", ((scores['recovery_score']<0)|(scores['recovery_score']>100)).sum())
print("sleep_score out of expected 0-100 range:", ((scores['sleep_score']<0)|(scores['sleep_score']>100)).sum())
print("strain_score out of expected 0-21 range:", ((scores['strain_score']<0)|(scores['strain_score']>21)).sum())
print("is_complete = False count:", (~scores['is_complete']).sum(), f"({(~scores['is_complete']).mean():.1%})")

print("\n4) Sleep anomalies")
print("total_sleep_minutes > time_in_bed_minutes (impossible):", (sleep['total_sleep_minutes'] > sleep['time_in_bed_minutes']).sum())
print("total_sleep_minutes <= 0:", (sleep['total_sleep_minutes'] <= 0).sum())
print("Very short sleep <2hrs (120 min), non-nap:", ((sleep['total_sleep_minutes']<120) & (~sleep['is_nap'])).sum())

print("\n5) HRV anomalies")
print("hrv_ms <=0 or >200 (physiologically implausible):", ((hrv['hrv_ms']<=0)|(hrv['hrv_ms']>200)).sum())
print(hrv['hrv_ms'].describe().round(1))

print("\n6) Weekly new-subscription volume trend (concerning trend check)")
subs['week'] = subs['subscription_start_date'].dt.to_period('W')
weekly = subs.groupby('week').size()
print(weekly)

print("\n7) Weekly cancellation volume trend")
canceled = subs[subs['is_canceled']].copy()
canceled['cancel_week'] = canceled['cancellation_date'].dt.to_period('W')
print(canceled.groupby('cancel_week').size())
