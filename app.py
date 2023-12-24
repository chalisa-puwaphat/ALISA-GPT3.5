from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import openai

app = Flask(__name__)
app.secret_key = 'alisa'  # Change this to a secret key for session management

# Set up OpenAI API credentials
openai.api_key = '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'

# Configure SQLAlchemy and Bcrypt
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/alisa_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

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
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for("login"))

    return render_template("signup.html")

# Define the /login route to handle GET and POST requests for login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # Log in the user and store user data in the session
            session['user_id'] = user.id
            session['username'] = user.username

            flash('Login successful!', 'success')
            return redirect(url_for("index"))
        else:
            flash('Invalid username or password', 'danger')

    return render_template("login.html")

# Define the /logout route to handle user logout
@app.route("/logout")
def logout():
    # Clear the session data to log out the user
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for("index"))

if __name__ == '__main__':
    # Create the database tables before running the app
    with app.app_context():
        db.create_all()
    app.run(debug=True)
