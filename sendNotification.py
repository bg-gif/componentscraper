import requests
import json


def send_notification_via_pushbullet(title, body):

    v = open('private.json')
    secrets = json.load(v)

    data_send = {"type": "note", "title": title, "body": body}

    ACCESS_TOKEN = secrets["API_KEY_PB"]
    resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                         headers={'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error sending Notification')
    else:
        print('Notification Sent')
