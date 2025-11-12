# -------------------------------
# NYFITCOACH_BOT/web_app.py
# -------------------------------
import os
import json
import random
from datetime import datetime
import streamlit as st

# ====== 모듈 가져오기 ======
from modules.user_module import get_user, update_user, get_user_data
from modules.weather_module import get_weather
from modules.coach_module import build_coach_message

# ====== 데이터 경로 ======
USER_DATA_PATH = os.path.join("data", "users.json")
os.makedirs("data", exist_ok=True)

# ====== 유튜브 카테고리 ======
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
    links = YOUTUBE_HOME_TRAINING.get(category, [])
    return random.choice(links) if links else random.choice(sum(YOUTUBE_HOME_TRAINING.values(), []))

# ====== 대화 기록 저장 ======
def save_chat(user_name, role, text):
    history_path = os.path.join("data", f"chat_{user_name}.json")
    data = []
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    data.append({"time": datetime.now().isoformat(), "role": role, "text": text})
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

def load_chat(user_name):
    path = os.path.join("data", f"chat_{user_name}.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ====== UI 시작 ======
st.set_page_config(page_title="NY FitCoach Bot", page_icon="💪", layout="centered")

st.markdown("<h2 style='text-align:center;'>🏃‍♀️ NY FitCoach Web Chatbot 💬</h2>", unsafe_allow_html=True)

# ====== 이름 입력 ======
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

if not st.session_state["user_name"]:
    name_input = st.text_input("이름을 입력하세요 ✨", key="name_input")
    if st.button("시작하기"):
        if name_input.strip():
            st.session_state["user_name"] = name_input.strip()
            get_user(name_input)
            st.rerun()
else:
    user_name = st.session_state["user_name"]
    st.success(f"{user_name}님, 환영합니다! 🎉")

    # ====== 대화 기록 ======
    chat_history = load_chat(user_name)
    for msg in chat_history:
        role = msg["role"]
        text = msg["text"]
        color = "#DCF8C6" if role == "user" else "#E6E6FA"
        align = "right" if role == "user" else "left"
        st.markdown(
            f"<div style='text-align:{align}; background:{color}; padding:10px; border-radius:15px; margin:5px;'>{text}</div>",
            unsafe_allow_html=True
        )

    # ====== 입력창 ======
    user_input = st.text_input("메시지를 입력하세요 💬", key="chat_input")

    if st.button("보내기"):
        if user_input.strip():
            save_chat(user_name, "user", user_input)
            # ---- 챗봇 응답 로직 ----
            lower = user_input.lower()
            if "홈트" in lower:
                bot_reply = "홈트 카테고리를 골라줘 💪 상체 / 하체 / 코어 / 유산소 / 스트레칭 / 요가 중에서!"
            elif any(k in lower for k in YOUTUBE_HOME_TRAINING.keys()):
                key = next((k for k in YOUTUBE_HOME_TRAINING if k in lower), None)
                link = random_youtube_link(key)
                bot_reply = f"🎥 {key} 추천 영상!\n👉 {link}"
            elif "날씨" in lower:
                bot_reply = "☀️ 날씨 기능은 텔레그램 버전에서 작동 중이에요!"
            else:
                bot_reply = random.choice([
                    "좋아요! 계속해볼까요? 💪", "멋져요 😎", "지금 페이스 좋아요 🔥"
                ])
            save_chat(user_name, "bot", bot_reply)
            st.rerun()

    # ====== 초기화 버튼 ======
    if st.button("대화 초기화"):
        os.remove(os.path.join("data", f"chat_{user_name}.json"))
        st.experimental_rerun()

st.markdown("<hr><p style='text-align:center;color:gray;'>© 2025 NYFitCoach WebBot</p>", unsafe_allow_html=True)
