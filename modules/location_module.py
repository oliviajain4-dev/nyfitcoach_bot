# 사용자별 도시를 메모리에 기억 (v1: 메모리, v2: 파일 저장으로 확장 예정)
user_city: dict[int, str] = {}

CLEAN_WORDS = ["여긴", "여기는", "사는 곳은", "도시는", "도시", "이야", "야", "입니다", "에요"]

def clean_city_text(text: str) -> str:
    s = text.strip()
    for w in CLEAN_WORDS:
        s = s.replace(w, "")
    return s.strip()

def set_city(user_id: int, text: str) -> str:
    city = clean_city_text(text)
    user_city[user_id] = city
    return city

def get_city(user_id: int) -> str | None:
    return user_city.get(user_id)
