import base64
import os

import google.generativeai as genai
from cloudevents.http import CloudEvent
import functions_framework

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyD4ShYWIkPoNmco52c5IiaVTSXrLQCsoCk')
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro')


@functions_framework.cloud_event
def handler(cloud_event: CloudEvent):
    print(
        "Hello, " + base64.b64decode(cloud_event.data["message"]["data"]).decode() + "!"
    )

