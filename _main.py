from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

from modules.location_module import set_city, get_city
from modules.weather_module import get_weather
from modules.coach_module import build_coach_message

# 🔑 토큰 채우기
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "안녕! 나는 운동코치봇 🏃‍♀️\n"
        "처음엔 위치부터 알려줘 👉 예) '여긴 성남시 수정구야'\n"
        "그 다음엔 '날씨' 또는 '운동' 이라고 말해봐!"
    )

# 자연어 처리: 위치 설정 / 날씨 / 운동
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    # 1) 위치 설정
    if any(k in text for k in ["여긴", "여기는", "사는 곳", "도시"]):
        city = set_city(user_id, text)
        await update.message.reply_text(f"✅ 도시를 '{city}'로 기억했어!")
        return

    # 2) 저장된 도시 확인
    city = get_city(user_id)
    if not city:
        await update.message.reply_text("🗺️ 먼저 도시를 알려줘! 예) '여긴 대구 달성군이야'")
        return

    # 3) 날씨 요청
    if "날씨" in text:
        weather, temp, desc = get_weather(city, WEATHER_KEY)
        if not weather:
            await update.message.reply_text(f"'{city}' 날씨를 찾을 수 없었어 😅")
            return
        await update.message.reply_text(f"📍{city}\n🌡 {temp}℃, 🌦 {desc}")
        return

    # 4) 운동 코칭
    if "운동" in text:
        weather, temp, desc = get_weather(city, WEATHER_KEY)
        if not weather:
            await update.message.reply_text(f"'{city}' 날씨를 찾을 수 없었어 😅")
            return
        coach_msg = build_coach_message(weather, temp)
        await update.message.reply_text(
            f"📍{city}\n🌡 {temp}℃, 🌦 {desc}\n\n{coach_msg}"
        )
        return

    # 기본 안내
    await update.message.reply_text("알겠어! '날씨' 또는 '운동'이라고 말해줘 🙂")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🤖 운동코치봇 실행 중…")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
