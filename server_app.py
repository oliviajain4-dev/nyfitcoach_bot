# -------------------------------
# NYFITCOACH_BOT/server_app.py
# -------------------------------
import os
import asyncio
import logging
import nest_asyncio
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from main import main  # 👈 네 텔레그램 봇 메인 함수 가져옴 (_main.py 이름이 main.py로 되어있음)

# ==============================
# 1️⃣ 환경 설정 및 로그 포맷
# ==============================
load_dotenv()  # .env 자동 로드
nest_asyncio.apply()  # asyncio 루프 충돌 방지

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("NYFitCoach")

# ==============================
# 2️⃣ FastAPI 서버 기본 설정
# ==============================
app = FastAPI(
    title="🏃‍♀️ NY FitCoach Server",
    description="FastAPI + Telegram Bot integrated server (Render optimized)",
    version="1.2.0"
)

# 서버 시작 시간 기록
START_TIME = datetime.now()
BOT_STATUS = {"running": False, "last_check": None, "users": 0}


# ==============================
# 3️⃣ 기본 경로들
# ==============================
@app.get("/")
async def root():
    """Render 상태 체크용 기본 경로"""
    uptime = datetime.now() - START_TIME
    return {
        "message": "🏃‍♀️ NY FitCoach Server is running!",
        "uptime": str(uptime).split('.')[0],
        "bot_status": "active" if BOT_STATUS["running"] else "inactive",
    }


@app.get("/health")
async def health_check():
    """Render 헬스체크 엔드포인트"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/info")
async def info():
    """서버 정보 + 환경 변수 로드 확인"""
    uptime = datetime.now() - START_TIME
    return {
        "version": "1.2.0",
        "uptime": str(uptime).split('.')[0],
        "telegram_bot": BOT_STATUS,
        "env_loaded": {
            "BOT_TOKEN": bool(os.getenv("BOT_TOKEN")),
            "WEATHER_KEY": bool(os.getenv("WEATHER_KEY")),
        },
    }


# ==============================
# 4️⃣ 텔레그램 봇 실행 (비동기)
# ==============================
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 텔레그램 봇 병행 실행"""
    logger.info("🚀 FastAPI 서버 시작됨 — 텔레그램 봇 실행 중...")
    try:
        BOT_STATUS["running"] = True
        BOT_STATUS["last_check"] = datetime.now().isoformat()
        asyncio.create_task(main())
    except Exception as e:
        BOT_STATUS["running"] = False
        logger.error(f"❌ 텔레그램 봇 실행 오류: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 로그"""
    logger.warning("🛑 서버 종료됨. Telegram 봇 세션 종료 중...")


# ==============================
# 5️⃣ 추가 유틸 (선택 기능)
# ==============================
@app.get("/status")
async def bot_status():
    """현재 봇 상태 실시간 확인"""
    uptime = datetime.now() - START_TIME
    return {
        "bot_running": BOT_STATUS["running"],
        "last_check": BOT_STATUS["last_check"],
        "uptime": str(uptime).split('.')[0]
    }
