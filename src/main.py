import base64
import json
import requests

from cloudevents.http import CloudEvent
import functions_framework

from rag import RagPrompt
from data_service import DataService
from prediction import create_recommedation
from enums import PubSource, PrefixSuffixEnum

BOT_URL = "https://us-east1-yonidev.cloudfunctions.net/orders-bot"


@functions_framework.cloud_event
def subscribe(cloud_event: CloudEvent):
    message_data = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode())
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'chat_id': message_data["chat_id"],
        'disable_notification': True
    }
    # Handle message from list generator
    if "source" in message_data and message_data["source"] == PubSource.LIST_GENERATOR:
        data["text"], history = handle_message_from_list_generator(message_data)

    # Handle message from bot
    else:
        data["text"], history = handle_message_from_bot(message_data)

    resp = requests.post(BOT_URL, headers=headers, data=json.dumps(data))
    if resp.status_code == 200:
        DataService.update_data(message_data["chat_id"], history)


def handle_message_from_bot(message_data):
    history = json.loads(get_history(message_data["chat_id"]))
    before_list = get_list(str(message_data["chat_id"])) == '[]'
    history = DataService.format_history(history)
    rag_service = RagPrompt(chat_id=message_data["chat_id"], history=history, before_list=before_list)
    response_text, history = rag_service.invoke(message_data["message"])
    return f"{PrefixSuffixEnum.FROM_LLM_MESSAGE_PREFIX}{response_text}", history


def handle_message_from_list_generator(message_data):
    rag_service = RagPrompt(chat_id=message_data["chat_id"], before_list=False)
    recommendations = json.loads(get_list(str(message_data["chat_id"])))
    recommendations = create_recommedation(recommendations)
    ai_message, history = rag_service.invoke_first_message_after_list(json.dumps(recommendations))
    return f"{PrefixSuffixEnum.FROM_LLM_MESSAGE_PREFIX}{ai_message}", history


def get_list(chat_id):
    return DataService.get_data(chat_id + PrefixSuffixEnum.LIST_KEY_SUFFIX)


def get_history(chat_id):
    return DataService.get_data(chat_id)
