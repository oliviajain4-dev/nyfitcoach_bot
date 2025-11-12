# -------------------------------
# config/env.py
# -------------------------------
import os
from dotenv import load_dotenv, find_dotenv

# ✅ 1. .env 파일 자동 탐색
# find_dotenv()는 현재 폴더부터 상위로 올라가며 .env를 찾음
env_path = find_dotenv(filename=".env", raise_error_if_not_found=False)

# ✅ 2. .env 파일 로드
# override=False → 이미 로드된 환경변수는 덮어쓰지 않음
load_dotenv(dotenv_path=env_path, override=False)

# ✅ 3. 환경변수 확인 (선택적)
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# 로드된 키 목록 자동 감지
loaded = [k for k, v in {
    "BOT_TOKEN": BOT_TOKEN,
    "WEATHER_KEY": WEATHER_KEY,
    "YOUTUBE_API_KEY": YOUTUBE_API_KEY
}.items() if v]

if len(loaded) == 3:
    print(f"✅ .env 로드 성공 — {', '.join(loaded)} 인식 완료")
else:
    print(f"⚠️ [주의] .env 파일 로드 실패 또는 누락된 키 있음 → {', '.join(loaded)}만 감지됨")
