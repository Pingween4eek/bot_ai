import requests

API_KEY = ""

def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        humidity = data["main"]["humidity"]

        return (f"Погода в городе {city}:\n"
                f"Температура: {temp:.1f}°C (ощущается как {feels_like:.1f}°C)\n"
                f"Описание: {description}\n"
                f"Скорость ветра: {wind_speed:.1f} м/с\n"
                f"Влажность: {humidity}%")

    except requests.exceptions.RequestException:
        return "Ошибка соединения с погодным сервисом."