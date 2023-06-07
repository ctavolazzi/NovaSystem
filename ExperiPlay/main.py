from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
import openai
from openai.api_resources.chat_completion import ChatCompletion
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SECRET_KEY'] = 'secret-key'

db = SQLAlchemy(app)
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/dashboard')  # Redirect to dashboard route

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return 'User already exists!'

        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@socketio.on('message')
def handle_message(message):
    # This function will be called whenever a 'message' event is received from a client.
    # You could store the message in a database here, or send the message to all connected clients.
    emit('message', message, broadcast=True)  # This sends the message to all connected clients

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/get_chat_response', methods=['POST'])
def get_chat_response():
    # Assume the message from the client is in the 'message' key of the JSON payload
    message = request.json['message']

    # Generate a response from OpenAI's ChatCompletion
    chat_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": message}
    ]
    response = ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=chat_messages
    )

    # Extract the assistant's reply
    assistant_reply = response['choices'][0]['message']['content']

    # Return the assistant's reply
    return jsonify({"response": assistant_reply})



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the database tables
    socketio.run(app, debug=True)

