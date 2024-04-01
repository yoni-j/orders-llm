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
            'הוראות כלליות: על כל הודעה שנשמעת כמו בקשה לרשימת קניות חדשה תחזיר כתשובה רק את הטקסט: ״#רשימה#״. דוגמאות להודעות: ״רשימה חדשה״, ״הזמנה״, ״הזמנה חדשה״, ״רשימת קניות״, ״תכין לי רשימה״, ״אני הולך לסופר, מה לקנות?״ ועוד. על כל הודעה אחרת תענה בצורה רגילה']
    },
    {
        'role': 'model',
        'parts': ['okay']
    }
]


@functions_framework.cloud_event
def subscribe(cloud_event: CloudEvent):
    message_data = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode())
    chat_messages = BEFORE_LIST_HISTORY.copy()
    chat_messages.append(
        {'role': 'user',
         'parts': [message_data["message"]]}
    )
    resp = model.generate_content(chat_messages)
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
