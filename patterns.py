import re
from datetime import datetime
from weather_api import get_weather
from database import init_db, save_user, log_message_db, log_weather_query


class ChatBot:
    def __init__(self):
        self.name = None
        self.current_user_id = None
        self.waiting_for_name = False
        self.patterns = []
        init_db()
        self.register_patterns()

    def register_patterns(self):
        self.patterns.append(
            (re.compile(r"^(привет|здравствуй|добрый день|здравствуйте)$", re.IGNORECASE), self.greet)
        )

        self.patterns.append(
            (re.compile(r"^(пока|до свидания|выход)$", re.IGNORECASE), self.farewell)
        )

        self.patterns.append(
            (re.compile(r"меня зовут ([а-яА-Яa-zA-Z]+)", re.IGNORECASE), self.set_name)
        )

        self.patterns.append(
            (re.compile(r"погода в ([а-яА-Яa-zA-Z\- ]+)", re.IGNORECASE), self.handle_weather)
        )

        self.patterns.append(
            (re.compile(r"(\d+)\s*\+\s*(\d+)"), self.handle_addition)
        )

        self.patterns.append(
            (re.compile(r"как (у тебя )?дела", re.IGNORECASE), self.how_are_you)
        )

        self.patterns.append(
            (re.compile(r"(сколько|какое) (сейчас )?время", re.IGNORECASE), self.what_time)
        )

    def greet(self, match):
        if self.name:
            return f"Здравствуйте, {self.name}! Чем могу помочь?"
        self.waiting_for_name = True
        return "Здравствуйте! Чем могу помочь? Как вас зовут?"

    def farewell(self, match):
        if self.name:
            return f"До свидания, {self.name}! Было приятно пообщаться."
        return "До свидания!"

    def set_name(self, match):
        self.name = match.group(1).capitalize()
        self.current_user_id = save_user(self.name)
        return f"Приятно познакомиться, {self.name}!"

    def handle_weather(self, match):
        city = match.group(1).strip()
        if self.current_user_id:
            log_weather_query(self.current_user_id, city)
        return get_weather(city)

    def handle_addition(self, match):
        try:
            a = float(match.group(1))
            b = float(match.group(2))
            return f"Результат сложения: {a} + {b} = {a + b}"
        except:
            return "Не удалось выполнить сложение"

    def how_are_you(self, match):
        responses = [
            "Всё отлично, спасибо!",
            "Хорошо, а у вас?"
        ]
        import random
        return random.choice(responses)

    def what_time(self, match):
        now = datetime.now()
        return f"Сейчас {now.strftime('%H:%M')}"

    def process(self, message):
        import string
        message_clean = message.strip()

        # Если бот ждёт имя — любое одиночное слово воспринимаем как имя
        if self.waiting_for_name and re.match(r'^[а-яА-ЯёЁa-zA-Z]+$', message_clean):
            self.waiting_for_name = False
            self.name = message_clean.capitalize()
            self.current_user_id = save_user(self.name)
            return f"Приятно познакомиться, {self.name}!"

        for pattern, handler in self.patterns:
            match = pattern.search(message)
            if match:
                return handler(match)

        return "я не понимаю этот запрос"


bot = ChatBot()