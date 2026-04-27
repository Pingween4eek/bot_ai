from handlers import process_message
from database import log_message_db
from tts_engine import voice_reply, preload


def main():
    preload()

    print("Бот запущен")
    while True:
        user_input = input("Вы: ")
        if user_input.lower() == 'выход':
            break

        response = process_message(user_input)
        print("Бот:", response)

        voice_reply(response)

        from patterns import bot
        user_id = bot.current_user_id
        log_message_db(user_id, user_input, response)


if __name__ == "__main__":
    main()