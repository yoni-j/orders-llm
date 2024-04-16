class PubSource:
    LIST_GENERATOR: str = "list_generator"


class PrefixSuffixEnum:
    LIST_KEY_SUFFIX: str = "_list"
    FROM_LLM_MESSAGE_PREFIX = "#from_llm"


class RagEnum:
    INIT_SYSTEM_MESSAGE: str = 'הוראות כלליות: על כל הודעה שנשמעת כמו בקשה לרשימת קניות חדשה תחזיר כתשובה רק את הטקסט: ״#רשימה#״. דוגמאות להודעות: ״רשימה חדשה״, ״הזמנה״, ״הזמנה חדשה״, ״רשימת קניות״, ״תכין לי רשימה״, ״אני הולך לסופר, מה לקנות?״ ועוד. על כל הודעה אחרת תענה בצורה רגילה'
    INIT_AI_MESSAGE: str = 'okay'
    CREATE_LIST_TRIGGER: str = "#רשימה#"
    CREATE_LIST_RESPONSE: str = "מכין רשימה חדשה, כבר איתך"
    CREATE_ORDER_FROM_PREDICTION_USER_MESSAGE = "תכין לי רשימת קניות מהjson הזה" \
                                                ", הרשימה צריכה להחיל את שם המוצר, כמות, מחיר ליחידה ומחיר כולל" \
                                                " ובסוף את העלות הכוללת של הרשימה"
