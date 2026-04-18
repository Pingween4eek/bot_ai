import re
import random
from datetime import datetime, timedelta

import spacy
from spacy.matcher import Matcher

from weather_api import get_weather, get_weather_forecast
from database import init_db, save_user, log_weather_query
from dialog_manager import (
    DialogState, get_state, set_state,
    get_user_data, set_user_data, reset_user_data
)
from intent_classifier import predict_with_confidence
from skills import WeatherSkill, TimeSkill, DateSkill, SmallTalkSkill, HelpSkill

nlp = spacy.load("ru_core_news_md")

matcher = Matcher(nlp.vocab)
matcher.add("WEATHER_QUERY", [
    [{"LEMMA": "погода"}, {"LOWER": {"IN": ["в", "во"]}}, {"POS": "PROPN"}],
    [{"LEMMA": "погода"}, {"LOWER": {"IN": ["в", "во"]}}, {"IS_TITLE": True}],
    [{"LEMMA": "погода"}, {"OP": "?"}, {"LOWER": {"IN": ["в", "во"]}}, {"POS": "PROPN"}],
])

DATE_KEYWORDS = {
    "сегодня":       0,
    "завтра":        1,
    "послезавтра":   2,
    "через два дня": 2,
    "через 2 дня":   2,
}

WEEKDAYS = {
    "понедельник": 0, "вторник": 1,
    "среду": 2,       "среда": 2,
    "четверг": 3,
    "пятницу": 4,     "пятница": 4,
    "субботу": 5,     "суббота": 5,
    "воскресенье": 6,
}


EXACT_COMMANDS = {
    "пока":      "goodbye",
    "стоп":      "goodbye",
    "выход":     "goodbye",
    "выйти":     "goodbye",
    "конец":     "goodbye",
    "хватит":    "goodbye",
    "закончить": "goodbye",
    "завершить": "goodbye",
    "привет":    "greeting",
    "хай":       "greeting",
    "салют":     "greeting",
    "ку":        "greeting",
    "время":     "time",
    "час":       "time",
    "дата":      "date",
    "число":     "date",
    "помощь":    "help",
    "справка":   "help",
}

# Ключевые слова для поиска внутри фразы
KEYWORD_INTENTS: list[tuple[list[str], str]] = [
    (["привет", "здравствуй", "здравствуйте", "здрасьте", "хелло",
      "добрый день", "доброе утро", "добрый вечер", "хай", "салют",
      "дарова", "хэй", "йоу"], "greeting"),
    (["пока", "до свидания", "прощай", "бывай", "до встречи",
      "всего хорошего", "всего доброго", "увидимся"], "goodbye"),
    (["погода", "температура", "дождь", "снег", "прогноз",
      "солнечно", "облачно", "ветер", "осадки"], "weather"),
    (["сколько времени", "который час", "текущее время"], "time"),
    (["какое число", "какая дата", "сегодняшняя дата",
      "текущая дата", "какой день"], "date"),
    (["что умеешь", "что можешь", "помощь", "справка",
      "список команд", "как пользоваться"], "help"),
]


def extract_date_offset(text: str) -> tuple[int, str]:
    text_lower = text.lower()
    for keyword, offset in DATE_KEYWORDS.items():
        if keyword in text_lower:
            labels = {0: "сегодня", 1: "завтра", 2: "послезавтра"}
            return offset, labels.get(offset, f"через {offset} дня")
    today_wd = datetime.now().weekday()
    for word, target_wd in WEEKDAYS.items():
        if word in text_lower:
            offset = (target_wd - today_wd) % 7
            if offset == 0:
                offset = 7
            return offset, word
    return 0, "сегодня"


def extract_city(text: str) -> str | None:
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            return ent.root.lemma_.capitalize()
    m = re.search(r"\bв[о]?\s+([А-ЯЁ][а-яёА-ЯЁ\-]+)", text)
    if m:
        word    = m.group(1)
        word_doc = nlp(word)
        return word_doc[0].lemma_.capitalize() if word_doc else word
    return None


class ChatBot:
    def __init__(self):
        self.name            = None
        self.current_user_id = None
        self.waiting_for_name = False
        init_db()

        self._weather_skill  = WeatherSkill()
        self._time_skill     = TimeSkill()
        self._date_skill     = DateSkill()
        self._smalltalk_skill = SmallTalkSkill()
        self._help_skill     = HelpSkill()

    def _handle_greeting(self) -> str:
        if self.name:
            return f"Здравствуйте, {self.name}! Чем могу помочь?"
        self.waiting_for_name = True
        return "Здравствуйте! Чем могу помочь? Как вас зовут?"

    def _handle_farewell(self) -> str:
        if self.current_user_id:
            set_state(self.current_user_id, DialogState.START)
            reset_user_data(self.current_user_id)
        if self.name:
            return f"До свидания, {self.name}! Было приятно пообщаться."
        return "До свидания!"

    def _handle_smalltalk(self) -> str:
        return self._smalltalk_skill.handle()

    def _handle_time(self) -> str:
        return self._time_skill.handle()

    def _handle_date(self) -> str:
        return self._date_skill.handle()

    def _handle_help(self) -> str:
        return self._help_skill.handle()

    def _handle_weather(self, message: str) -> str:
        city = extract_city(message)
        offset, day_label = extract_date_offset(message)
        if city:
            if self.current_user_id:
                log_weather_query(self.current_user_id, city)
            return self._weather_skill.handle(city, offset, day_label)
        else:
            return self._start_weather_dialog(None, message)

    def _route_intent(self, intent: str, message: str) -> str:
        if intent == "greeting":  return self._handle_greeting()
        if intent == "goodbye":   return self._handle_farewell()
        if intent == "smalltalk": return self._handle_smalltalk()
        if intent == "time":      return self._handle_time()
        if intent == "date":      return self._handle_date()
        if intent == "help":      return self._handle_help()
        if intent == "weather":   return self._handle_weather(message)
        return "я не понимаю этот запрос"

    def _start_weather_dialog(self, city: str | None, message: str) -> str:
        uid = self.current_user_id if self.current_user_id else "guest"
        if city:
            set_user_data(uid, "city", city)
            set_state(uid, DialogState.WAIT_DATE)
            return f"Город {city} определён. На какую дату? (сегодня / завтра / послезавтра / день недели)"
        else:
            set_state(uid, DialogState.WAIT_CITY)
            return "В каком городе вас интересует погода?"

    def handle_fsm(self, message: str) -> str | None:
        uid   = self.current_user_id if self.current_user_id else "guest"
        state = get_state(uid)

        if state == DialogState.WAIT_CITY:
            city = extract_city(message) or message.strip().capitalize()
            set_user_data(uid, "city", city)
            set_state(uid, DialogState.WAIT_DATE)
            return "На какую дату? (сегодня / завтра / послезавтра / день недели)"

        if state == DialogState.WAIT_DATE:
            offset, day_label = extract_date_offset(message)
            city = get_user_data(uid).get("city", "")
            set_state(uid, DialogState.START)
            reset_user_data(uid)
            if self.current_user_id:
                log_weather_query(self.current_user_id, city)
            return get_weather(city) if offset == 0 else get_weather_forecast(city, offset, day_label)

        return None

    def process(self, message: str) -> str:
        message_clean = message.strip()
        message_lower = message_clean.lower()
        fsm_uid   = self.current_user_id if self.current_user_id else "guest"
        fsm_state = get_state(fsm_uid)

        if fsm_state in (DialogState.WAIT_CITY, DialogState.WAIT_DATE):
            original_uid         = self.current_user_id
            self.current_user_id = fsm_uid
            fsm_response         = self.handle_fsm(message_clean)
            self.current_user_id = original_uid
            if fsm_response is not None:
                return fsm_response

        if self.waiting_for_name and re.match(r'^[а-яА-ЯёЁa-zA-Z]+$', message_clean):
            self.waiting_for_name = False
            self.name             = message_clean.capitalize()
            self.current_user_id  = save_user(self.name)
            return f"Приятно познакомиться, {self.name}!"

        if message_lower in EXACT_COMMANDS:
            intent = EXACT_COMMANDS[message_lower]
            return self._route_intent(intent, message_clean)

        for keywords, kw_intent in KEYWORD_INTENTS:
            for kw in keywords:
                if kw in message_lower:
                    print(f"[KW] intent={kw_intent!r}, matched keyword={kw!r}")
                    return self._route_intent(kw_intent, message_clean)

        intent, confidence = predict_with_confidence(message_clean)
        print(f"[BERT] intent={intent!r}, confidence={confidence:.2f}")

        if confidence < 0.35:
            return "Я не уверен что понял вас. Попробуйте переформулировать."

        return self._route_intent(intent, message_clean)


bot = ChatBot()