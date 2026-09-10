"""
PeakPulse Product Analyst Assignment
Part 1: Data Exploration & Analysis
Author: Biswa

Step 1: Load all tables, check shapes, dtypes, date ranges, null rates.
"""
import pandas as pd
import numpy as np

pd.set_option('display.width', 140)
pd.set_option('display.max_columns', 20)

DATA = "./Dataset_problem"  # place the unzipped Dataset_problem folder next to this script

users = pd.read_csv(f"{DATA}/users.csv", parse_dates=["created_at", "last_sync_date"])
sessions = pd.read_csv(f"{DATA}/app_sessions.csv", parse_dates=["session_start", "session_end"])
events = pd.read_csv(f"{DATA}/app_events.csv", parse_dates=["event_time"])
subs = pd.read_csv(f"{DATA}/subscriptions.csv", parse_dates=["subscription_start_date", "subscription_end_date", "cancellation_date"])
scores = pd.read_csv(f"{DATA}/daily_scores.csv", parse_dates=["date", "calculated_at"])
sleep = pd.read_csv(f"{DATA}/sleep_data.csv", parse_dates=["sleep_start", "sleep_end"])
activity = pd.read_csv(f"{DATA}/activity_data.csv", parse_dates=["activity_start", "activity_end"])
hrv = pd.read_csv(f"{DATA}/hrv_data.csv", parse_dates=["date"])
journal = pd.read_csv(f"{DATA}/journal_entries.csv", parse_dates=["entry_date"])
teams = pd.read_csv(f"{DATA}/teams.csv", parse_dates=["created_at"])
team_mem = pd.read_csv(f"{DATA}/team_memberships.csv", parse_dates=["joined_at"])

tables = {
    "users": users, "sessions": sessions, "events": events, "subs": subs,
    "scores": scores, "sleep": sleep, "activity": activity, "hrv": hrv,
    "journal": journal, "teams": teams, "team_mem": team_mem
}

print("="*80)
print("SHAPE & DATE RANGE SUMMARY")
print("="*80)
for name, df in tables.items():
    date_cols = [c for c in df.columns if df[c].dtype == 'datetime64[ns]']
    date_info = ""
    if date_cols:
        c = date_cols[0]
        date_info = f" | {c}: {df[c].min()} -> {df[c].max()}"
    print(f"{name:12s} rows={len(df):>8,}  cols={df.shape[1]:>2}{date_info}")

print()
print("="*80)
print("USERS overview")
print("="*80)
print(users['is_active'].value_counts(dropna=False))
print()
print(users['country'].value_counts().head(10))
print()
print(users['acquisition_source'].value_counts())
print()
print("Null rates in users:")
print(users.isna().mean().round(3))

print()
print("="*80)
print("SUBSCRIPTIONS overview")
print("="*80)
print(subs['plan_type'].value_counts())
print(subs['is_canceled'].value_counts())
print("Users with a subscription:", subs['user_id'].nunique(), "/ total users:", users['user_id'].nunique())
