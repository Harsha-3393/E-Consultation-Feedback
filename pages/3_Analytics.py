import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("Analytics")
st.markdown("Visual insights into comment data.")

with sqlite3.connect('comments.db') as conn:
    df = pd.read_sql_query("SELECT sentiment, intent FROM comments", conn)

if not df.empty:
    # Sentiment Chart
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    sentiment_fig = px.pie(sentiment_counts, values='Count', names='Sentiment', title='Sentiment Distribution')
    st.plotly_chart(sentiment_fig, width='stretch')
    
    # Intent Chart
    intent_counts = df['intent'].value_counts().reset_index()
    intent_counts.columns = ['Intent', 'Count']
    intent_fig = px.bar(intent_counts, x='Intent', y='Count', title='Intent Distribution')
    st.plotly_chart(intent_fig, width='stretch')
else:
    st.info("No data available to display analytics. Please add some comments first.")