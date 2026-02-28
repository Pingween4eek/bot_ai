from handlers import process_message
from database import log_message_db


def main():
    print("Бот запущен")
    while True:
        user_input = input("Вы: ")
        if user_input.lower() == 'выход':
            break

        response = process_message(user_input)
        print("Бот:", response)

        from patterns import bot
        user_id = bot.current_user_id
        log_message_db(user_id, user_input, response)


if __name__ == "__main__":
    main()