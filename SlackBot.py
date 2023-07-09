import os
import threading
from flask import Flask, request, Response
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from env import BOT_TOKEN, SIGNING_SECRET, DEEPLAKE_USERNAME, DEEPLAKE_DB
from RepoAgent import RepoAgent
import json

# Init the agent
agent = RepoAgent(deeplake_username=DEEPLAKE_USERNAME, deeplake_db=DEEPLAKE_DB)

# Instantiate Flask 
app = Flask(__name__)

# Initialize a Web API client
slack_web_client = WebClient(token=BOT_TOKEN)
response = slack_web_client.auth_test()
bot_id = response['user_id']

print("Bot ID: ", bot_id)

# Initialize signature verifier
signature_verifier = SignatureVerifier(SIGNING_SECRET)

def post_agent_response(channel, text):
    try:
        # Post the markdown answer to the channel where the event was triggered
        response = slack_web_client.chat_postMessage(
            channel=channel,
            text=agent.ask(text)
        )
        print("chat_postMessage", response)
    except SlackApiError as e:
        print(f"Error: {e}")


@app.route('/ask', methods=['POST'])
def handle_ask():
    print("@ask Headers: ", request.headers)
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
        payload = request.form
    else:
        payload = request.get_data().decode("utf-8")
    print("Payload: ", json.dumps(payload, indent=4))
    user = payload['user_id']
    text = payload['text']
    channel = payload['channel_id']
    try:
        # Post the markdown answer to the channel where the event was triggered
        response = slack_web_client.chat_postMessage(
            channel=channel,
            text="I'm looking..."
        )
        print("chat_postMessage", response)
        # Call the agent in a new thread to avoid timeout
        thread = threading.Thread(target=post_agent_response, args=(channel, text))
        thread.start()
    except SlackApiError as e:
        print(f"Error: {e}")
    return Response(), 200


@app.route('/mention', methods=['POST'])
def handle_mention():
    print("@mention Headers: ", request.headers)
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
        payload = request.form
    else:
        payload = request.get_data().decode("utf-8")
    
    if signature_verifier.is_valid_request(payload, request.headers):
        # Extract the data from the payload
        data = request.json
        print("data", json.dumps(data, indent=4))
        # Here's the added part for verification
        if 'challenge' in data:
            return Response(data['challenge']), 200

        # Extract the text from the payload
        event = data.get('event', {})
        print("event", json.dumps(event, indent=4))

        message = event.get('text', "").replace("<@"+bot_id+">", "DocBot")
        channel = event.get('channel', {})
        print("message", json.dumps(message, indent=4))
       
        thread = threading.Thread(target=post_agent_response, args=(channel, message))
        thread.start()
        return Response(), 200
    else:
        return Response(), 403


if __name__ == "__main__":
    app.run(port=3000)