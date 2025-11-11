# -------------------------------
# config/version.py
# -------------------------------
import datetime

# ✅ 프로젝트 버전
__version__ = "1.0.0"
__updated__ = datetime.date.today().strftime("%Y-%m-%d")

# ✅ 간단한 변경 이력 (나중에 확장 가능)
CHANGE_LOG = {
    "1.0.0": "⚙️ 완전체 구조 확립 — config/env.py 기반 한 곳 수정형",
    "0.3.3": "🧩 기억형 + 알림형 통합 구조",
    "0.2.x": "📦 모듈 분리 및 weather_module 안정화",
}

# ✅ 버전 출력 함수
def show_version(detail: bool = False):
    """
    현재 버전 정보를 출력.
    detail=True 시 변경 이력까지 표시.
    """
    print(f"🧭 NYFITCOACH BOT — Version {__version__} (Updated: {__updated__})")
    if detail and __version__ in CHANGE_LOG:
        print(f"📜 Changelog: {CHANGE_LOG[__version__]}")

if __name__ == "__main__":
    show_version(detail=True)
