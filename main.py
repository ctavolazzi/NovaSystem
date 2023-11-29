# main.py

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        # Process the data, save it, send an email, etc.
        return f"Thank you, {name}. We received your message!"
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
