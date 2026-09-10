"""
Task 5: Analyze the onboarding funnel to identify drop-off points
Onboarding per product spec: Device purchase -> app installation -> account
creation -> device pairing -> initial calibration (7-14 days)

We approximate the funnel using:
  Step 1: Account created (all users.csv rows = account creation)
  Step 2: First session logged (app installed & opened)
  Step 3: Calibration complete (calibration_complete flag)
  Step 4: First daily score generated (device paired & producing data)
  Step 5: Still active 30 days later (is_active)
"""
import pandas as pd
import numpy as np

DATA = "./Dataset_problem"  # place the unzipped Dataset_problem folder next to this script
users = pd.read_csv(f"{DATA}/users.csv", parse_dates=["created_at", "last_sync_date"])
sessions = pd.read_csv(f"{DATA}/app_sessions.csv", parse_dates=["session_start", "session_end"])
scores = pd.read_csv(f"{DATA}/daily_scores.csv", parse_dates=["date", "calculated_at"])

total_users = len(users)

# Step 2: users who ever had a session
users_with_session = sessions['user_id'].nunique()

# Step 3: calibration complete
users_calibrated = users['calibration_complete'].sum()

# Step 4: users who have at least one daily_score
users_with_score = scores['user_id'].nunique()

# Step 5: currently active
users_active = users['is_active'].sum()

funnel = pd.DataFrame({
    'step': ['Account created', 'First app session', 'Calibration complete',
             'First daily score generated', 'Still active today'],
    'users': [total_users, users_with_session, users_calibrated, users_with_score, users_active]
})
funnel['pct_of_total'] = (funnel['users'] / total_users * 100).round(1)
funnel['pct_of_prev_step'] = (funnel['users'] / funnel['users'].shift(1) * 100).round(1)
print(funnel)

# Time-to-calibrate: first session date vs created_at, for calibrated vs not
first_session = sessions.groupby('user_id')['session_start'].min().rename('first_session')
u = users.merge(first_session, on='user_id', how='left')
u['days_to_first_session'] = (u['first_session'] - u['created_at']).dt.days

print("\nDays from account creation to first app session:")
print(u['days_to_first_session'].describe().round(1))

print("\nCalibration completion rate by whether they ever had a session:")
u['had_session'] = u['first_session'].notna()
print(u.groupby('had_session')['calibration_complete'].mean().round(3))

print("\nCalibration completion rate by acquisition source:")
print(u.groupby('acquisition_source')['calibration_complete'].mean().sort_values().round(3))

print("\nCalibration completion rate by country:")
print(u.groupby('country')['calibration_complete'].mean().sort_values().round(3))

print("\nis_active rate by calibration_complete:")
print(u.groupby('calibration_complete')['is_active'].mean().round(3))
