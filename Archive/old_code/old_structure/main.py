# main.py
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the 'core' directory to the Python path
core_path = os.path.join(os.path.dirname(__file__), 'core')
sys.path.append(core_path)

# Now import ChatBot
from bots.Bot_01 import ChatBot
import webbrowser
import threading
import asyncio
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Check if the API key is set
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI API key not found. Please check your .env file.")

bot = ChatBot(openai_api_key=api_key)

# Simple HTML template for the chat interface
html_template = '''
<!doctype html>
<html lang="en">
  <head>
    <title>Chat with {{ bot_name }}</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 20px; }
      .chat-container { width: 500px; margin: auto; }
      .message { border: 1px solid #ccc; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
      .user { background-color: #e1f5fe; }
      .bot { background-color: #fff9c4; }
      .model-select { margin-bottom: 10px; }
    </style>
  </head>
  <body>
    <div class="chat-container">
      <h2>Chat with {{ bot_name }}</h2>
      <div class="model-select">
        <form method="post" action="/set_model">
          <label for="model">Select Model:</label>
          <select name="model" id="model">
            <option value="openai" {% if current_model == 'openai' %}selected{% endif %}>OpenAI</option>
            <option value="ollama" {% if current_model == 'ollama' %}selected{% endif %}>Ollama</option>
          </select>
          <input type="submit" value="Set Model">
        </form>
      </div>
      {% for msg in messages %}
        <div class="message {{ msg.role }}">
          <strong>{{ msg.role.capitalize() }}:</strong> {{ msg.content }}
        </div>
      {% endfor %}
      <form method="post">
        <input type="text" name="user_input" autofocus style="width: 80%;" required />
        <input type="submit" value="Send" />
      </form>
    </div>
  </body>
</html>
'''

# Store conversation history
conversation = []

@app.route('/', methods=['GET', 'POST'])
async def chat():
    global conversation
    if request.method == 'POST':
        user_input = request.form['user_input']
        if user_input.strip() != '':
            conversation.append({'role': 'user', 'content': user_input})
            try:
                response = await bot.generate_response(user_input, model=bot.current_model)
            except Exception as e:
                response = f"Error generating response: {e}"
            conversation.append({'role': 'bot', 'content': response})

    return render_template_string(html_template, messages=conversation, bot_name=bot.name, current_model=bot.current_model)

@app.route('/set_model', methods=['POST'])
def set_model():
    model = request.form['model']
    bot.set_model(model)
    return '', 204  # No content response

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Start the browser in a separate thread
    threading.Timer(1, open_browser).start()
    
    print("Starting the chat application...")
    print("The chat interface will open in your default web browser.")
    print("If it doesn't open automatically, please navigate to http://127.0.0.1:5000/ in your browser.")
    
    app.run(debug=False)