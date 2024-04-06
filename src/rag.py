import os
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyD4ShYWIkPoNmco52c5IiaVTSXrLQCsoCk')


class RagPrompt:
    init_system_message = 'הוראות כלליות: על כל הודעה שנשמעת כמו בקשה לרשימת קניות חדשה תחזיר כתשובה רק את הטקסט: ״#רשימה#״. דוגמאות להודעות: ״רשימה חדשה״, ״הזמנה״, ״הזמנה חדשה״, ״רשימת קניות״, ״תכין לי רשימה״, ״אני הולך לסופר, מה לקנות?״ ועוד. על כל הודעה אחרת תענה בצורה רגילה'
    init_ai_message = 'okay'

    def __init__(self, history: list[tuple] = None):
        if not history:
            history = [
                ("human", self.init_system_message),
                ("ai", self.init_ai_message),
            ]
        self.history = history
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
        return self.chain.invoke(messages)
