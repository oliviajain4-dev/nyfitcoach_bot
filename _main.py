# -------------------------------
# NYFITCOACH_BOT/_main.py (2025 완성형 통합버전 - 1/2)
# -------------------------------
import os, re, asyncio, random, datetime, requests, nest_asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ========= 환경설정 =========
from config.env import BOT_TOKEN, WEATHER_KEY
from modules.user_module import get_user, update_user, get_user_data, load_data
from modules.weather_module import get_weather
from modules.coach_module import build_coach_message
from modules.youtube_module import get_random_video

TOKEN = BOT_TOKEN
nest_asyncio.apply()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
os.makedirs("data", exist_ok=True)

# ========= 도움말 (자동 업데이트용) =========
def get_help_text():
    return (
        "📌 **도움말**\n"
        "• '홈트' → 카테고리별 유튜브 추천 🎥 (상체/하체/전신/코어/유산소/스트레칭/요가/HIIT/필라테스/복근/스트렝스)\n"
        "• '내 정보' → 설정 확인, '변경' → 재설정 🧾\n"
        "• '날씨', '오늘 날씨 어때?', '내일날씨어때?' → 날씨 안내 🌦\n"
        "• '운동하자' → 코칭 + 날씨 추천 💪"
    )

HELP_HINTS = get_help_text()

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

YT_CATEGORIES = ["상체","하체","전신","코어","유산소","스트레칭","요가","HIIT","필라테스","복근","스트렝스","상관없음"]

CITY_MAP = {
    "성남시 수정구": "Seongnam", "성남시 중원구": "Seongnam", "성남시 분당구": "Seongnam",
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon",
    "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "제주": "Jeju"
}

def recommend_exercise_by_weather(desc, temp):
    indoor_keywords = ["비","눈","소나기","천둥","thunder"]
    outdoor_good = (10 <= temp <= 26) and not any(k in desc for k in indoor_keywords)
    if outdoor_good:
        return ("🌤 **실외 운동 추천!**", "🚴‍♀️ 달리기 / 걷기 / 자전거 / 등산 등 야외운동 어때요?")
    else:
        return ("🏠 **실내 운동 추천!**", "🧘 요가 / 코어 / 스트레칭 / 홈트레이닝 추천 💪")

#2
# -------------------------------
# NYFITCOACH_BOT/_main.py (2025 완성형 통합버전 - 2/2)
# -------------------------------
def build_keyboard(missing):
    buttons = []
    if "name" in missing: buttons.append(KeyboardButton("이름 입력"))
    if "location" in missing: buttons.append(KeyboardButton("지역 설정"))
    if "exercise" in missing: buttons.append(KeyboardButton("운동 종류"))
    if "time" in missing: buttons.append(KeyboardButton("알림시간"))
    if "tone" in missing: buttons.append(KeyboardButton("톤 선택"))
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True, one_time_keyboard=True) if buttons else None

def build_profile_progress(user: dict):
    tone_map = {"friendly": "친구형", "coach": "코치형", "healing": "힐링형"}
    name, loc, exr, time_, tone = (
        user.get("name"), user.get("location"), user.get("exercise"),
        user.get("notify_time"), user.get("tone")
    )
    msg = [HELP_HINTS, "✅ **입력 정보 정리완료!**\n"]
    msg.append(f"1️⃣ 이름: {name or '❌ 없음'}")
    msg.append(f"2️⃣ 지역: {loc or '❌ 없음'}")
    msg.append(f"3️⃣ 운동: {exr or '❌ 없음'}")
    msg.append(f"4️⃣ 알림시간: {time_ or '❌ 없음'}")
    msg.append(f"5️⃣ 톤: {tone_map.get(tone, '❌ 없음') if tone else '❌ 없음'}")
    return "\n".join(msg), []

# ========= /start =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)
    await update.message.reply_text(
        get_help_text() + "\n\n안녕! 나는 운동코치봇 🏃‍♀️\n"
        "이름, 지역, 운동, 시간, 말투(톤)를 알려줘!\n"
        "예: 나연, 성남시 수정구, 달리기, 17시, 코치"
    )

# ========= 메시지 처리 =========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    get_user(user_id)

    # 도움말 자동 호출
    if text in ["도움말", "help", "Help"]:
        await update.message.reply_text(get_help_text())
        return

    if "홈트" in text:
        await update.message.reply_text(get_help_text() + "\n\n홈트 카테고리 골라줘 💪\n" + " / ".join(YT_CATEGORIES))
        return

    if any(k in text for k in YT_CATEGORIES):
        key = next((k for k in YT_CATEGORIES if k in text), "전신")
        vid = get_random_video(key)
        await update.message.reply_photo(
            photo=vid["thumbnail"],
            caption=f"🎬 {key} 추천 영상!\n{vid['title']}\n👉 {vid['link']}"
        )
        return

    if re.search(r"(오늘\s*날씨|날씨)(어때)?\??", text):
        city = get_user_data(user_id, "location") or "서울"
        city_en = CITY_MAP.get(city.strip(), city)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={WEATHER_KEY}&units=metric&lang=kr"
        data = requests.get(url).json()
        temp, desc = data["main"]["temp"], data["weather"][0]["description"]
        cat, sug = recommend_exercise_by_weather(desc, temp)
        msg = f"📍 {city}\n🌡 {temp}°C / {desc}\n\n{cat}\n{sug}"
        await update.message.reply_text(msg)
        return

    await update.message.reply_text(get_help_text())

# ========= 실행 =========
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🤖 NYFITCOACH_BOT 실행 중...")
    await app.run_polling(close_loop=False)

if __name__ == "__main__":
    asyncio.run(main())
