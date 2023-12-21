from flask import Flask, render_template, request
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
    # Get the message and device type from the POST request
    user_message = request.json.get("message")
    device_type = request.json.get("device_type")

    # Generate a prompt based on the user's input and selected device type
    prompt = f"Create a user interface suitable for the elderly for a {user_message} app on {device_type}."

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

if __name__ == '__main__':
    app.run()
