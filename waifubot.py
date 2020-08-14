# Python Libraries
import os
import json
import requests

# External Libraries
from flask import Flask, request
from pymessenger.bot import Bot

# IO helper
def get_dir(dir):
	curr_dir = os.path.dirname(__file__)
	return os.path.join(curr_dir, dir)

# Initialization
app = Flask(__name__)

with open(get_dir("config.json")) as auth_file:
	auth = json.load(auth_file)
	
ACCESS_TOKEN = auth['ACCESS_TOKEN']
VERIFY_TOKEN = auth['VERIFY_TOKEN']
DEEPAI_APIKEY = auth['DEEPAI_APIKEY']

bot = WaifuBot(ACCESS_TOKEN)
bot.initialize()

# Bot Class Derivative
class WaifuBot(Bot):
	def initialize(self):
		with open(get_dir('strings.json')) as f:
			self.strings = json.load(f)

	def on_message(self, recipient_id=None, message_string=None):
		strings = self.strings
		self.send_text_message(recipient_id, strings['greetings'])

	def on_send_photo(self, recipient_id=None, image_url=None):
		r = requests.post(
		    "https://api.deepai.org/api/waifu2x",
		    data={
		    	'image':image_url,
		    },
		    headers={'api-key': DEEPAI_APIKEY}
		)
		print(r.json())
		self.send_image_url(recipient_id, r.json()['output_url'])
		self.send_text_message(recipient_id, self.strings['processed'])

# Listener base code of the bot
@app.route("/getpost", methods=['GET', 'POST'])
def receive_message():
	if request.method == 'GET':
		token_sent = request.args.get("hub.verify_token")
		return verify_fb_token(token_sent)
	elif request.method == 'POST':
		output = request.get_json()
		print(f"{output}")
		for event in output['entry']:
			messaging = event['messaging']
			for message in messaging:
				recip = message['sender']['id']
				message_object = message['message']
				if message_object.get('text'):
					bot.on_message(recip, message_string=message['message']['text'])
				if message_object.get('attachments'):
					attachments = message_object.get('attachments')
					for attachment in attachments:
						if attachment.get('type') == 'image':
							bot.on_send_photo(recip, attachment.get('payload')['url'])
	return "Message Processed"

# Token verifier
def verify_fb_token(token_sent):
	if token_sent == VERIFY_TOKEN:
		return request.args.get("hub.challenge")
	return 'Invalid verification token'

if __name__ == "__main__":
	app.run()
