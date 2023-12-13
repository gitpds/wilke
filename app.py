import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import time
from dotenv import load_dotenv


# Load environment variables and OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the Flask application
app = Flask(__name__)

# Define the route to receive SMS messages
@app.route("/sms", methods=['POST'])
def receive_sms():
    # Extract message content, thread_id, and assistant_id from the SMS
    body = request.form['Body']
    try:
        parts = body.split(',')
        thread_id = parts[0].split(':')[1].strip()
        assistant_id = parts[1].split(':')[1].strip()
        message = ','.join(parts[2:]).strip()
    except IndexError:
        return "Incorrect message format. Please use 'thread_id:xxx,assistant_id:yyy,Your message'."

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
