# app.py
from flask import Flask, request, redirect, url_for, render_template_string
import os

app = Flask(__name__)

SECRET_KEY = "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ12543589890"

@app.route('/')
def home():
    return "Welcome to the insecure Flask app!"

# Insecure endpoint - Bandit and Semgrep should find this
@app.route('/exec')
def exec_command():
    command = request.args.get('cmd')
    if command:
        # Dangerous: allows arbitrary command execution
        output = os.popen(command).read()
        return f"<pre>{output}</pre>"
    return "No command provided."

# Another insecure pattern - potentially vulnerable to XSS
@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')
    # Danger: Reflects user input directly without proper sanitization
    return render_template_string(f"<h1>Hello, {name}!</h1>")

# Login endpoint with intentionally weak validation (for ZAP DAST)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Insecure: Simple hardcoded check, no real authentication
        if username == "admin" and password == "password123":
            return "Login successful! Welcome admin."
        else:
            return "Invalid credentials."
    return '''
        <form method="post">
            <p><input type=text name=username placeholder="Username"></p>
            <p><input type=password name=password placeholder="Password"></p>
            <p><input type=submit value=Login></p>
        </form>
    '''

if __name__ == '__main__':
    # Running in debug mode which can be insecure in production
    app.run(debug=True, host='0.0.0.0', port=5000)