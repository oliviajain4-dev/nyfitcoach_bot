# -------------------------------
# NYFITCOACH_BOT/_main.py
# -------------------------------

# ① ─── 기본 내장 라이브러리 ───────────────────────────────
import os
import re
import asyncio

# ② ─── 외부 라이브러리 (pip 설치 모듈) ─────────────────────
from dotenv import load_dotenv
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ③ ─── 환경 설정 (.env 로드 + asyncio 환경 준비) ───────────
# ✅ .env 파일 로드 (루트 기준)
load_dotenv()
TOKEN = os.getenv("TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")

# ✅ asyncio (비동기 루프 설정)
# 이미 실행 중인 루프에서도 재실행 가능하게
nest_asyncio.apply()

# Windows 환경 전용 (Python 3.12 이상)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ④ ─── 내부 모듈 임포트 (네가 만든 기능들) ────────────────
from modules.location_module import set_city, get_city
from modules.weather_module import get_weather
from modules.coach_module import build_coach_message

# ⑤ ─── 명령어 함수 정의 (/start 등) ────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """사용자가 /start 입력 시 호출되는 함수"""
    await update.message.reply_text(
        "안녕! 나는 운동코치봇 🏃‍♀️\n"
        "1️⃣ 위치 알려줘 → 예: '여긴 서울이야'\n"
        "2️⃣ 그 다음 '날씨' 또는 '운동'이라고 말해줘!"
    )

# ⑥ ─── 텍스트 처리 함수 ────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """사용자의 일반 텍스트 입력 처리"""
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # 위치 설정
    if any(k in text for k in ["여긴", "여기는", "사는 곳", "도시"]):
        city = set_city(user_id, text)
        await update.message.reply_text(f"도시를 '{city}'로 기억했어! 🌆")
        return

    # 저장된 위치 확인
    city = get_city(user_id)
    if not city:
        await update.message.reply_text("먼저 도시를 알려줘! 예: '여긴 부산이야'")
        return

    # 날씨 요청
    if "날씨" in text:
        result = get_weather(city, WEATHER_KEY)
        await update.message.reply_text(result)
        return

    # 운동 추천
    if "운동" in text:
        weather_result = get_weather(city, WEATHER_KEY)
        if "오류" in weather_result or "없습니다" in weather_result:
            await update.message.reply_text(weather_result)
            return

        # 온도와 날씨 추출
        temp_match = re.search(r"([\d\.]+)°C", weather_result)
        desc_match = re.search(r"날씨는 ([\w]+)", weather_result)

        temp = float(temp_match.group(1)) if temp_match else None
        weather_main = desc_match.group(1) if desc_match else "Clouds"

        coach_msg = build_coach_message(weather_main, temp)
        await update.message.reply_text(f"{weather_result}\n\n{coach_msg}")
        return

    # 기본 응답
    await update.message.reply_text("알겠어! '날씨' 또는 '운동'이라고 말해줘 🙂")

# ⑦ ─── 메인 실행 함수 ─────────────────────────────────────
async def main():
    """봇 실행 메인 함수"""
    if not TOKEN:
        print("🚨 TOKEN 없음! .env 파일 확인!")
        return
    if not WEATHER_KEY:
        print("🚨 WEATHER_KEY 없음! .env 파일 확인!")
        return

    print("🤖 운동코치봇 실행 중...")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # ✅ run_polling 실행 (비동기 루프 닫지 않음)
    await app.run_polling(close_loop=False)

# ⑧ ─── 실행 진입점 ────────────────────────────────────────
if __name__ == "__main__":
    try:
        # ✅ Windows 전용 루프 설정
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # ✅ 이미 실행 중인 루프에서도 안전하게 실행
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

    except RuntimeError:
        # ✅ 이미 루프가 동작 중이면 새 task로 실행
        asyncio.get_event_loop().create_task(main())
        print("⚙️ 이미 실행 중인 루프 감지 → 안전모드로 전환 완료")
