"""
Task 2: Identify which features correlate most strongly with user retention
Task 6: Compare behavior patterns between retained users and churned users
Task 7: Examine session frequency and duration across user segments
"""
import pandas as pd
import numpy as np

DATA = "./Dataset_problem"  # place the unzipped Dataset_problem folder next to this script
users = pd.read_csv(f"{DATA}/users.csv", parse_dates=["created_at", "last_sync_date"])
sessions = pd.read_csv(f"{DATA}/app_sessions.csv", parse_dates=["session_start", "session_end"])
subs = pd.read_csv(f"{DATA}/subscriptions.csv", parse_dates=["subscription_start_date", "subscription_end_date", "cancellation_date"])
scores = pd.read_csv(f"{DATA}/daily_scores.csv", parse_dates=["date", "calculated_at"])
journal = pd.read_csv(f"{DATA}/journal_entries.csv", parse_dates=["entry_date"])
team_mem = pd.read_csv(f"{DATA}/team_memberships.csv", parse_dates=["joined_at"])
events = pd.read_csv(f"{DATA}/app_events.csv", parse_dates=["event_time"])

# retained = subscription NOT canceled
retained = subs[['user_id', 'is_canceled', 'plan_type', 'initial_price', 'renewal_price']].copy()
retained['retained'] = ~retained['is_canceled']

# ---- session-level features ----
sess_agg = sessions.groupby('user_id').agg(
    n_sessions=('session_id', 'count'),
    avg_session_secs=('session_duration_seconds', 'mean'),
    total_session_secs=('session_duration_seconds', 'sum'),
    crash_rate=('is_crashed', 'mean'),
).reset_index()

# ---- daily score features (device engagement / health metrics) ----
score_agg = scores.groupby('user_id').agg(
    n_score_days=('score_id', 'count'),
    avg_recovery=('recovery_score', 'mean'),
    avg_strain=('strain_score', 'mean'),
    avg_sleep_score=('sleep_score', 'mean'),
    avg_active_minutes=('active_minutes', 'mean'),
    journal_rate=('has_journal_entry', 'mean'),
).reset_index()

# ---- journal engagement ----
journal_agg = journal.groupby('user_id').size().rename('n_journal_entries').reset_index()

# ---- community engagement ----
team_agg = team_mem.groupby('user_id').size().rename('n_teams_joined').reset_index()

# ---- app feature breadth (distinct feature_category touched) ----
feat_breadth = events.groupby('user_id')['feature_category'].nunique().rename('n_feature_categories').reset_index()

# ---- merge everything onto users ----
df = users.merge(retained, on='user_id', how='left')
df = df.merge(sess_agg, on='user_id', how='left')
df = df.merge(score_agg, on='user_id', how='left')
df = df.merge(journal_agg, on='user_id', how='left')
df = df.merge(team_agg, on='user_id', how='left')
df = df.merge(feat_breadth, on='user_id', how='left')

fillcols = ['n_sessions', 'avg_session_secs', 'total_session_secs', 'crash_rate',
            'n_score_days', 'n_journal_entries', 'n_teams_joined', 'n_feature_categories']
for c in fillcols:
    df[c] = df[c].fillna(0)

df.to_csv('user_features.csv', index=False)
print(f"Built user feature table: {df.shape}")
print("Retained overall:", df['retained'].mean().round(3))

# ---- Task 6: compare retained vs churned ----
compare_cols = ['n_sessions', 'avg_session_secs', 'crash_rate', 'n_score_days',
                 'avg_recovery', 'avg_strain', 'avg_sleep_score', 'avg_active_minutes',
                 'journal_rate', 'n_journal_entries', 'n_teams_joined', 'n_feature_categories',
                 'calibration_complete', 'notification_enabled']

print("\n" + "="*90)
print("RETAINED vs CHURNED -- mean feature comparison")
print("="*90)
comp = df.groupby('retained')[compare_cols].mean().T
comp.columns = ['churned', 'retained']
comp['pct_diff'] = ((comp['retained'] - comp['churned']) / comp['churned'].replace(0, np.nan) * 100).round(1)
print(comp.round(3))

# ---- Task 2: correlation of numeric features with retained (point-biserial ~ pearson w/ 0/1) ----
print("\n" + "="*90)
print("CORRELATION of features with retention (retained=1/0)")
print("="*90)
df['retained_int'] = df['retained'].astype(int)
corr_cols = compare_cols + ['retained_int']
corrs = df[corr_cols].corr()['retained_int'].drop('retained_int').sort_values(key=abs, ascending=False)
print(corrs.round(3))

# ---- Team membership vs retention specifically ----
df['on_team'] = df['n_teams_joined'] > 0
print("\nRetention rate: on a team vs not:")
print(df.groupby('on_team')['retained'].mean().round(3))
print(df.groupby('on_team')['retained'].count())

# ---- Journaling vs retention ----
df['journals_regularly'] = df['journal_rate'] > df['journal_rate'].median()
print("\nRetention rate: journals >median vs <=median:")
print(df.groupby('journals_regularly')['retained'].mean().round(3))

# ---- Task 7: session frequency/duration by segment (age_group, plan_type, country) ----
print("\n" + "="*90)
print("SESSION FREQUENCY / DURATION BY SEGMENT")
print("="*90)
for seg in ['age_group', 'plan_type', 'app_platform', 'acquisition_source']:
    print(f"\n--- by {seg} ---")
    g = df.groupby(seg)[['n_sessions', 'avg_session_secs', 'retained']].mean().round(2)
    g['n_users'] = df.groupby(seg).size()
    print(g.sort_values('n_sessions', ascending=False))
