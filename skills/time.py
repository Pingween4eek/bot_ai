from datetime import datetime


class TimeSkill:

    def handle(self) -> str:
        return f"Сейчас {datetime.now().strftime('%H:%M')}"
