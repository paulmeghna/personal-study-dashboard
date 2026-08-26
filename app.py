import streamlit as st

st.set_page_config(page_title="Personal Study Dashboard", page_icon="📚")

st.title("📚 Personal Study Dashboard")
st.markdown("---")

st.sidebar.header("Navigation")
st.sidebar.button("Dashboard")
st.sidebar.button("Study Log")
st.sidebar.button("Goals")
st.sidebar.button("Analytics")

st.header("Welcome to Your Study Dashboard")
st.subheader("Track your learning journey effectively")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Today's Study", "0 hours")
with col2:
    st.metric("Weekly Total", "0 hours")
with col3:
    st.metric("Subjects", "0")

st.markdown("---")
st.write("Ready to log your first study session?")
