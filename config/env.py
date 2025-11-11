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

if BOT_TOKEN and WEATHER_KEY:
    print(f"✅ .env 로드 성공 — BOT_TOKEN, WEATHER_KEY 인식 완료")
else:
    print("⚠️ [주의] .env 파일 로드 실패! 경로 또는 변수명 확인 필요.")
