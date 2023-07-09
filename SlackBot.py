import os
import threading
from flask import Flask, request, Response
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from env import CHANNELS, BOT_TOKEN, SIGNING_SECRET, DEEPLAKE_USERNAME, DEEPLAKE_DB
from RepoAgent import RepoAgent
import json


class SlackBot:
    def __init__(self, username, db, token, secret):
        self.username = username
        self.agents = {}
        self.load_embeddings()
        #self.agent = RepoAgent(deeplake_username=username, deeplake_db=db)
        self.slack_web_client = WebClient(token=token)
        response = self.slack_web_client.auth_test()
        self.bot_id = response['user_id']
        print("Bot ID: ", self.bot_id)
        self.signature_verifier = SignatureVerifier(secret)
    
    def load_embeddings(self):
        for channel in CHANNELS:
            print("Loading the embeddings for "+CHANNELS[channel]["name"])
            self.agents[channel] = RepoAgent(deeplake_username=self.username, deeplake_db=CHANNELS[channel]["db"])
        print("Embeddings loaded.")

    def post_agent_response(self, channel, text):
        try:
            # Post the markdown answer to the channel where the event was triggered
            print(f"#{channel}: {text}")
            if channel in self.agents:
                response = self.slack_web_client.chat_postMessage(
                    channel=channel,
                    text=self.agents[channel].ask(text)
                )
            else:
                response = self.slack_web_client.chat_postMessage(
                    channel=channel,
                    text="This channel doesn't match any repo, sorry.\nTry the `*-doc` channels"
                )
        except SlackApiError as e:
            print(f"Error: {e}")
        return True

    def handle_ask(self, payload):
        if isinstance(payload, str):
            payload = json.loads(payload)
        user = payload['user_id']
        text = payload['text']
        channel = payload['channel_id']
        try:
            # Post the markdown answer to the channel where the event was triggered
            # response = self.slack_web_client.chat_postMessage(
            #     channel=channel,
            #     text="I'm looking..."
            # )
            # Call the agent in a new thread to avoid timeout
            thread = threading.Thread(target=self.post_agent_response, args=(channel, text))
            thread.start()
        except SlackApiError as e:
            print(f"Error: {e}")
        return Response({'status':'ok'}), 200

    def handle_mention(self, payload, headers):
        if self.signature_verifier.is_valid_request(payload, headers):
            if isinstance(payload, str):
                payload = json.loads(payload)
            # Here's the added part for verification
            if 'challenge' in payload:
                return Response(payload['challenge']), 200
            # Extract the text from the payload
            event = payload.get('event', {})
            print("event", json.dumps(event, indent=4))
            message = event.get('text', "").replace("<@"+self.bot_id+">", "DocBot")
            channel = event.get('channel', {})
            #print("message", json.dumps(message, indent=4))
            thread = threading.Thread(target=self.post_agent_response, args=(channel, message))
            thread.start()
            return Response({'status':'ok'}), 200
        else:
            return Response({'status':'invalid_signature'}), 403


if __name__ == "__main__":
    app = Flask(__name__)
    bot = SlackBot(DEEPLAKE_USERNAME, DEEPLAKE_DB, BOT_TOKEN, SIGNING_SECRET)

    @app.route('/ask', methods=['POST'])
    def ask():
        print("@ask Headers: ", request.headers)
        if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
            payload = request.form
        else:
            payload = request.get_data().decode("utf-8")
        print("Payload: ", json.dumps(payload, indent=4))
        return bot.handle_ask(payload)

    @app.route('/mention', methods=['POST'])
    def mention():
        print("@mention Headers: ", request.headers)
        if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
            payload = request.form
        else:
            payload = request.get_data().decode("utf-8")
        return bot.handle_mention(payload, request.headers)

    app.run(port=3000)
