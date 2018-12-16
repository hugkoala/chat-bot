from flask import Flask, request
from pymessenger.bot import Bot
from image_api import UserAssert
import random


API_ROOT = '/'
FB_WEBHOOK = 'webhook'

app = Flask(__name__)
# VERIFY_TOKEN = "YOUR_ACCESS_TOKEN"
# ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
VERIFY_TOKEN = "EAAC8LmJKbe0BAHbY2lmlXSa01hZAyZCGZBp0rfWbvc9GpOrlHJQB1xCOwMca41VlQa8K1o9paIrmdZAgFBMWLQTe95cUjZBvwHov5rTRXLoUmOTr7O2Qr1HdaE9VsHFCihpxZCDBz6IUCh47DiLMZCPL2S1zZATHpGs32JxVdSsMIDxb7jv6ayuZA"
ACCESS_TOKEN = "EAAC8LmJKbe0BAHbY2lmlXSa01hZAyZCGZBp0rfWbvc9GpOrlHJQB1xCOwMca41VlQa8K1o9paIrmdZAgFBMWLQTe95cUjZBvwHov5rTRXLoUmOTr7O2Qr1HdaE9VsHFCihpxZCDBz6IUCh47DiLMZCPL2S1zZATHpGs32JxVdSsMIDxb7jv6ayuZA"
bot = Bot(ACCESS_TOKEN)


@app.route(API_ROOT + FB_WEBHOOK, methods=["GET", "POST"])
def fb_receive_message():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        if verify_fb_token(verify_token):
            return request.args.get("hub.challenge")
        else:
            return app.make_response(("Invalid verification token", 403))
    elif request.method == "POST":
        inputJson = request.get_json()
        print(inputJson)
        for event in inputJson["entry"]:
            messaging = event["messaging"]
            for message in messaging:
                recipient_id = message["sender"]["id"]
                user_assert = UserAssert(recipient_id)
                if message.get("message"):
                    if message["message"].get("text"):
                        response_sent_text = get_message()
                        send_message(recipient_id, response_sent_text)
                    if message["message"].get("attachments"):
                        attachments = message["message"]["attachments"]
                        for attachment in attachments:
                            send_attachment(recipient_id, attachment["type"], attachment["payload"]["url"])
                            user_assert.download_picture(attachment["payload"]["url"])
                            send_message(recipient_id, "Download Your Picture to your folder")

                elif message.get("postback"):

                    if message["postback"]["payload"] == "yes":
                        send_message(recipient_id, "Thanks so much!")
                    else:
                        send_message(recipient_id, "Oh no! Can you delivery again?")

        return app.make_response(("post success", 200))
    else:
        return app.make_response(("Method Not Allowed", 405))


def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)


def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


def send_attachment(recipient_id, type, attachment_url):
    if type == "image":
        bot.send_image_url(recipient_id, attachment_url)
        bot.send_button_message(recipient_id, "是否正確?", [{
                "type": "postback",
                "title": "Yes!",
                "payload": "yes",
              },
              {
                "type": "postback",
                "title": "No!",
                "payload": "no",
              }])


def verify_fb_token(verify_token):
    if verify_token == VERIFY_TOKEN:
        return True
    else:
        return False


if __name__ == '__main__':
    # context = ('ssl/fullchain.pem', 'ssl/privkey.pem')
    # app.run(host='0.0.0.0', debug=True, ssl_context=context)
    app.run()

