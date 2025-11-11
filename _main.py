# -------------------------------
# NYFITCOACH_BOT/_main.py (2025 완성형 통합버전)
# -------------------------------
import os
import re
import asyncio
import random
import datetime
import requests
import nest_asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)

# ========= 환경설정 =========
from config.env import BOT_TOKEN, WEATHER_KEY
from modules.user_module import get_user, update_user, get_user_data, load_data
from modules.weather_module import get_weather
from modules.coach_module import build_coach_message

TOKEN = BOT_TOKEN
nest_asyncio.apply()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
os.makedirs("data", exist_ok=True)

# ========= 상단 도움말 (위쪽 배치용) =========
HELP_HINTS = (
    "📌 **도움말**\n"
    "• '홈트' 입력 시 유튜브 홈트 영상 추천 🎥 (랜덤)\n"
    "• '내 정보'로 현재 설정 확인, '변경'으로 재설정 가능 🧾\n"
    "• '오늘 날씨 어때?' → 실내/실외 운동 추천 + 날씨 안내 🌦\n"
)

# ========= 톤 =========
TONE_STYLES = {
    "friendly": {
        "greetings": ["좋아~ 오늘도 에너지 넘치네 😄", "오~ 오늘 기분 좋아 보여!", "힘내자 나연아 💕"],
        "encourage": ["조금만 더! 넌 할 수 있어 😎", "너무 잘하고 있어 👏", "지금 페이스 좋아~"]
    },
    "coach": {
        "greetings": ["오늘 컨디션 점검 완료 💪", "집중하자, 오늘 루틴 가자!", "좋은 자세로 시작하자!"],
        "encourage": ["자, 코어 힘주고 가자!", "지금처럼만 계속해!", "그 자세 유지! 완벽해."]
    },
    "healing": {
        "greetings": ["오늘도 잘 버텨줘서 고마워 🌷", "괜찮아, 지금 그대로도 충분해 🌿", "잠시 쉬어가도 돼, 나연아 ☁️"],
        "encourage": ["힘들 땐 쉬어가도 괜찮아 💜", "조급해하지 마. 네가 잘하고 있어 🌱", "하루하루가 다 의미 있는 발걸음이야 🌸"]
    }
}
def get_tone_message(user_id, category="greetings"):
    tone = get_user_data(user_id, "tone") or "friendly"
    return random.choice(TONE_STYLES[tone][category])

# ========= 유튜브 데이터 (랜덤추천) =========
YOUTUBE_HOME_TRAINING = {
    "스트레칭": [
        "https://youtu.be/AjNfMZJk0mQ", "https://youtu.be/VkV8V0z8v7E", "https://youtu.be/z8wVb6s6T9k"
    ],
    "요가": [
        "https://youtu.be/k1Rx5yElnp8", "https://youtu.be/qzOmE7Uk5V4", "https://youtu.be/Zx2lNQ7Rrjs"
    ],
    "상체": [
        "https://youtu.be/Ec1nD-OMK8E", "https://youtu.be/yRytTh6QxgA", "https://youtu.be/MoQq7A91bN8"
    ],
    "하체": [
        "https://youtu.be/d2Q4DgRwA1s", "https://youtu.be/rxQz3H6yr9A", "https://youtu.be/9vE6tG8p5sA"
    ],
    "코어": [
        "https://youtu.be/TfY4KvFrYxQ", "https://youtu.be/0gMKnDn_zbg", "https://youtu.be/BJ3fGkXu0s4"
    ],
    "유산소": [
        "https://youtu.be/Z5kzY0QHnY8", "https://youtu.be/pj6s9bPOx54", "https://youtu.be/gPZ6A9RQKyM"
    ]
}

def random_youtube_link(category):
    """카테고리별로 유튜브 링크 중 랜덤 추천"""
    links = YOUTUBE_HOME_TRAINING.get(category, [])
    return random.choice(links) if links else None

# ========= 지역 매핑 =========
CITY_MAP = {
    "성남시 수정구": "Seongnam", "성남시 중원구": "Seongnam", "성남시 분당구": "Seongnam",
    "달성군 다사읍": "Daegu", "서울": "Seoul", "부산": "Busan", "대구": "Daegu",
    "인천": "Incheon", "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan",
    "수원": "Suwon", "창원": "Changwon", "제주": "Jeju"
}

# ========= 실내/실외 운동 추천 =========
def recommend_exercise_by_weather(desc, temp):
    indoor_keywords = ["비", "눈", "소나기", "천둥", "thunder"]
    outdoor_good = (10 <= temp <= 26) and not any(k in desc for k in indoor_keywords)
    if outdoor_good:
        return ("🌤 **실외 운동 추천!**", "🚴‍♀️ 달리기 / 걷기 / 자전거 / 등산 / 테니스 등 야외운동 어때요?")
    else:
        return ("🏠 **실내 운동 추천!**", "🧘 요가 / 코어 / 스트레칭 / 홈트레이닝으로 가볍게 시작해요 💪")

# ========= ReplyKeyboard =========
def build_keyboard(missing):
    buttons = []
    if "name" in missing: buttons.append(KeyboardButton("이름 입력"))
    if "location" in missing: buttons.append(KeyboardButton("지역 설정"))
    if "exercise" in missing: buttons.append(KeyboardButton("운동 종류"))
    if "time" in missing: buttons.append(KeyboardButton("알림시간"))
    if "tone" in missing: buttons.append(KeyboardButton("톤 선택"))
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True, one_time_keyboard=True) if buttons else None

# ========= 프로필 시각화 =========
def build_profile_progress(user: dict):
    tone_map = {"friendly": "친구형", "coach": "코치형", "healing": "힐링형"}
    name, loc, exr, time_, tone = (
        user.get("name"),
        user.get("location"),
        user.get("exercise"),
        user.get("notify_time"),
        user.get("tone"),
    )
    msg = [HELP_HINTS, "✅ **입력 정보 정리완료!**\n"]
    msg.append(f"1️⃣ 이름: {name or '❌ 없음'}")
    msg.append(f"2️⃣ 지역: {loc or '❌ 없음'}")
    msg.append(f"3️⃣ 운동: {exr or '❌ 없음'}")
    msg.append(f"4️⃣ 알림시간: {time_ or '❌ 없음'}")
    msg.append(f"5️⃣ 톤: {tone_map.get(tone, '❌ 없음') if tone else '❌ 없음'}")

    missing = []
    if not name: missing.append("name")
    if not loc: missing.append("location")
    if not exr: missing.append("exercise")
    if not time_: missing.append("time")
    if not tone: missing.append("tone")

    if missing:
        msg.append("\n🧭 누락된 항목이 있어요! 아래 버튼으로 채워요 👇")
    else:
        msg.append("\n🎯 모두 설정 완료!\n☀️ ‘오늘 날씨 어때?’  💪 ‘운동하자’  📋 ‘내 정보’ 가능!")
    return "\n".join(msg), missing

# ========= /start 및 “안녕” =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    get_user(user_id)
    await update.message.reply_text(
        HELP_HINTS
        + "\n\n안녕! 나는 운동코치봇 🏃‍♀️\n"
        "이름, 지역, 운동, 알림시간(24시간제), 말투(톤)를 알려줘!\n"
        "예: 나연, 성남시 수정구, 달리기, 17시, 코치"
    )

# ========= 텍스트 처리 =========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    get_user(user_id)

    if text == "안녕":
        await start(update, context)
        return

    if text in ["변경", "다시 입력", "수정", "변경모드"]:
        for k in ["name","location","exercise","notify_time","tone"]:
            update_user(user_id, k, None)
        await update.message.reply_text(HELP_HINTS + "\n\n🛠 모든 설정 초기화! 예: 나연, 성남시 수정구, 달리기, 17시, 코치")
        return

    if text in ["정보", "내 정보", "내 설정", "프로필"]:
        user = get_user(user_id)
        msg, missing = build_profile_progress(user)
        reply_markup = build_keyboard(missing) if missing else None
        await update.message.reply_text(msg, reply_markup=reply_markup)
        return

    if "홈트" in text:
        await update.message.reply_text(HELP_HINTS + "\n\n홈트 카테고리를 골라줘 💪\n상체 / 하체 / 코어 / 유산소 / 스트레칭 / 요가 중에서!")
        return

    if any(k in text for k in ["요가","스트레칭","상체","하체","코어","유산소"]):
        key = next((k for k in YOUTUBE_HOME_TRAINING if k in text), None)
        if key:
            link = random_youtube_link(key)
            await update.message.reply_text(f"🧘 {key} 영상이에요!\n🎥 {link}")
            return

    if "," in text:
        parts = [p.strip() for p in text.split(",")]
        for p in parts:
            if re.search(r"\d{1,2}\s*시", p):
                hour = int(re.search(r"\d{1,2}", p).group(0))
                update_user(user_id, "notify_time", f"{hour:02d}:00")
            elif any(k in p for k in ["시","군","구","읍","면","동","도"]):
                update_user(user_id, "location", p)
            elif any(k in p for k in ["달리기","요가","헬스","산책","등산","수영","자전거"]):
                update_user(user_id, "exercise", p)
            elif any(k in p for k in ["코치","힐링","친구"]):
                update_user(user_id, "tone", "coach" if "코치" in p else "healing" if "힐링" in p else "friendly")
            elif len(p) <= 4:
                update_user(user_id, "name", p)
        user = get_user(user_id)
        msg, missing = build_profile_progress(user)
        reply_markup = build_keyboard(missing) if missing else None
        await update.message.reply_text(msg, reply_markup=reply_markup)
        return

    if any(k in text for k in ["날씨","비","눈","더워","추워","오늘 날씨","지금 날씨"]):
        city = get_user_data(user_id, "location")
        if not city:
            await update.message.reply_text("먼저 지역을 알려줘! 예: ‘여긴 성남시 수정구야’")
            return
        city_en = CITY_MAP.get(city.strip(), city)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={WEATHER_KEY}&units=metric&lang=kr"
        res = requests.get(url)
        if res.status_code != 200:
            await update.message.reply_text("❌ 날씨 정보를 가져올 수 없어요.")
            return
        data = res.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        category, suggestion = recommend_exercise_by_weather(desc, temp)
        msg = (
            HELP_HINTS
            + f"\n\n📍 {city}의 현재 날씨입니다!\n"
            f"🌡 온도: {temp}°C / 상태: {desc}\n\n"
            f"{category}\n{suggestion}"
        )
        await update.message.reply_text(msg)
        return

    if "운동" in text or "운동하자" in text:
        city = get_user_data(user_id, "location")
        if not city:
            await update.message.reply_text("먼저 지역부터 알려줘! 예: ‘여긴 성남시 수정구야’")
            return
        result = get_weather(city, WEATHER_KEY)
        tone_msg = get_tone_message(user_id, "encourage")
        await update.message.reply_text(HELP_HINTS + f"\n\n{result}\n\n{tone_msg}")
        return

    await update.message.reply_text(HELP_HINTS + "\n\n예: ‘나연, 성남시 수정구, 달리기, 17시, 코치’ 이렇게 입력해봐!")

# ========= 메인 실행 =========
async def main():
    if not TOKEN or not WEATHER_KEY:
        print("🚨 .env 또는 config/env.py 확인 필요!")
        return

    print("🤖 NYFITCOACH_BOT 실행 중...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.job_queue.run_repeating(lambda ctx: None, interval=60, first=10)
    await app.run_polling(close_loop=False)

if __name__ == "__main__":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        nest_asyncio.apply()
        asyncio.run(main())
    except RuntimeError:
        print("⚙️ 이미 실행 중인 루프 감지 → 안전모드 전환 완료")
