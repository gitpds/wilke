import os
import time
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
from google.cloud import secretmanager
from dotenv import load_dotenv

# Function to access secrets from Google Secret Manager
def access_secret_version(secret_id):
    project_id = os.getenv('GCP_PROJECT_ID')  # Set this as an environment variable
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Load environment variables and OpenAI API key
load_dotenv()
openai.api_key = access_secret_version("OPENAI_API_KEY")

# Fetch thread_id and assistant_id from Secret Manager
thread_id = access_secret_version("WILKE_THREAD")
assistant_id = access_secret_version("WILKE_ID")

# Initialize the Flask application
app = Flask(__name__)

# Define the route to receive SMS messages
@app.route("/sms", methods=['POST'])
def receive_sms():
    # Extract message content from the SMS
    body = request.form['Body']
    message = body.strip()

    # Process the incoming message with OpenAI
    response_text = send_message_to_assistant(thread_id, assistant_id, message)

    # Create a Twilio MessagingResponse and send the response back
    twilio_response = MessagingResponse()
    twilio_response.message(response_text)
    return str(twilio_response)

def send_message_to_assistant(thread_id, assistant_id, message, wait_time=5):
    # Function to interact with OpenAI
    client = openai.Client()
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    time.sleep(wait_time)
    messages = client.beta.threads.messages.list(thread_id)
    for msg in reversed(messages.data):
        if msg.role == 'assistant':
            return msg.content[0].text.value
    return "No response from the assistant."

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
