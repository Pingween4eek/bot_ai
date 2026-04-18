import random


class SmallTalkSkill:

    RESPONSES = [
        "Всё отлично, спасибо!",
        "Хорошо, а у вас?",
        "Прекрасно! Готов помочь.",
        "Отлично! Чем могу быть полезен?",
        "Я бот, но настроение у меня всегда хорошее 😊",
    ]

    def handle(self) -> str:
        return random.choice(self.RESPONSES)
