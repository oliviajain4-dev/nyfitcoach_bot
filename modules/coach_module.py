# -------------------------------
# modules/coach_module.py
# NYFITCOACH_BOT 2025 - Tone + Weather + Routine Feedback + Condition Tracker
# -------------------------------
import random
from datetime import datetime

def build_coach_message(
    tone: str,
    weather_main: str,
    temp: float,
    is_outdoor: bool,
    did_exercise_yesterday: bool = None,
    condition: str = None
) -> str:
    """
    🌤️ 톤 + 날씨 + 운동상황 + 컨디션 기반 코멘트 생성
    tone: 'friendly' | 'coach' | 'healing'
    weather_main: 'Clear', 'Rain', 'Snow' 등
    temp: 현재 온도
    is_outdoor: 실외운동 가능 여부
    did_exercise_yesterday: 어제 운동 여부 (None=모름)
    condition: '좋음' | '보통' | '피곤'
    """

    hot = temp is not None and temp >= 30
    cold = temp is not None and temp <= 0

    # ===== 톤별 문장 Pool =====
    friendly_pool = {
        "intro": [
            "오늘 기분 어때? ☀️", "좋은 하루야~ 운동 가자 💕",
            "오늘도 화이팅 나연이!", "너무 덥지 않지? 물 자주 마셔야 해 💧"
        ],
        "motivate": [
            "조금만 해도 몸이 개운해질 거야!", "네 페이스 좋아! 천천히 꾸준히!",
            "오늘은 꾸준함으로 승부하자 🔥"
        ],
        "rest": [
            "오늘은 몸이 좀 피곤하면 스트레칭만 해도 좋아 🌿", 
            "쉼도 운동의 일부야 ☁️", "가벼운 산책도 충분해 ☺️"
        ]
    }

    coach_pool = {
        "intro": [
            "컨디션 점검 완료 💪", "루틴 점검 시작! 오늘도 집중하자 ⚡️",
            "지금이 바로 운동 타임이야!"
        ],
        "motivate": [
            "폼 체크 잊지 말고, 정확하게!", "좋아, 지금 리듬 유지!", 
            "오늘 루틴 완벽하게 가자 👊"
        ],
        "rest": [
            "휴식도 훈련의 일부야. 몸 상태 봐서 강약 조절!",
            "가볍게 유산소로 마무리해도 좋아."
        ]
    }

    healing_pool = {
        "intro": [
            "오늘도 잘 버텨줘서 고마워 🌷", "괜찮아, 오늘은 느리게 가도 돼 ☁️",
            "햇살이 따뜻하네. 잠깐 숨 돌리자 🌿"
        ],
        "motivate": [
            "조급해하지 말고, 네 속도로 가면 돼 🌱", "지금도 충분히 잘하고 있어 💜",
            "작은 움직임 하나도 의미 있어 🌸"
        ],
        "rest": [
            "오늘은 스스로를 돌보는 날이야 🩵", "스트레칭만 살짝 해도 괜찮아 🌙"
        ]
    }

    tone_pool = {"friendly": friendly_pool, "coach": coach_pool, "healing": healing_pool}.get(tone, friendly_pool)

    # ===== 날씨 기반 문장 =====
    if weather_main in ("Rain", "Drizzle", "Thunderstorm", "Snow"):
        weather_line = "☔ 오늘은 바깥이 안 좋아요! 실내 루틴으로 가자 🏠"
    elif hot:
        weather_line = "🥵 날이 덥다! 수분 꼭 챙기고, 그늘 위주로 하자 🌤️"
    elif cold:
        weather_line = "🥶 추운 날씨네! 워밍업을 충분히 하고 시작하자 🔥"
    elif weather_main == "Clear":
        weather_line = "☀️ 맑은 날씨야! 밖에서 운동하면 기분 최고일 거야 😎"
    else:
        weather_line = "🌤️ 무난한 날씨네. 오늘도 네 루틴 지켜보자 💪"

    # ===== 어제 운동 여부 =====
    if did_exercise_yesterday is None:
        activity_line = "어제 운동했어? 😊 했으면 꾸준함 최고야, 안 했다면 오늘 시작해보자!"
    elif did_exercise_yesterday:
        activity_line = "어제도 운동했네! 대단해 👏 오늘은 강도 살짝 조절해서 가자."
    else:
        activity_line = "어제는 쉬었네 🌿 오늘은 가볍게 몸을 풀어볼까?"

    # ===== 컨디션 분석 =====
    if condition == "좋음":
        condition_line = "컨디션 최고네! 오늘은 조금 더 힘내보자 💪"
    elif condition == "보통":
        condition_line = "무리하지 말고, 네 페이스대로 가자 🌼"
    elif condition == "피곤":
        condition_line = "피곤하다면 스트레칭 위주로만 하자 ☁️"
    else:
        condition_line = "오늘 몸 상태는 어때? 🌤️ 네 컨디션에 맞게 루틴 조절해볼까?"

    # ===== 실내/실외 선택 =====
    env_line = "🏠 오늘은 실내 운동 위주로!" if not is_outdoor else "🚴‍♀️ 바깥공기 마시면서 달려보자!"

    # ===== 문장 랜덤 선택 =====
    intro = random.choice(tone_pool["intro"])
    motivate = random.choice(tone_pool["motivate"])
    rest = random.choice(tone_pool["rest"])

    # ===== 최종 조합 =====
    if tone == "healing":
        final_message = f"{intro}\n{weather_line}\n{condition_line}\n{rest}"
    elif tone == "coach":
        final_message = f"{intro}\n{weather_line}\n{condition_line}\n{env_line}\n{motivate}"
    else:
        final_message = f"{intro}\n{weather_line}\n{activity_line}\n{condition_line}\n{motivate}"

    return final_message
1m1