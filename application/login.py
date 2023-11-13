from flask_login import LoginManager, login_user, logout_user, login_required
from flask import request, current_app as app, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash , check_password_hash
from .models import User, db, Language

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_get"

@login_manager.user_loader
def load_user(user_id):
    return User.query.where(User.id == int(user_id)).first()

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter(User.username == username).first()

    empty = [None, '']

    if username in empty or password in empty:
        flash('Invalid Inputs')
        return redirect('/signup')

    if user != None:
        if check_password_hash( user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Incorrect Password')
            return redirect('/login')
    else:
        flash('Username not found. Signup!')
        return redirect('/login')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    language = request.form.get('language')

    empty = [None, '']

    if email in empty or username in empty or password in empty or name in empty or language in empty:
        flash('Invalid Inputs')
        return redirect('/signup')
    
    user = User.query.where(User.username == username).first()

    if user:
        flash('User already exists login!')
        return redirect('/login')
    else:
        user = User(username = username, password = generate_password_hash(password), email = email, name = name, language=language)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))

@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login/login.html')

@app.route('/signup', methods=['GET'])
def signup_get():
    languages = Language.query.all()
    return render_template('login/signup.html', languages= languages)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect('/signup')