import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Meghna's Study Dashboard", page_icon="📚", layout="wide")

DATA_FILE = "study_log.csv"

# Load existing data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    # Convert to datetime objects for calculation
    df["Date"] = pd.to_datetime(df["Date"])
else:
    df = pd.DataFrame(columns=["Date", "Subject", "Hours"])

# ─────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────
st.title("📚 Meghna's Personal Study Dashboard")
st.write("Track your study sessions, goals, and progress.")
st.divider()

# ─────────────────────────────────────────────
# SECTION 1: METRICS
# ─────────────────────────────────────────────
st.subheader("📊 Overview")

if not df.empty:
    total_hours = int(df["Hours"].sum())
    total_sessions = len(df)
    most_studied = df["Subject"].mode()[0]
    avg_hours = round(float(np.mean(df["Hours"])), 2)
else:
    total_hours, total_sessions, most_studied, avg_hours = 0, 0, "None", 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("📚 Total Hours", total_hours)
col2.metric("✅ Total Sessions", total_sessions)
col3.metric("⭐ Most Studied", most_studied)
col4.metric("⏱️ Avg Hours/Session", avg_hours)

st.divider()

# ─────────────────────────────────────────────
# SECTION 2: GOAL TRACKER
# ─────────────────────────────────────────────
st.subheader("🎯 Weekly Goal Tracker")
weekly_goal = st.slider("Set your weekly study goal (hours)", 5, 50, 20)

if not df.empty:
    # Use pandas to find the start of the current week (Monday)
    today = pd.Timestamp.now().normalize()
    start_of_week = today - pd.Timedelta(days=today.weekday())
    
    # Filter using pure pandas Timestamps
    this_week_df = df[df["Date"] >= start_of_week]
    weekly_hours = int(this_week_df["Hours"].sum())
else:
    weekly_hours = 0

goal_percent = min(int((weekly_hours / weekly_goal) * 100), 100)
col1, col2 = st.columns(2)
col1.metric("📅 Hours This Week", weekly_hours)
col2.metric("🎯 Goal", f"{weekly_goal} hrs")
st.progress(goal_percent)

st.divider()

# ─────────────────────────────────────────────
# SECTION 3: ANALYSIS
# ─────────────────────────────────────────────
st.subheader("📈 Analysis")

if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Hours by Subject**")
        subject_data = df.groupby("Subject")["Hours"].sum().reset_index()
        st.bar_chart(subject_data.set_index("Subject"))
    with col2:
        st.write("**Hours Over Time**")
        time_data = df.groupby("Date")["Hours"].sum().reset_index()
        st.line_chart(time_data.set_index("Date"))
else:
    st.info("No data yet.")

st.divider()

# ─────────────────────────────────────────────
# SECTION 4: TABLE
# ─────────────────────────────────────────────
st.subheader("📋 All Study Sessions")

if not df.empty:
    # We display a copy so we don't break the original data types
    display_df = df.copy()
    display_df["Date"] = display_df["Date"].dt.strftime('%Y-%m-%d')
    st.dataframe(display_df.sort_values("Date", ascending=False), use_container_width=True)

    # Download button
    csv_content = display_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", csv_content, "study_log.csv", "text/csv")
else:
    st.info("No sessions logged yet.")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.header("➕ Log Study Session")
subject = st.sidebar.text_input("Subject", placeholder="e.g. Java, Python")
hours = st.sidebar.slider("Hours studied", 1, 10, 2)
date_input = st.sidebar.date_input("Date")

if st.sidebar.button("💾 Save Session"):
    if subject.strip() == "":
        st.sidebar.error("Please enter a subject!")
    else:
        # Save as a standard string YYYY-MM-DD
        new_row = pd.DataFrame({
            "Date": [pd.to_datetime(date_input)],
            "Subject": [subject.strip()],
            "Hours": [hours]
        })
        updated_df = pd.concat([df, new_row], ignore_index=True)
        updated_df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("Saved!")
        st.rerun()
