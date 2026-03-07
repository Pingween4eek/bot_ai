import requests
from datetime import datetime, timedelta

API_KEY = ""


def get_weather(city: str) -> str:
    if not city:
        return "Не удалось определить город."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "ru"}

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 404:
            return f"Город «{city}» не найден в базе погодного сервиса."
        response.raise_for_status()
        data = response.json()
        temp        = data["main"]["temp"]
        feels_like  = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        wind_speed  = data["wind"]["speed"]
        humidity    = data["main"]["humidity"]
        return (
            f"Погода в городе {city} (сегодня):\n"
            f"Температура: {temp:.1f}°C (ощущается как {feels_like:.1f}°C)\n"
            f"Описание: {description}\n"
            f"Скорость ветра: {wind_speed:.1f} м/с\n"
            f"Влажность: {humidity}%"
        )
    except requests.exceptions.RequestException as e:
        return f"Ошибка соединения с погодным сервисом: {e}"


def get_weather_forecast(city: str, day_offset: int, day_label: str) -> str:
    if not city:
        return "Не удалось определить город."

    if day_offset > 5:
        return "Прогноз доступен максимум на 5 дней вперёд."

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "ru", "cnt": 40}

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 404:
            return f"Город «{city}» не найден в базе погодного сервиса."
        response.raise_for_status()
        data = response.json()

        # Ищем записи прогноза на нужный день
        target_date = (datetime.now() + timedelta(days=day_offset)).date()
        entries = [
            item for item in data["list"]
            if datetime.fromtimestamp(item["dt"]).date() == target_date
        ]

        if not entries:
            return f"Прогноз на {day_label} для города {city} недоступен."

        # Берём дневное время (12:00) или первую доступную запись
        day_entry = next(
            (e for e in entries if "12:00" in e["dt_txt"]),
            entries[len(entries) // 2]
        )

        temp        = day_entry["main"]["temp"]
        feels_like  = day_entry["main"]["feels_like"]
        temp_min    = min(e["main"]["temp_min"] for e in entries)
        temp_max    = max(e["main"]["temp_max"] for e in entries)
        description = day_entry["weather"][0]["description"]
        wind_speed  = day_entry["wind"]["speed"]
        humidity    = day_entry["main"]["humidity"]
        date_str    = target_date.strftime("%d.%m.%Y")

        return (
            f"Погода в городе {city} ({day_label}, {date_str}):\n"
            f"Температура: {temp:.1f}°C (ощущается как {feels_like:.1f}°C)\n"
            f"Мин/Макс за день: {temp_min:.1f}°C / {temp_max:.1f}°C\n"
            f"Описание: {description}\n"
            f"Скорость ветра: {wind_speed:.1f} м/с\n"
            f"Влажность: {humidity}%"
        )

    except requests.exceptions.RequestException as e:
        return f"Ошибка соединения с погодным сервисом: {e}"