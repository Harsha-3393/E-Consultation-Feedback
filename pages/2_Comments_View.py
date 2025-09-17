import streamlit as st
import sqlite3
import pandas as pd

st.title("Comments View")
st.markdown("A log of all analyzed comments.")

with sqlite3.connect('comments.db') as conn:
    df = pd.read_sql_query("SELECT comment, sentiment, intent, author, timestamp FROM comments ORDER BY timestamp DESC", conn)

st.dataframe(df, width='stretch')