from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_dance.contrib.google import make_google_blueprint, google
from datetime import datetime
from flask import redirect

import openai

app = Flask(__name__)
app.secret_key = 'alisa'  # Change this to a secret key for session management

# Set up OpenAI API credentials
openai.api_key = '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'

# Configure SQLAlchemy, Bcrypt, and Flask-Dance
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/alisa_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GOOGLE_OAUTH_CLIENT_ID'] = '680127095298-t8c4s4f2auaar62lnglmjr26gs32re1k.apps.googleusercontent.com'
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = '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'
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this to a strong secret key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Flask-Dance Google Blueprint
google_bp = make_google_blueprint()
app.register_blueprint(google_bp, url_prefix='/google_login')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    signup_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_timestamp = db.Column(db.DateTime)

# Define the default route to return the index.html file
@app.route("/")
def index():
    return render_template("index.html")

# Define the /api route to handle POST requests
@app.route("/api", methods=["POST"])
def api():
    user_message = request.json.get("message")
    device_type = request.json.get("device_type")
    selected_style = request.json.get("style")

    # Generate a prompt based on the user's input, selected device type, and style
    prompt = f"Create a {selected_style} user interface suitable for the elderly for a {user_message} app on {device_type}."

    # Send the modified message to OpenAI's API and receive the response
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    if 'choices' in completion and completion['choices']:
        return {"content": completion['choices'][0]['message']['content']}
    else:
        return {'content': 'Failed to generate response!'}

# Define the /signup route to handle GET and POST requests for sign-up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        password = request.form.get("password")

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(name=name, lastname=lastname, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for("index"))

    return render_template("signup.html")

# Define the /login route to handle GET and POST requests for login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # Log in the user and store user data in the session
            session['user_id'] = user.id
            session['email'] = user.email

            # Update last login timestamp
            user.last_login_timestamp = datetime.utcnow()
            db.session.commit()

            flash('Login successful!', 'success')
            return redirect(url_for("index"))
        else:
            flash('Invalid email or password', 'danger')

    return render_template("login.html")

# Define the /logout route to handle user logout
@app.route("/logout")
def logout():
    # Clear the session data to log out the user
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for("index"))

# Google login route
@app.route('/google_login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    google_data = resp.json()
    
    # Check if the user with this email already exists in your database
    user = User.query.filter_by(email=google_data['emails'][0]['value']).first()
    
    if not user:
        # If the user doesn't exist, create a new user using Google data
        new_user = User(
            name=google_data['displayName'],
            email=google_data['emails'][0]['value'],
            # You might want to generate a random password for the user
            password=bcrypt.generate_password_hash('some_random_password').decode('utf-8')
        )
        db.session.add(new_user)
        db.session.commit()

    # Log in the user and store user data in the session
    session['user_id'] = user.id
    session['email'] = user.email

    # Update last login timestamp
    user.last_login_timestamp = datetime.utcnow()
    db.session.commit()

    flash('Login successful!', 'success')
    return redirect(url_for("index"))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
