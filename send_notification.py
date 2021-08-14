import os
import requests
import json


def send_notification_via_pushbullet(title, body):

    data_send = {"type": "note", "title": title, "body": body}
    access_token = os.getenv("API_KEY_PB")
    resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                         headers={'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error sending Notification')
    else:
        print('Notification Sent')
