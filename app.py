from flask import Flask, render_template, request, redirect, url_for
import openai

app = Flask(__name__)

# Set up OpenAI API credentials
openai.api_key = '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'

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
# Define the /signup route to handle GET and POST requests for sign-up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Handle sign-up form submission
        # Extract user input from the form
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Perform validation and database insertion (not implemented in this example)

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

        # Perform validation and authentication (not implemented in this example)

        # Redirect to the index page for now
        return redirect(url_for("index"))

    # If it's a GET request, render the login page
    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)
