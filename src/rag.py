import json
import os
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages.human import HumanMessage

from google.cloud import pubsub_v1

from enums import RagEnum

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


class RagPrompt:

    def __init__(self, chat_id: str, history=None, before_list: bool = True):
        if history is None:
            history = []
        self.before_list = before_list
        self.history = self._tune_history(history)
        self.llm = self._get_llm()
        self.parser = StrOutputParser()
        self.chain = self.llm | self.parser
        self.chat_id = chat_id

    def invoke(self, user_text: str) -> tuple:
        message_prompt = "{text}"
        chat_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template(message_prompt)
        ])
        messages = chat_template.format_messages(chat_history=self.history, text=user_text)
        response_text = self._chain_invoke(messages)
        self.history += [("human", messages[-1].content), ("ai", response_text)]
        return self._handle_response_text(response_text), self.history

    def _tune_history(self, history: list[tuple]) -> list[tuple]:
        before_init_history = [
            ("human", RagEnum.INIT_SYSTEM_MESSAGE),
            ("ai", RagEnum.INIT_AI_MESSAGE),
        ]
        if self.before_list:
            if before_init_history[0] not in history:
                return before_init_history + history
        return history

    def _handle_response_text(self, text: str) -> str:
        if text == RagEnum.CREATE_LIST_TRIGGER:
            self._generate_list()
            return RagEnum.CREATE_LIST_RESPONSE
        return text

    def _generate_list(self):
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path("yonidev", "generate-list-topic")
        message_bytes = json.dumps(
            {"chat_id": self.chat_id}
        ).encode("utf-8")
        try:
            publish_future = publisher.publish(topic_path, data=message_bytes)
            publish_future.result()
        except Exception as e:
            print(f"Error publishing message: {e}")

    def invoke_first_message_after_list(self, orders_json_str: str):
        message_prompt = orders_json_str+RagEnum.CREATE_ORDER_FROM_PREDICTION_USER_MESSAGE
        chat_template = ChatPromptTemplate.from_messages([
            HumanMessage(content=message_prompt)
        ])
        messages = chat_template.format_messages(orders_json_str=orders_json_str)
        response_text = self._chain_invoke(messages)
        self.history = [
            ("human", messages[0].content),
            ("ai", response_text)
        ]
        return self._handle_response_text(response_text), self.history

    def _chain_invoke(self, messages) -> str:
        return self.chain.invoke(messages)

    @staticmethod
    def _get_llm():
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.0, google_api_key=GOOGLE_API_KEY)
