import os 
import sys
import traceback
import streamlit as st
import psycopg2
import psycopg2.extras
import pandas as pd
from pathlib import Path
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.init_db import get_db_connection

DB_PATH = Path("logtrack.db")
ph = PasswordHasher()

def get_dict_cursor(con):
    return con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# User authorization
def check_credentials(username, password):
    """
    Gets the user and role associated with username, password if the user exists
    :param username: The name of the user
    :type username: str
    :param password: The user's password
    :type password: str
    :returns: (True, role) if successful authentication, else (False, None)
    """
    try:
        con = get_db_connection()
        cur = get_dict_cursor(con)
        cur.execute("SELECT password_hash, role FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        if row is None:
            return (False, None)
        else:
            db_pw_hash, user_role = row['password_hash'], row['role']
            try:
                if ph.verify(db_pw_hash, password):
                    return (True, user_role)
            except VerifyMismatchError:
                return (False, None)
    except Exception as e:
        print(f"An exception occurred when authenticating {username}: {e}")
        return (False, None)

# Login page
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 LogTrack Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            try:
                ok, role = check_credentials(username, password)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            except Exception:
                print(f"Unexpected error during login attempt for user '{username}':")
                traceback.print_exc()
                st.error("An unexpected error occurred. Please try again later.")

    st.stop()

# Dashboard
st.set_page_config(page_title="LogTrack Dashboard", layout="wide")
st.title("📊 LogTrack Monitoring Dashboard")

# Sidebar
st.sidebar.header("🔎 Filters")
log_limit = st.sidebar.slider("Number of logs to show", 10, 500, 100)

def get_connection():
    try:
        return get_db_connection()
    except Exception as e:
        print(f"An exception occurred when connecting to log database: {e}")
        print("Rule of thumb: run `make reinit` to ensure the database exists")

def load_logs(limit):
    """Loads up to limit number of logs from database"""
    con = get_connection()
    df = pd.read_sql_query(
        f"SELECT id, timestamp, service, message, user FROM logs ORDER BY timestamp DESC LIMIT {limit}",
        con
    )
    con.close()
    return df

def load_alerts():
    """Loads alerts from database"""
    con = get_connection()
    df = pd.read_sql_query("SELECT * FROM alerts ORDER BY triggered_at DESC", con)
    con.close()
    return df

# Tabs
tabs = st.tabs(["🪵 Logs", "🚨 Alerts"])

# Logs Tab
with tabs[0]:
    st.subheader("Recent Logs")
    logs_df = load_logs(log_limit)
    st.dataframe(logs_df, use_container_width=True)

# Alerts Tab
with tabs[1]:
    st.subheader("Triggered Alerts")
    alerts_df = load_alerts()
    if alerts_df.empty:
        st.info("No alerts found.")
    else:
        st.dataframe(alerts_df, use_container_width=True)

        # Optional: Show expanded alert details
        with st.expander("🔍 View Rule Details for First Alert"):
            first_alert = alerts_df.iloc[0]
            st.json({
                "rule_id": first_alert["rule_id"],
                "message": first_alert["message"],
                "log_ids": first_alert["related_log_ids"].split(",")
            })

# Optional: Logout
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Logout"):
    st.session_state.clear()
    st.rerun()