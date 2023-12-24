from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import openai

app = Flask(__name__)

# Replace 'your_username', 'your_password', and 'your_database_name' with your actual MySQL credentials
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/alisa_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create a SQLAlchemy instance
db = SQLAlchemy(app)

# Define the User model
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
    # Get the message, device type, and style from the POST request
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
        # Handle sign-up form submission
        # Extract user input from the form
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Create a new user and add it to the database
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the index page for now
        return redirect(url_for("index"))

    # If it's a GET request, render the sign-up page
    return render_template("signup.html")

# Define the /login route to handle GET and POST requests for login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Handle login form submission
        # Extract user input from the form
        username = request.form.get("username")
        password = request.form.get("password")

        # Perform authentication (check username and password against the database)
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # Authentication successful, redirect to the index page
            return redirect(url_for("index"))
        else:
            # Authentication failed, render the login page with an error message
            return render_template("login.html", error="Invalid username or password")

    # If it's a GET request, render the login page
    return render_template("login.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
