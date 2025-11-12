# -------------------------------
# modules/weather_module.py
# -------------------------------
import os, requests, random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from config.env import WEATHER_KEY
from modules.youtube_module import get_random_video

OUTFIT_DIR = "data/outfits"
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

CITY_MAP = {
    "성남시 수정구": "Seongnam", "성남시 중원구": "Seongnam", "성남시 분당구": "Seongnam",
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon",
    "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "제주": "Jeju"
}

# ===== 날씨 이모지 매핑 =====
def get_weather_icon(desc: str) -> str:
    desc = desc.lower()
    if any(k in desc for k in ["맑", "clear"]): return "☀️"
    if any(k in desc for k in ["구름", "cloud"]): return "🌤️"
    if any(k in desc for k in ["비", "rain", "소나기"]): return "🌧️"
    if any(k in desc for k in ["눈", "snow"]): return "❄️"
    if any(k in desc for k in ["번개", "thunder"]): return "⛈️"
    if any(k in desc for k in ["안개", "fog", "mist"]): return "🌫️"
    return "🌈"

# ===== 오늘 날씨 =====
def get_weather(city_kr: str) -> dict:
    city_en = CITY_MAP.get(city_kr.strip(), city_kr)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={WEATHER_KEY}&units=metric&lang=kr"
    res = requests.get(url, timeout=5)
    data = res.json()
    desc = data["weather"][0]["description"]
    return {
        "city": city_kr,
        "temp": round(data["main"]["temp"], 1),
        "feels": round(data["main"]["feels_like"], 1),
        "desc": desc,
        "icon": get_weather_icon(desc)
    }

# ===== 내일 예보 =====
def get_tomorrow_weather(city_kr: str) -> dict:
    city_en = CITY_MAP.get(city_kr.strip(), city_kr)
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_en}&appid={WEATHER_KEY}&units=metric&lang=kr"
    res = requests.get(url, timeout=5)
    data = res.json()
    target = next((item for item in data["list"] if "12:00:00" in item["dt_txt"]), None)
    if not target:
        target = data["list"][8] if len(data["list"]) > 8 else data["list"][0]
    desc = target["weather"][0]["description"]
    return {
        "temp": round(target["main"]["temp"], 1),
        "desc": desc,
        "icon": get_weather_icon(desc)
    }

# ===== 복장 + 운동 추천 =====
def recommend_outfit(temp: float, desc: str) -> dict:
    indoor_keywords = ["비","눈","소나기","thunder","rain","snow"]
    outdoor_good = (10 <= temp <= 26) and not any(k in desc for k in indoor_keywords)
    exercise_text = "🌤 실외운동 (산책, 자전거, 달리기, 축구)" if outdoor_good else "🏠 실내운동 (요가, 홈트, 스트레칭)"
    outfit_text = (
        "☔ 방수 자켓 + 운동화" if "비" in desc
        else "⛄ 따뜻한 방한복" if "눈" in desc
        else "😎 반팔 + 반바지" if temp >= 25
        else "🍂 긴팔 트레이닝복" if 15 <= temp < 25
        else "🧤 기모 트레이닝복" if 5 <= temp < 15
        else "🥶 패딩 + 장갑"
    )
    return {"outfit": outfit_text, "exercise": exercise_text, "is_outdoor": outdoor_good}

# ===== 이미지 선택 =====
def select_outfit_image(temp: float, desc: str) -> str:
    if "비" in desc: return os.path.join(OUTFIT_DIR, "rain.png")
    if "눈" in desc: return os.path.join(OUTFIT_DIR, "snow.png")
    if temp >= 25: return os.path.join(OUTFIT_DIR, "summer.png")
    if 15 <= temp < 25: return os.path.join(OUTFIT_DIR, "autumn.png")
    if 5 <= temp < 15: return os.path.join(OUTFIT_DIR, "winter.png")
    return os.path.join(OUTFIT_DIR, "heavy_winter.png")

# ===== 카드 생성 =====
def build_outfit_card(user_name: str, city: str):
    today = get_weather(city)
    tomorrow = get_tomorrow_weather(city)
    reco = recommend_outfit(today["temp"], today["desc"])
    category = "요가" if not reco["is_outdoor"] else "스트레칭"
    video = get_random_video(category)

    img_path = select_outfit_image(today["temp"], today["desc"])
    img = Image.open(img_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 40)
        font_info = ImageFont.truetype("arial.ttf", 26)
    except:
        font_title = ImageFont.load_default()
        font_info = ImageFont.load_default()

    title = f"{user_name}'s Weather & Workout 🩵"
    info = f"{today['icon']} {today['temp']}°C / {today['desc']} / 체감 {today['feels']}°C"
    outfit_line = reco["outfit"]
    exercise_line = reco["exercise"]
    tomorrow_line = f"{tomorrow['icon']} 내일: {tomorrow['temp']}°C / {tomorrow['desc']}"

    draw.rectangle([(30, 30), (img.width - 30, 240)], fill=(255, 255, 255, 230))
    draw.text((50, 50), title, fill=(40, 40, 60), font=font_title)
    draw.text((50, 100), info, fill=(40, 40, 60), font=font_info)
    draw.text((50, 140), outfit_line, fill=(20, 20, 20), font=font_info)
    draw.text((50, 180), exercise_line, fill=(20, 40, 80), font=font_info)
    draw.text((50, 215), tomorrow_line, fill=(70, 60, 100), font=font_info)

    output_path = os.path.join(TEMP_DIR, f"{user_name}_outfit.png")
    img.save(output_path)

    caption = (
        f"{today['icon']} 오늘의 날씨 ({city})\n"
        f"🌡 {today['temp']}°C / {today['desc']} / 체감 {today['feels']}°C\n\n"
        f"👕 복장: {reco['outfit']}\n"
        f"💪 운동: {reco['exercise']}\n\n"
        f"🎬 추천 영상 ({category})\n"
        f"{video['title']}\n👉 {video['link']}\n\n"
        f"{tomorrow['icon']} 내일: {tomorrow['temp']}°C / {tomorrow['desc']}"
    )
    return output_path, caption
