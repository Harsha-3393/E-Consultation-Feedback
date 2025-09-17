import streamlit as st
import pandas as pd
from transformers import pipeline
import re

@st.cache_resource
def load_sentiment_classifier():
    return pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

sentiment_classifier = load_sentiment_classifier()

def get_intent(text):
    text = text.lower()
    if any(keyword in text for keyword in ["return", "replace", "refund", "wapas"]):
        return "Return/Refund"
    elif any(keyword in text for keyword in ["when", "where", "how", "track", "kab", "kaha"]):
        return "Query/Tracking"
    elif any(keyword in text for keyword in ["good", "bad", "happy", "love", "achha", "badiya"]):
        return "Feedback"
    else:
        return "Other"

def get_sentiment(text):
    sentiment_result = sentiment_classifier(text)[0]
    model_output_label = sentiment_result['label']

    if model_output_label == '5 stars':
        return 'Strongly Positive'
    elif model_output_label == '4 stars':
        return 'Positive'
    elif model_output_label == '3 stars':
        return 'Neutral'
    elif model_output_label == '2 stars':
        return 'Negative'
    elif model_output_label == '1 star':
        return 'Strongly Negative'
    else:
        return 'Unknown'

st.title("E-Consultation Sentiment Analyzer")
st.markdown("Analyze the sentiment and intent of comments in Indian languages.")

comment_text = st.text_area("Enter your comment here:", height=100, placeholder="E.g., Yeh product bahut achha hai!")

if st.button("Analyze Comment"):
    if comment_text:
        sentiment_label = get_sentiment(comment_text)
        intent_label = get_intent(comment_text)

        st.subheader("Analysis Results")
        st.write(f"**Comment:** {comment_text}")
        st.write(f"**Sentiment:** {sentiment_label}")
        st.write(f"**Intent:** {intent_label}")
    else:
        st.error("Please enter a comment to analyze.")

