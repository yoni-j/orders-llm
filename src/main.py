import base64
import json
import os
import requests

import google.generativeai as genai
from cloudevents.http import CloudEvent
import functions_framework

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro')

BEFORE_LIST_HISTORY = [
    {
        'role': 'user',
        'parts': [
            'הוראות כלליות: '
            'על הודעה עם בקשה לייצר רשימת קניות חדשה תשלח רק את המילה - רשימה.'
            ' בקשה כזאת יכולה להופיע בכל מיני צורות, לדוגמה - '
            'רשימה חדשה, רשימהֿ, הזמנה חדשה, תכין לי רשימה, אני רוצה ללכת לקניות ועוד. '
            'על כל דבר אחר תענה בצורה רגילה']
    },
    {
        'role': 'model',
        'parts': ['אין בעיה'],
    },
]


@functions_framework.cloud_event
def subscribe(cloud_event: CloudEvent):
    message_data = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode())
    chat = model.start_chat(history=BEFORE_LIST_HISTORY)
    resp = chat.send_message(
        content=message_data["message"],
    )
    url = "https://us-east1-yonidev.cloudfunctions.net/orders-bot"

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'chat_id': message_data["chat_id"],
        'text': f"#from_llm#{resp.text}",
        'disable_notification': True
    }

    requests.post(url, headers=headers, data=json.dumps(data))
