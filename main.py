from handlers import process_message
from database import log_message_db
from tts_engine import voice_reply, preload
from voice import listen, clean_asr_text


def main():
    preload()

    print("Бот запущен (голосовой режим). Скажите 'выход' для завершения.")
    while True:
        user_input = clean_asr_text(listen())

        if not user_input:
            print("[ASR] Не удалось распознать речь, попробуйте ещё раз.")
            continue

        print("Вы:", user_input)

        if "выход" in user_input:
            print("Бот: До свидания!")
            break

        response = process_message(user_input)
        print("Бот:", response)

        voice_reply(response)

        from patterns import bot
        user_id = bot.current_user_id
        log_message_db(user_id, user_input, response)


if __name__ == "__main__":
    main()