from datetime import datetime

def log_message(user_message: str, bot_response: str):
    try:
        with open("chat_log.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] USER: {user_message}\n")
            f.write(f"[{timestamp}] BOT: {bot_response}\n")
            f.write("-" * 50 + "\n")
    except Exception as e:
        print(f"Ошибка при логировании: {e}")