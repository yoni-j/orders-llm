import os
from langchain.prompts import SystemMessagePromptTemplate, AIMessagePromptTemplate, ChatPromptTemplate, \
    HumanMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


class RagPrompt:
    init_system_message = 'הוראות כלליות: על כל הודעה שנשמעת כמו בקשה לרשימת קניות חדשה תחזיר כתשובה רק את הטקסט: ״#רשימה#״. דוגמאות להודעות: ״רשימה חדשה״, ״הזמנה״, ״הזמנה חדשה״, ״רשימת קניות״, ״תכין לי רשימה״, ״אני הולך לסופר, מה לקנות?״ ועוד. על כל הודעה אחרת תענה בצורה רגילה'
    init_ai_message = 'okay'

    def __init__(self):
        self.chat_template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template("{init_system_message}"),
                AIMessagePromptTemplate.from_template("{init_ai_message}")
            ]
        )
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.0, convert_system_message_to_human=True,
                                          google_api_key=GOOGLE_API_KEY)
        self.parser = StrOutputParser()
        self.chain = self.llm | self.parser

    def invoke(self, user_text: str) -> str:
        message_template = HumanMessagePromptTemplate(
            content=(
                user_text
            )
        )
        self.chat_template.append(message_template)
        messages = self.chat_template.format_messages(init_system_message=self.init_system_message,
                                                      init_ai_message=self.init_ai_message)
        return self.chain.invoke(messages)
