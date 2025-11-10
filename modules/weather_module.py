import requests
import os
from dotenv import load_dotenv

load_dotenv()
WEATHER_KEY = os.getenv("WEATHER_KEY")

def get_weather(city_name: str) -> str:
    """
    도시 이름을 입력받아 현재 날씨 정보를 문자열로 반환하는 함수
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_KEY}&units=metric&lang=kr"
    res = requests.get(url)

    if res.status_code != 200:
        return "❌ 날씨 정보를 가져올 수 없습니다."

    data = res.json()
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]

    return f"{city_name}의 현재 온도는 {temp}°C, 날씨는 {desc}입니다."

