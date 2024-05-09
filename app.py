from flask import Flask, render_template, request, redirect, session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to create a database connection
def get_db_connection():
    conn = sqlite3.connect('syst.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create tables if they don't exist
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            userid INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to register a new user
def register_user(name, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    conn.close()

# Function to check if a user exists and return its details
def get_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        user = get_user(email, password)
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return render_template('user.html', message=message)
        else:
            message = 'Please enter correct email/password!'
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('name', None)
    session.pop('email', None)
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not name or not password or not email:
            message = 'Please fill out the form!'
        else:
            register_user(name, email, password)
            message = 'You have successfully registered!'
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    return render_template('register.html', message=message)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
