import os
# Import the 'quote_plus' function to handle special characters in the password
from urllib.parse import quote_plus
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# --- APP CONFIGURATION ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secret@123' 

# --- DATABASE CONFIGURATION ---
DB_USER = 'budgetwise_user'
DB_PASSWORD = 'Secret@1234'
DB_HOST = 'localhost'
DB_NAME = 'budgetwise_db'

# --- THE FIX IS HERE ---
# We use quote_plus to safely encode the password, especially the '@' symbol.
encoded_password = quote_plus(DB_PASSWORD)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}/{DB_NAME}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- LOGIN MANAGER CONFIGURATION ---
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DATABASE MODEL ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    # --- FIX APPLIED HERE: Increased length from 128 to 256 ---
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.gender}')"

# --- ROUTES ---
@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        gender = request.form.get('gender')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user_by_username = User.query.filter_by(username=username).first()
        user_by_email = User.query.filter_by(email=email).first()

        if user_by_username:
            flash('This username is already taken. Please choose another.', 'danger')
            return redirect(url_for('signup'))
        
        if user_by_email:
            flash('This email address is already registered.', 'danger')
            return redirect(url_for('signup'))
            
        if not all([username, email, gender, password, confirm_password]):
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('signup'))

        new_user = User(
            username=username,
            email=email,
            gender=gender,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user)
        next_page = request.args.get('next')
        flash('You have been logged in!', 'success')
        return redirect(next_page) if next_page else redirect(url_for('home'))
        
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/home")
@login_required 
def home():
    return render_template('home.html', title='Home')

if __name__ == '__main__':
    app.run(debug=True)

