import base64
import json
import requests

from cloudevents.http import CloudEvent
import functions_framework

from rag import RagPrompt

BOT_URL = "https://us-east1-yonidev.cloudfunctions.net/orders-bot"


class PubSource:
    LIST_GENERATOR: str = "list_generator"


@functions_framework.cloud_event
def subscribe(cloud_event: CloudEvent):
    message_data = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode())

    # Handle message from list generator
    if "source" in message_data and message_data["source"] == PubSource.LIST_GENERATOR:
        pass

    # Handle message from bot
    else:
        rag_service = RagPrompt()
        response_text = rag_service.invoke(message_data["message"])

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'chat_id': message_data["chat_id"],
            'text': f"#from_llm#{response_text}",
            'disable_notification': True
        }

        requests.post(BOT_URL, headers=headers, data=json.dumps(data))
