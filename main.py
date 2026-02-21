from handlers import process_message
from logger import log_message


def main():
    print("Бот запущен")
    while True:
        user_input = input("Вы: ")
        if user_input.lower() == 'выход':
            break

        response = process_message(user_input)
        print("Бот:", response)
        log_message(user_input, response)


if __name__ == "__main__":
    main()