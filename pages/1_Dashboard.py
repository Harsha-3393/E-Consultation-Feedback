import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- DATABASE INTERACTION ---
def get_dashboard_stats():
    with sqlite3.connect('comments.db') as conn:
        cursor = conn.cursor()
        total = cursor.execute('SELECT COUNT(*) FROM comments').fetchone()[0]
        pos_count = cursor.execute("SELECT COUNT(*) FROM comments WHERE sentiment LIKE '%Positive%'").fetchone()[0]
        neg_count = cursor.execute("SELECT COUNT(*) FROM comments WHERE sentiment LIKE '%Negative%'").fetchone()[0]
        neu_count = cursor.execute("SELECT COUNT(*) FROM comments WHERE sentiment = 'Neutral'").fetchone()[0]
    return total, pos_count, neg_count, neu_count

# --- STREAMLIT PAGE LAYOUT ---
st.title("Dashboard Overview")
st.markdown("A quick look at your comment statistics.")

total, positive, negative, neutral = get_dashboard_stats()

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total Comments", value=total)
col2.metric(label="Positive Sentiment", value=positive)
col3.metric(label="Negative Sentiment", value=negative)
col4.metric(label="Neutral Sentiment", value=neutral)

st.subheader("Add a New Comment")
with st.form("add_comment_form"):
    comment_text = st.text_area("Comment text:")
    author = st.text_input("Author (optional):")
    submitted = st.form_submit_button("Add Comment")
    
    if submitted:
        # Import the analysis functions from the main app
        from streamlit_app import get_sentiment, get_intent
        
        sentiment_label = get_sentiment(comment_text)
        intent_label = get_intent(comment_text)
        
        with sqlite3.connect('comments.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO comments (comment, sentiment, intent, timestamp, author)
                VALUES (?, ?, ?, ?, ?)
            ''', (comment_text, sentiment_label, intent_label, datetime.datetime.now().isoformat(), author))
            conn.commit()
            st.success(f"Comment added! Sentiment: {sentiment_label}, Intent: {intent_label}")