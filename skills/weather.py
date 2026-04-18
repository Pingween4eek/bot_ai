from weather_api import get_weather, get_weather_forecast


class WeatherSkill:

    def handle(self, city: str, offset: int = 0, day_label: str = "сегодня") -> str:
        if offset == 0:
            return get_weather(city)
        return get_weather_forecast(city, offset, day_label)
