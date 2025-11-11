# -------------------------------
# modules/user_module.py
# -------------------------------
import json
import os

DATA_PATH = "data/users.json"
os.makedirs("data", exist_ok=True)

# ✅ 1️⃣ 데이터 로드
def load_data():
    """users.json 파일을 읽어 딕셔너리로 반환"""
    if not os.path.exists(DATA_PATH):
        return {}
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

# ✅ 2️⃣ 데이터 저장
def save_data(data):
    """데이터를 users.json 파일에 저장"""
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ✅ 3️⃣ 유저 생성 또는 가져오기
def get_user(user_id):
    """user_id가 없으면 새로 생성하고 반환"""
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "name": None,
            "location": None,
            "exercise": None,
            "notify_time": None,
            "tone": "friendly"
        }
        save_data(data)
    return data[user_id]

# ✅ 4️⃣ 유저 정보 업데이트
def update_user(user_id, key, value):
    """특정 key의 값을 업데이트"""
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        get_user(user_id)
        data = load_data()
    data[user_id][key] = value
    save_data(data)

# ✅ 5️⃣ 유저 정보 조회
def get_user_data(user_id, key=None):
    """user_id 또는 all로 전체 데이터 반환"""
    data = load_data()
    if user_id == "all":
        return data
    user = data.get(str(user_id), {})
    return user.get(key) if key else user
