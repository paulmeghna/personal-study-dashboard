import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

st.set_page_config(
    page_title="Meghna's Study Dashboard",
    page_icon="📚",
    layout="wide"
)

DATA_FILE = "study_log.csv"
COLUMNS = ["Date", "Subject", "Hours", "Type", "Focus"]


def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        # Ensure all expected columns exist
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = np.nan

        # Keep only expected columns in correct order
        df = df[COLUMNS].copy()

        # Clean and convert data types
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Subject"] = df["Subject"].astype(str).str.strip()
        df["Subject"] = df["Subject"].replace("nan", np.nan)
        df["Hours"] = pd.to_numeric(df["Hours"], errors="coerce")
        df["Focus"] = pd.to_numeric(df["Focus"], errors="coerce")
    else:
        df = pd.DataFrame(columns=COLUMNS)

    return df


df = load_data()
clean_df = df.dropna(subset=["Date", "Subject", "Hours"]).copy()

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

if not clean_df.empty:
    total_hours = round(float(clean_df["Hours"].sum()), 1)
    total_sessions = int(len(clean_df))
    most_studied = (
        clean_df["Subject"].mode().iloc[0]
        if not clean_df["Subject"].mode().empty
        else "None"
    )
    avg_hours = round(float(clean_df["Hours"].mean()), 2)
    avg_focus = (
        round(float(clean_df["Focus"].dropna().mean()), 1)
        if clean_df["Focus"].notna().any()
        else 0
    )
else:
    total_hours = 0
    total_sessions = 0
    most_studied = "None"
    avg_hours = 0
    avg_focus = 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📚 Total Hours", total_hours)
col2.metric("✅ Total Sessions", total_sessions)
col3.metric("⭐ Most Studied", most_studied)
col4.metric("⏱️ Avg Hours/Session", avg_hours)
col5.metric("🎯 Avg Focus", avg_focus)

st.divider()

# ─────────────────────────────────────────────
# SECTION 2: GOAL TRACKER
# ─────────────────────────────────────────────
st.subheader("🎯 Weekly Goal Tracker")

weekly_goal = st.slider("Set your weekly study goal (hours)", 5, 50, 20)

if not clean_df.empty:
    today = pd.Timestamp.today().normalize()
    start_of_week = today - pd.Timedelta(days=today.weekday())
    end_of_week = start_of_week + pd.Timedelta(days=7)

    this_week_df = clean_df[
        (clean_df["Date"] >= start_of_week) & (clean_df["Date"] < end_of_week)
    ]
    weekly_hours = round(float(this_week_df["Hours"].sum()), 1)
else:
    weekly_hours = 0.0

goal_percent = int((weekly_hours / weekly_goal) * 100) if weekly_goal > 0 else 0
progress_value = min(goal_percent, 100)

goal_col1, goal_col2 = st.columns(2)
goal_col1.metric("📅 Hours This Week", weekly_hours)
goal_col2.metric("🎯 Goal", f"{weekly_goal} hrs")
st.progress(progress_value)

if weekly_hours >= weekly_goal:
    st.success("Great job! You have achieved your weekly study goal. 🎉")
else:
    remaining = round(weekly_goal - weekly_hours, 1)
    st.info(f"You need {remaining} more hour(s) to reach your weekly goal.")

st.divider()

# ─────────────────────────────────────────────
# SECTION 3: ANALYSIS
# ─────────────────────────────────────────────
st.subheader("📈 Analysis")

if not clean_df.empty:
    tab1, tab2, tab3, tab4 = st.tabs([
        "Hours by Subject",
        "Hours Over Time",
        "Sessions by Type",
        "Average Focus by Subject"
    ])

    with tab1:
        st.markdown("### Hours by Subject")
        subject_data = (
            clean_df.groupby("Subject", as_index=False)["Hours"]
            .sum()
            .sort_values("Hours", ascending=False)
        )
        st.bar_chart(subject_data.set_index("Subject"), use_container_width=True)

    with tab2:
        st.markdown("### Hours Over Time")
        time_data = (
            clean_df.groupby("Date", as_index=False)["Hours"]
            .sum()
            .sort_values("Date")
        )
        st.line_chart(time_data.set_index("Date"), use_container_width=True)

    with tab3:
        st.markdown("### Sessions by Type")
        if clean_df["Type"].notna().any():
            type_data = (
                clean_df["Type"]
                .fillna("Unknown")
                .value_counts()
                .reset_index()
            )
            type_data.columns = ["Type", "Count"]
            st.bar_chart(type_data.set_index("Type"), use_container_width=True)
        else:
            st.info("No session type data available yet.")

    with tab4:
        st.markdown("### Average Focus by Subject")
        focus_df = clean_df.dropna(subset=["Focus"]).copy()
        if not focus_df.empty:
            focus_data = (
                focus_df.groupby("Subject", as_index=False)["Focus"]
                .mean()
                .sort_values("Focus", ascending=False)
            )
            st.bar_chart(focus_data.set_index("Subject"), use_container_width=True)
        else:
            st.info("No focus data available yet.")
else:
    st.info("No study data available yet. Log your first session to unlock analysis.")

st.divider()

# ─────────────────────────────────────────────
# SECTION 4: TABLE
# ─────────────────────────────────────────────
st.subheader("📋 All Study Sessions")

if not df.empty:
    display_df = df.copy()
    display_df = display_df.sort_values("Date", ascending=False, na_position="last")
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_df, use_container_width=True)

    csv_content = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download CSV",
        csv_content,
        "study_log.csv",
        "text/csv"
    )
else:
    st.info("No sessions logged yet.")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.header("➕ Log Study Session")

subject = st.sidebar.text_input("Subject", placeholder="e.g. Python, Pandas")
hours = st.sidebar.slider("Hours studied", 0.5, 10.0, 2.0, step=0.5)
session_type = st.sidebar.selectbox(
    "Session Type",
    ["New Learning", "Revision", "Practice", "Assignment"]
)
focus_rating = st.sidebar.slider(
    "Focus Level (1 = Distracted, 5 = Deep Work)",
    1,
    5,
    3
)
date_input = st.sidebar.date_input("Date", value=datetime.today())

if st.sidebar.button("💾 Save Session"):
    if subject.strip() == "":
        st.sidebar.error("Please enter a subject!")
    else:
        new_row = pd.DataFrame([{
            "Date": pd.to_datetime(date_input),
            "Subject": subject.strip(),
            "Hours": hours,
            "Type": session_type,
            "Focus": focus_rating
        }])

        updated_df = pd.concat([df, new_row], ignore_index=True)
        updated_df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("Session saved successfully!")
        st.rerun()
