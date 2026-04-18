from datetime import datetime


class DateSkill:

    def handle(self) -> str:
        return f"Сегодня {datetime.now().strftime('%d.%m.%Y')}"
