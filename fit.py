from flask import Flask, render_template, request, jsonify
import google.generativeai as ai
import sqlite3
import time

app = Flask(__name__)

API_KEY = 'AIzaSyCIgHspeOtytvBf0_ohZZdt43DUqNJBf2Q'
ai.configure(api_key=API_KEY)

model = ai.GenerativeModel("gemini-pro")
chat = model.start_chat()

predefined_responses = {
    "who are you": "I am Fitness Tech-AI, your personal fitness assistant, developed by denQueue 😊",
    "who are you?": "I am Fitness Tech-AI, your personal fitness assistant, developed by denQueue 😊",
    "what is your name": "I am Fitness Tech-AI, your personal fitness assistant, developed by denQueue 😊",
    "what is your name?": "I am Fitness Tech-AI, your personal fitness assistant, developed by denQueue 😊",
    "hello": "Hi! How can I assist you today? 👋",
    "bye": "Goodbye! Have a great day! 👋",
    "❤️": "Love is in the air! 😊",
    "who created you?": "I was created by denQueue.",
    "who developed you?": "I was developed by denQueue.",
    "give me a fitness tip": "Remember to stay hydrated and warm up before your workout! 💪",
    "motivate me": "You're doing amazing! Keep pushing your limits! 💪🔥",
    "who made you": "I was made by denQueue.",
    "calculate bmi": "Please provide your weight (kg) and height (cm) to calculate BMI.",
}

def get_db_connection():
    conn = sqlite3.connect('interactions.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            response_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

create_table()

def handle_message(message):
    normalized_message = message.strip().lower()
    if normalized_message in predefined_responses:
        return predefined_responses[normalized_message]
    return None

@app.route('/')
def home():
    return render_template('good.html')

@app.route('/chat', methods=['POST'])
def chat_response():
    user_message = request.form['message']
    predefined_response = handle_message(user_message)
    if predefined_response:
        response_text = predefined_response
    elif user_message.lower().startswith('bmi '):
        try:
            weight, height = map(float, user_message[4:].split())
            bmi = weight / (height / 100) ** 2
            response_text = f"Your BMI is {bmi:.2f}. A healthy BMI is typically between 18.5 and 24.9."
        except ValueError:
            response_text = "Please provide your weight (kg) and height (cm) separated by a space. Example: 'BMI 70 175'"
    else:
        response_text = send_message_with_retry(chat, user_message)

    response_chunks = [response_text[i:i+500] for i in range(0, len(response_text), 500)]
    save_interaction(user_message, response_text)
    return jsonify(response=response_text)

def save_interaction(user_message, response_text):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO interactions (user_message, response_text)
        VALUES (?, ?)
    ''', (user_message, response_text))
    conn.commit()
    conn.close()

def send_message_with_retry(chat, user_message, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = chat.send_message(user_message)
            if any(word in response.text.lower() for word in ["gemini", "google"]):
                response.text = "I am Fitness Tech-AI, your personal fitness assistant, developed by denQueue 😊"
            return response.text
        except ai.errors.ApiError as api_err:
            app.logger.error(f"API Error on attempt {attempt + 1}: {api_err}")
            time.sleep(delay)
        except Exception as e:
            app.logger.error(f"General Error on attempt {attempt + 1}: {e}")
            time.sleep(delay)
    return "Sorry, something went wrong. Please try again."

@app.route('/chat-history')
def chat_history():
    conn = get_db_connection()
    interactions = conn.execute('SELECT id, user_message, timestamp FROM interactions ORDER BY timestamp DESC').fetchall()
    conn.close()
    history = [{"id": row["id"], "title": row["user_message"][:30], "timestamp": row["timestamp"]} for row in interactions]
    return jsonify(history=history)

@app.route('/chat/<int:chat_id>')
def get_chat(chat_id):
    conn = get_db_connection()
    interaction = conn.execute('SELECT user_message, response_text FROM interactions WHERE id = ?', (chat_id,)).fetchall()
    conn.close()
    messages = [{"text": row["user_message"], "sender": "user"} for row in interaction]
    messages += [{"text": row["response_text"], "sender": "bot"} for row in interaction]
    return jsonify(messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
