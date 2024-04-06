import os
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder

from mock_list import create_mock_recommendations

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyD4ShYWIkPoNmco52c5IiaVTSXrLQCsoCk')


class RagPrompt:
    init_system_message = 'הוראות כלליות: על כל הודעה שנשמעת כמו בקשה לרשימת קניות חדשה תחזיר כתשובה רק את הטקסט: ״#רשימה#״. דוגמאות להודעות: ״רשימה חדשה״, ״הזמנה״, ״הזמנה חדשה״, ״רשימת קניות״, ״תכין לי רשימה״, ״אני הולך לסופר, מה לקנות?״ ועוד. על כל הודעה אחרת תענה בצורה רגילה'
    init_ai_message = 'okay'
    CREATE_LIST_TRIGGER = "#רשימה#"
    CREATE_LIST_RESPONSE = "מכין רשימה חדשה, כבר איתך"

    def __init__(self, history=None, before_list: bool = True):
        if history is None:
            history = []
        self.before_list = before_list
        self.history = self._tune_history(history)
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.0, google_api_key=GOOGLE_API_KEY)
        self.parser = StrOutputParser()
        self.chain = self.llm | self.parser

    def invoke(self, user_text: str) -> str:
        message_prompt = "{text}"
        chat_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template(message_prompt)
        ])
        messages = chat_template.format_messages(chat_history=self.history, text=user_text)
        response_text = self.chain.invoke(messages)
        return self._handle_response_text(response_text)

    def _tune_history(self, history: list[tuple]) -> list[tuple]:
        before_init_history = [
            ("human", self.init_system_message),
            ("ai", self.init_ai_message),
        ]
        if self.before_list:
            if before_init_history[0] not in history:
                return before_init_history + history
        return history

    def _handle_response_text(self, text: str) -> str:
        if text == self.CREATE_LIST_TRIGGER:
            self._generate_list()
            # return self.CREATE_LIST_RESPONSE
            # TODO: remove mock after implement list generator
            return self.invoke_first_message_after_list(create_mock_recommendations())
        return text

    def _generate_list(self):
        # TODO: trigger list generator
        pass

    def invoke_first_message_after_list(self, orders_json_str: str):
        message_prompt = "תכין לי רשימת קניות מהjson הזה, הרשימה צריכה להחיל את שם המוצר, כמות ומחיר" \
                         "\n" \
                         "{orders_json_str}"
        chat_template = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template(message_prompt)
        ])
        messages = chat_template.format_messages(orders_json_str=orders_json_str)
        response_text = self.chain.invoke(messages)
        return self._handle_response_text(response_text)
