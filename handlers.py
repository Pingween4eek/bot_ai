from patterns import bot


def process_message(message: str) -> str:
    if not message or not message.strip():
        return "Пожалуйста, введите сообщение."

    return bot.process(message)


def handle_greeting():
    return bot.greet(None)


def handle_farewell():
    return bot.farewell(None)