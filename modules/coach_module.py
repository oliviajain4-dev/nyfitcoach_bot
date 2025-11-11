def build_coach_message(weather_main: str, temp: float) -> str:
    """
    날씨 + 기온에 따라 코칭 메시지 생성.
    v1 기본값: 달리기 30분, 근력 10분, 스트레칭 10분.
    나중엔 config 파일로 시간만 바꾸면 되게 확장 가능.
    """
    hot = temp is not None and temp >= 30
    cold = temp is not None and temp <= 0

    if weather_main in ("Rain", "Drizzle", "Thunderstorm", "Snow"):
        # 비/눈/천둥 → 실내 루틴
        return (
            "☔️/❄️ 오늘은 바깥 날씨가 안 좋아! \n"
            "🏋️ 근력 10분 + 🧘 스트레칭 10분(실내) 추천!\n"
            "트레드밀이 있으면 가볍게 걷기 15분 추가도 굿."
        )

    if hot:
        return (
            "🥵 더운 날씨! 탈수 조심.\n"
            "🏃 달리기 20분(그늘 위주) + 🧘 스트레칭 10분 + 💪 근력 10분(가볍게)"
        )

    if cold:
        return (
            "🥶 추운 날씨! 준비운동 길게.\n"
            "🏃 달리기 20분(워밍업 충분히) + 🧘 스트레칭 10분 + 💪 근력 10분(실내)"
        )

    if weather_main == "Clear":
        return (
            "☀️ 맑은 날! \n"
            "🏃 달리기 30분 + 🧘 스트레칭 10분 + 💪 근력 10분 가자!"
        )

    # Clouds 등 기타
    return (
        "🌤️ 무난한 날씨!\n"
        "🏃 달리기 30분 + 🧘 스트레칭 10분 + 💪 근력 10분 추천!"
    )

from telegram import Update
from telegram.ext import ContextTypes

async def build_coach_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "안녕" in text:
        await update.message.reply_text("안녕하세요! 💪 운동할 준비 됐나요?")
    elif "운동" in text:
        await update.message.reply_text("좋아요! 오늘은 10분 스트레칭부터 시작해볼까요?")
    elif "날씨" in text:
        await update.message.reply_text("오늘 날씨가 어떤지 알려드릴까요? ☀️")
    else:
        await update.message.reply_text("음... 무슨 말인지 모르겠어요 😅\n'운동', '날씨', '위치' 중 하나로 말해보세요!")
