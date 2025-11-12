# -------------------------------
# NYFITCOACH_BOT/server_app.py
# -------------------------------
import os
import asyncio
import logging
import json
from datetime import datetime, date
import nest_asyncio
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from main import main  # 👈 텔레그램 봇 실행 함수 (_main.py 이름이 main.py로 되어 있음)

# ==============================
# 1️⃣ 환경 설정 및 로그 포맷
# ==============================
load_dotenv()              
nest_asyncio.apply()        

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("NYFitCoach")

# ==============================
# 2️⃣ FastAPI 기본 설정
# ==============================
app = FastAPI(
    title="🏃‍♀️ NY FitCoach Server",
    description="FastAPI + Telegram Bot integrated server (Render optimized + admin monitor)",
    version="1.5.0"
)

# ==============================
# 3️⃣ 글로벌 상태 관리
# ==============================
START_TIME = datetime.now()
BOT_STATUS = {"running": False, "last_check": None, "users": 0}
LAST_USER_COUNT = 0

ADMIN_ID = os.getenv("ADMIN_ID")  # 👈 너의 텔레그램 ID (봇이 관리자에게 알림 전송)
BOT_TOKEN = os.getenv("BOT_TOKEN")


# ==============================
# 4️⃣ 데이터 로드 유틸
# ==============================
def get_user_data():
    """data/users.json을 읽어서 (유저수, 유저이름리스트, 오늘활성유저수) 반환"""
    path = os.path.join("data", "users.json")
    if not os.path.exists(path):
        return 0, [], 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return 0, [], 0

        users = list(data.keys())
        today_str = date.today().isoformat()
        today_active = 0

        # 각 유저의 마지막 활동일자 계산
        for user_id, user_info in data.items():
            last_time = user_info.get("last_active") or user_info.get("updated_at")
            if last_time and str(last_time).startswith(today_str):
                today_active += 1

        return len(users), users, today_active

    except Exception as e:
        logger.error(f"❌ 사용자 데이터 로드 오류: {e}")
        return 0, [], 0


def send_admin_alert(message: str):
    """관리자에게 텔레그램 알림 전송"""
    if not (BOT_TOKEN and ADMIN_ID):
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": ADMIN_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        logger.error(f"⚠️ 관리자 알림 실패: {e}")


def log_user_change():
    """유저 수가 변하면 로그 + 관리자 알림"""
    global LAST_USER_COUNT
    count, users, _ = get_user_data()
    if count != LAST_USER_COUNT:
        diff = count - LAST_USER_COUNT
        if diff > 0:
            msg = f"🟢 새로운 유저 {diff}명 추가됨 (총 {count}명)"
            logger.info(msg)
            send_admin_alert(f"[NYFitCoach 알림]\n{msg}\n최근 가입자: {users[-1] if users else '알 수 없음'}")
        elif diff < 0:
            msg = f"🔴 유저 {abs(diff)}명 감소 (현재 {count}명)"
            logger.warning(msg)
            send_admin_alert(f"[NYFitCoach 알림]\n{msg}")
        LAST_USER_COUNT = count


# ==============================
# 5️⃣ API 엔드포인트
# ==============================
@app.get("/")
async def root():
    """Render 상태 체크용 기본 경로"""
    uptime = datetime.now() - START_TIME
    user_count, users, today_active = get_user_data()
    return {
        "message": "🏃‍♀️ NY FitCoach Server is running!",
        "uptime": str(uptime).split('.')[0],
        "bot_status": "active" if BOT_STATUS["running"] else "inactive",
        "registered_users": user_count,
        "today_active_users": today_active,
        "recent_users": users[-3:] if users else []
    }


@app.get("/health")
async def health_check():
    """Render 헬스체크 엔드포인트"""
    log_user_change()
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/info")
async def info():
    """서버 상태 전체 요약"""
    uptime = datetime.now() - START_TIME
    user_count, users, today_active = get_user_data()
    return {
        "version": "1.5.0",
        "uptime": str(uptime).split('.')[0],
        "telegram_bot": BOT_STATUS,
        "env_loaded": {
            "BOT_TOKEN": bool(os.getenv("BOT_TOKEN")),
            "WEATHER_KEY": bool(os.getenv("WEATHER_KEY")),
            "ADMIN_ID": bool(ADMIN_ID),
        },
        "registered_users": user_count,
        "today_active_users": today_active,
        "recent_users": users[-3:] if users else []
    }


# ==============================
# 6️⃣ 서버 이벤트
# ==============================
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 텔레그램 봇 실행"""
    logger.info("🚀 FastAPI 서버 시작됨 — 텔레그램 봇 실행 중...")
    try:
        BOT_STATUS["running"] = True
        BOT_STATUS["last_check"] = datetime.now().isoformat()

        user_count, _, today_active = get_user_data()
        BOT_STATUS["users"] = user_count
        global LAST_USER_COUNT
        LAST_USER_COUNT = user_count

        asyncio.create_task(main())
        logger.info(f"✅ 현재 등록된 사용자 수: {user_count}명 (오늘 활성: {today_active}명)")
        send_admin_alert(f"✅ NYFitCoach 서버 시작됨!\n총 유저: {user_count}명\n오늘 활성: {today_active}명")
    except Exception as e:
        BOT_STATUS["running"] = False
        logger.error(f"❌ 텔레그램 봇 실행 오류: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 로그"""
    logger.warning("🛑 서버 종료됨. Telegram 봇 세션 종료 중...")
    send_admin_alert("⚠️ NYFitCoach 서버가 종료되었습니다.")


@app.get("/status")
async def bot_status():
    """현재 봇 상태 및 사용자 수 실시간 확인"""
    uptime = datetime.now() - START_TIME
    user_count, users, today_active = get_user_data()
    return {
        "bot_running": BOT_STATUS["running"],
        "last_check": BOT_STATUS["last_check"],
        "registered_users": user_count,
        "today_active_users": today_active,
        "recent_users": users[-3:] if users else [],
        "uptime": str(uptime).split('.')[0]
    }
