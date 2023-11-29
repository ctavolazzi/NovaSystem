# main.py

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy()

with app.app_context():
    db.init_app(app)
    db.create_all()  # Initialize database tables

from models.chat_message import ChatMessage
from models.conversation import Conversation
from services.chat_service import get_last_messages, process_user_message, call_ai_api


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_message = request.form['message']
        process_user_message(user_message)
        return render_template('home.html', messages=get_last_messages())
    last_messages = get_last_messages()
    return render_template('home.html', messages=last_messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()  # This method automatically checks for 'application/json' Content-Type
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid message data'}), 400
    user_message = data['message']
    # Assuming default conversation ID as 1 for now; this should be replaced with actual logic to retrieve the correct ID
    response = process_user_message(user_message, conversation_id=1)
    return jsonify(response)


def process_user_message(user_message, conversation_id):
    ai_response = call_ai_api(user_message)  # This function would call your AI API
    new_message = ChatMessage(user_message=user_message, ai_response=ai_response, conversation_id=conversation_id)
    db.session.add(new_message)
    db.session.commit()
    return {'user_message': user_message, 'ai_response': ai_response, 'conversation_id': conversation_id}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Initialize database tables
    app.run(debug=True)