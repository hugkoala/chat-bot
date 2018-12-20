from flask import Flask, request
from pymessenger.bot import Bot
from image_api import UserAssert
from os import listdir




API_ROOT = '/'
FB_WEBHOOK = 'webhook'

app = Flask(__name__)
VERIFY_TOKEN = "YOUR_ACCESS_TOKEN"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
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
                    # if message["message"].get("text"):
                    #     response_sent_text = get_message()
                    #     send_message(recipient_id, response_sent_text)
                    if message["message"].get("attachments"):
                        attachments = message["message"]["attachments"]
                        for attachment in attachments:
                            # send_attachment(recipient_id, attachment["type"], attachment["payload"]["url"])
                            user_assert.download_picture(attachment["payload"]["url"])
                            send_message(recipient_id, "Download Your Picture to your folder")

                elif message.get("postback"):

                    if message["postback"]["payload"] == "yes":
                        send_message(recipient_id, key_to_functions_to_strings("yes"))
                    elif message["postback"]["payload"] == "no":
                        send_message(recipient_id, key_to_functions_to_strings("no"))
                    elif message["postback"]["payload"] == "picture_show":
                        key_to_functions_to_strings('picture_show', recipient_id)

        return app.make_response(("post success", 200))
    else:
        return app.make_response(("Method Not Allowed", 405))


# def get_message():
#     sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
#     # return selected item to the user
#     return random.choice(sample_responses)


def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


def send_attachment(recipient_id, type, attachment_url):
    if type == "image":
        bot.send_image_url(recipient_id, attachment_url)
        # obj = []
        # yes = dict(); yes['type'] = 'postback'; yes['title'] = 'Yes!'; yes['payload'] = 'yes'
        # no = dict(); no['type'] = 'postback'; no['title'] = 'No!'; no['payload'] = 'no'
        # obj.append(yes); obj.append(no)
        # bot.send_button_message(recipient_id, "是否正確?", json.dumps(obj))
        bot.send_button_message(recipient_id, "是否正確?", [{
                "type": "postback",
                "title": "Yes!",
                "payload": "yes"
            },
            {
                "type": "postback",
                "title": "No!",
                "payload": "no"
            }]
        )


def verify_fb_token(verify_token):
    if verify_token == VERIFY_TOKEN:
        return True
    else:
        return False


def yes():
    return "Thanks so much!"


def no():
    return "Oh no! Can you delivery again?"


def picture_show(*args):
    """

    :param args[0]:recipient_id
    :return:
    """

    recipient_id = args[0][0]
    userAssert = UserAssert(recipient_id)
    # bot.send_image(recipient_id, userAssert.get_folder_path())
    allUserFiles = listdir(userAssert.get_folder_path())

    for userFile in allUserFiles:
        userFileUrl = userAssert.get_folder_path() + '/' + userFile
        print(userFileUrl)
        bot.send_image(recipient_id, userFileUrl)



def key_to_functions_to_strings(argument, *args):
    switcher = {
        'yes': yes,
        'no': no,
        'picture_show': picture_show
    }
    # Get the function from switcher dictionary
    func = switcher.get(argument)
    # Execute the function
    if len(args) == 0:
        return func()
    else:
        return func(args)


if __name__ == '__main__':
    # context = ('ssl/fullchain.pem', 'ssl/privkey.pem')
    # app.run(host='0.0.0.0', debug=True, ssl_context=context)
    app.run()


