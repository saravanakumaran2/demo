from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

BACKEND_URL = os.getenv("BACKEND_URL")


@app.route('/')
def home():
    return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = ""
    if request.method == 'POST':
        res = requests.post(f"{BACKEND_URL}/login", json=request.form)
        if res.status_code == 200:
            username = request.form['username']
            session['username'] = username
            return redirect(url_for('main'))
        else:
            try:
                error_msg = res.json().get('error', "Login Failed! Please check your credentials.")
            except:
                error_msg = "Login Failed! Please check your credentials."
    return render_template("login.html", error_msg=error_msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_msg = ""
    if request.method == 'POST':
        res = requests.post(f"{BACKEND_URL}/register", json=request.form)
        if res.status_code == 201:
            return redirect('/login')
        else:
            try:
                error_msg = res.json().get('error', "Register Failed! Check username and password rules.")
            except:
                error_msg = "Register Failed! Check username and password rules."
    return render_template("register.html", error_msg=error_msg)

@app.route('/main')
def main():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    return render_template("main.html", username=username)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    requests.post(f"{BACKEND_URL}/logout")
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
