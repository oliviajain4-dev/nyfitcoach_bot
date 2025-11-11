# test/test_geocoding.py
import requests, os
from dotenv import load_dotenv

load_dotenv()
WEATHER_KEY = os.getenv("WEATHER_KEY")

def test_geocoding(location):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={WEATHER_KEY}"
    res = requests.get(url)
    print("🔍 상태코드:", res.status_code)
    print("📍 결과:", res.json())

if __name__ == "__main__":
    # 여기에 실험하고 싶은 주소를 마음껏 입력!
    test_geocoding("경기도 성남시 수정구 수정로 157")