# import from external
from flask import Flask, request
from pymessenger.bot import Bot
from bson.objectid import ObjectId
# import from local
from image_api import UserAssert
from db import FbUser
import requests

# ngrok url
# url = ''


API_ROOT = '/'
FB_WEBHOOK = 'webhook'

app = Flask(__name__)
# VERIFY_TOKEN = "YOUR_ACCESS_TOKEN"
# ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

bot = Bot(ACCESS_TOKEN)


@app.route(API_ROOT + "delete/<id>", methods=["GET", "DELETE"])
def delete(id):
    if request.method == "GET":
        delete_result = redirect_delete_url(request.url)

        if delete_result:
            return app.make_response(("Delete Success", 200))

    elif request.method == "DELETE":
        fb_user = FbUser()
        fb_user.delete({"_id": ObjectId(id)}, 'one')
        return app.make_response(("Delete Success", 204))


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
                            send_message(recipient_id, key_to_functions_to_strings("yes"))
                elif message.get("postback"):
                    if message["postback"]["payload"] == "yes":
                        print()
                    elif message["postback"]["payload"] == "no":
                        send_message(recipient_id, key_to_functions_to_strings("no"))
                    elif message["postback"]["payload"] == "picture_show":
                        key_to_functions_to_strings('picture_show', recipient_id)
                    elif message["postback"]["payload"] == "picture_delete_all":
                        key_to_functions_to_strings('picture_delete_all', recipient_id)

        return app.make_response(("post success", 200))
    else:
        return app.make_response(("Method Not Allowed", 405))


def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


def send_attachment(recipient_id, type, attachment_url):
    if type == "image":
        bot.send_image_url(recipient_id, attachment_url)
        # bot.send_button_message(recipient_id, "是否正確?", [{
        #         "type": "postback",
        #         "title": "Yes!",
        #         "payload": "yes"
        #     },
        #     {
        #         "type": "postback",
        #         "title": "No!",
        #         "payload": "no"
        #     }]
        # )


def verify_fb_token(verify_token):
    if verify_token == VERIFY_TOKEN:
        return True
    else:
        return False


def yes():
    return "Save your picture!"


def no():
    return "Oh no! Can you delivery again?"


def show():
    return 'Please press Delete Button to Delete'


def delete_all():
    return 'Delete All Picture!'


def picture_show(*args):
    """

    :param args[0]:recipient_id
    :return:
    """

    recipient_id = args[0][0]
    fb_user = FbUser()
    elements = list()
    cnt = 1
    for data in fb_user.select({"user": recipient_id}):
        obj = dict()
        obj['image_url'] = data['image_url']
        obj['title'] = cnt
        obj['buttons'] = [{"title": "Delete", "type": "web_url", "url": url + "delete/" + str(data['_id']), "webview_height_ratio": "COMPACT"}]
        elements.append(obj)

        if cnt % 10 == 0:
            bot.send_generic_message(recipient_id, elements)
            elements = list()
        cnt += 1
    else:
        bot.send_generic_message(recipient_id, elements)
    send_message(recipient_id, key_to_functions_to_strings("show"))


def picture_delete_all(*args):
    recipient_id = args[0][0]
    fb_user = FbUser()
    fb_user.delete({"user": recipient_id}, 'many')
    send_message(recipient_id, key_to_functions_to_strings("delete_all"))


def key_to_functions_to_strings(argument, *args):
    switcher = {
        'yes': yes,
        'no': no,
        'show': show,
        'delete_all': delete_all,
        'picture_show': picture_show,
        'picture_delete_all': picture_delete_all
    }
    # Get the function from switcher dictionary
    func = switcher.get(argument)
    # Execute the function
    if len(args) == 0:
        return func()
    else:
        return func(args)


def redirect_delete_url(delete_url):
    delete_response = requests.delete(delete_url)
    if delete_response.status_code == 204:
        return True


if __name__ == '__main__':
    app.run()


