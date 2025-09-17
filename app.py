from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import sqlite3
import datetime
import io
import re
import xlsxwriter

from transformers import pipeline

# --- ONE-TIME SETUP ---
print("Loading sentiment analysis model...")
try:
    sentiment_classifier = pipeline(
        "sentiment-analysis", 
        model="nlptown/bert-base-multilingual-uncased-sentiment"
    )
    print("Sentiment model loaded successfully.")
    
    data = pd.read_csv('preprocessed_ecom_data.csv')
    print("Preprocessed data loaded.")

except Exception as e:
    print(f"Error loading models or data: {e}")
    exit()

# --- DATABASE SETUP ---
DATABASE = 'comments.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                comment TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                intent TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                author TEXT
            )
        ''')
        conn.commit()

init_db()

app = Flask(__name__)

# --- FUNCTIONS FOR ANALYSIS & DATABASE INTERACTION ---
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

def get_dashboard_stats():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        total = cursor.execute('SELECT COUNT(*) FROM comments').fetchone()[0]
        pos_count = cursor.execute("SELECT COUNT(*) FROM comments WHERE sentiment LIKE '%Positive%'").fetchone()[0]
        neg_count = cursor.execute("SELECT COUNT(*) FROM comments WHERE sentiment LIKE '%Negative%'").fetchone()[0]
        neu_count = cursor.execute("SELECT COUNT(*) FROM comments WHERE sentiment = 'Neutral'").fetchone()[0]
    return total, pos_count, neg_count, neu_count

# --- DEFINE THE WEB ROUTES ---
@app.route('/')
@app.route('/dashboard')
def dashboard():
    total, pos_count, neg_count, neu_count = get_dashboard_stats()
    return render_template('dashboard.html',
                           total=total,
                           positive=pos_count,
                           negative=neg_count,
                           neutral=neu_count)

@app.route('/comments_view')
def comments_view():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        comments_data = cursor.execute('SELECT comment, sentiment, intent, timestamp, author FROM comments ORDER BY timestamp DESC').fetchall()
    
    comments_with_scores = []
    for comment_row in comments_data:
        comment_text = comment_row[0]
        sentiment_result = sentiment_classifier(comment_text)[0]
        score = f"{sentiment_result['score']:.2f}"
        
        comments_with_scores.append(comment_row + (score,))
        
    return render_template('comments_view.html', comments=comments_with_scores)

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/api/analytics_data')
def api_analytics_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        sentiment_counts = cursor.execute('SELECT sentiment, COUNT(*) FROM comments GROUP BY sentiment').fetchall()
        intent_counts = cursor.execute('SELECT intent, COUNT(*) FROM comments GROUP BY intent').fetchall()
    
    sentiment_data = {sentiment: count for sentiment, count in sentiment_counts}
    intent_data = {intent: count for intent, count in intent_counts}
    
    return jsonify({
        'sentiment_data': sentiment_data,
        'intent_data': intent_data
    })


@app.route('/add_comment', methods=['POST'])
def add_comment():
    try:
        comment_text = request.form.get('comment_text')
        author = request.form.get('author')

        if not comment_text:
            return jsonify({'status': 'error', 'message': 'Comment cannot be empty.'}), 400

        sentiment_label = get_sentiment(comment_text)
        intent_label = get_intent(comment_text)

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO comments (comment, sentiment, intent, timestamp, author)
                VALUES (?, ?, ?, ?, ?)
            ''', (comment_text, sentiment_label, intent_label, datetime.datetime.now().isoformat(), author))
            conn.commit()

        total, pos_count, neg_count, neu_count = get_dashboard_stats()
        return jsonify({
            'status': 'success',
            'sentiment': sentiment_label,
            'intent': intent_label,
            'stats': {
                'total': total,
                'positive': pos_count,
                'negative': neg_count,
                'neutral': neu_count
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/analyze_all', methods=['POST'])
def analyze_all():
    try:
        data_to_analyze = pd.read_csv('preprocessed_ecom_data.csv')
        comments = data_to_analyze.to_dict('records')

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            for row in comments:
                comment_text = row['review_text']
                sentiment_label = get_sentiment(comment_text)
                intent_label = get_intent(comment_text)
                author = row.get('user_id', 'N/A')
                cursor.execute('''
                    INSERT INTO comments (comment, sentiment, intent, timestamp, author)
                    VALUES (?, ?, ?, ?, ?)
                ''', (comment_text, sentiment_label, intent_label, datetime.datetime.now().isoformat(), author))
            conn.commit()

        total, pos_count, neg_count, neu_count = get_dashboard_stats()
        return jsonify({
            'status': 'success',
            'message': 'All comments analyzed and saved.',
            'stats': {
                'total': total,
                'positive': pos_count,
                'negative': neg_count,
                'neutral': neu_count
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/clear_comments', methods=['POST'])
def clear_comments():
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM comments')
            conn.commit()
        return jsonify({'status': 'success', 'message': 'All comments have been cleared.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/download_excel')
def download_excel():
    try:
        clear_data = request.args.get('clear', 'false').lower() == 'true'
        
        with sqlite3.connect(DATABASE) as conn:
            df = pd.read_sql_query("SELECT comment, sentiment, intent, timestamp, author FROM comments", conn)

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Comments', index=False)
        writer.close()
        output.seek(0)

        if clear_data:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM comments')
                conn.commit()

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='E-Consultation_Feedback.xlsx'
        )

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)