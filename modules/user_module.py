# modules/user_module.py
# NYFITCOACH_BOT 2025 - USER MODULE (Full Upgrade Ver.)
# 기능: 사용자 정보 / 루틴 / 알림 / 즐겨찾기 / 히스토리 관리
# 특징: 자동갱신 + 데이터보존 + 안전저장
import os, json, re
from datetime import datetime
from typing import Dict, Any, List, Optional

# ===== 경로 설정 =====
DATA_DIR = "data"
USERS_DB = os.path.join(DATA_DIR, "users.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ===== 내부 기본 함수 =====
def _read_db() -> Dict[str, Any]:
    """DB 로드 (없으면 자동 생성)."""
    if not os.path.exists(USERS_DB):
        with open(USERS_DB, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    try:
        with open(USERS_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def _write_db(db: Dict[str, Any]) -> None:
    """안전하게 DB 저장 (임시파일 후 교체)."""
    tmp = USERS_DB + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USERS_DB)

# ===== 기본 데이터 구조 =====
WEEKDAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
TONE_CHOICES = {"friendly","coach","healing"}

def _default_user(user_id: int) -> Dict[str, Any]:
    """새 유저 기본값"""
    return {
        "user_id": user_id,
        "name": None,
        "age": None,
        "location": "서울",
        "temp_limit": 5,
        "tone": "friendly",
        "favorites": [],
        "notifications": {
            "weather_only": {"enabled": True,  "time": "06:30"},
            "combo":        {"enabled": False, "time": None, "days": ["Mon","Tue","Wed","Thu","Fri"]},
            "workout_only": {"enabled": False, "time": None},
            "none": False
        },
        "routine": {wd: [] for wd in WEEKDAYS},
        "last_activity": None,
        "history": [],
        "usage_stats": {},
    }

# ===== 자동 갱신 엔진 =====
def _auto_update_structure(u: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """누락된 필드 자동 추가 (기존 데이터 손상 없이 갱신)."""
    base = _default_user(user_id)
    for key, val in base.items():
        if key not in u:
            u[key] = val  # 누락된 필드 새로 추가
        elif isinstance(val, dict):
            # 하위 dict도 자동 갱신 (예: notifications)
            for subkey, subval in val.items():
                if subkey not in u[key]:
                    u[key][subkey] = subval
    return u

# ===== 메인 CRUD =====
def load_data() -> Dict[str, Any]:
    return _read_db()

def get_user(user_id: int) -> Dict[str, Any]:
    """유저 불러오기 + 없으면 생성 + 자동 구조갱신"""
    db = _read_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = _default_user(user_id)
    else:
        db[uid] = _auto_update_structure(db[uid], user_id)
    _write_db(db)
    return db[uid]

def update_user(user_id: int, key: str, value: Any) -> Dict[str, Any]:
    """특정 key 업데이트"""
    db = _read_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = _default_user(user_id)
    db[uid][key] = value
    db[uid] = _auto_update_structure(db[uid], user_id)
    _write_db(db)
    return db[uid]

def get_user_data(user_id: int, key: Optional[str] = None) -> Any:
    u = get_user(user_id)
    return u if key is None else u.get(key)

# ===== 유틸 =====
TIME_24H_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
def is_valid_time_24h(t: str) -> bool:
    return bool(TIME_24H_PATTERN.match(t or ""))

def normalize_weekday(wd: str) -> str:
    mapping = {
        "mon":"Mon","monday":"Mon","월":"Mon","월요일":"Mon",
        "tue":"Tue","tuesday":"Tue","화":"Tue","화요일":"Tue",
        "wed":"Wed","wednesday":"Wed","수":"Wed","수요일":"Wed",
        "thu":"Thu","thursday":"Thu","목":"Thu","목요일":"Thu",
        "fri":"Fri","friday":"Fri","금":"Fri","금요일":"Fri",
        "sat":"Sat","saturday":"Sat","토":"Sat","토요일":"Sat",
        "sun":"Sun","sunday":"Sun","일":"Sun","일요일":"Sun",
    }
    return mapping.get(wd.lower(), "Mon")

def _weekday_kr(wd: str) -> str:
    return {"Mon":"월","Tue":"화","Wed":"수","Thu":"목","Fri":"금","Sat":"토","Sun":"일"}[wd]

# ===== 설정 요약 =====
def build_settings_summary(user_id: int) -> str:
    u = get_user(user_id)
    n = u["notifications"]
    def onoff(v): return "ON" if v else "OFF"
    # 루틴 요약
    r_txt = []
    for wd in WEEKDAYS:
        acts = u["routine"].get(wd, [])
        if not acts:
            r_txt.append(f"{_weekday_kr(wd)}: (없음)")
        else:
            pretty = ", ".join(
                f"{a['type']}({a.get('minutes','-')}분)" if a.get('minutes') else a['type']
                for a in acts
            )
            r_txt.append(f"{_weekday_kr(wd)}: {pretty}")
    routine_block = "\n".join(r_txt)

    return (
        "⚙️ [설정탭] – 나연님의 정보\n"
        f"👤 이름/나이: {u.get('name') or '-'} / {u.get('age') or '-'}\n"
        f"📍 지역: {u.get('location')}\n"
        f"🌡 실외 허용온도: {u.get('temp_limit')}°C\n"
        f"🗣 말투: {u.get('tone')}\n"
        f"⭐️ 즐겨찾기: {', '.join(u.get('favorites') or []) or '(없음)'}\n\n"
        "⏰ 알림 설정\n"
        f"• 날씨 전용: {onoff(n['weather_only']['enabled'])} ({n['weather_only']['time'] or '-'})\n"
        f"• 날씨+운동: {onoff(n['combo']['enabled'])} ({n['combo']['time'] or '-'}, {','.join(n['combo'].get('days',[])) or '-'})\n"
        f"• 운동만 알림: {onoff(n['workout_only']['enabled'])} ({n['workout_only']['time'] or '-'})\n"
        f"• 알림 없음: {'ON' if n['none'] else 'OFF'}\n\n"
        "📅 요일별 루틴\n" + routine_block
    )

# ===== 기본정보 설정 =====
def set_basic_profile(user_id: int, **kwargs) -> Dict[str, Any]:
    db = _read_db()
    uid = str(user_id)
    u = db.get(uid, _default_user(user_id))
    for k, v in kwargs.items():
        if k == "tone" and v not in TONE_CHOICES:
            continue
        if k == "temp_limit":
            v = int(v)
        u[k] = v
    db[uid] = _auto_update_structure(u, user_id)
    _write_db(db)
    return db[uid]

# ===== 즐겨찾기 =====
def update_favorites(user_id: int, favs: List[str]) -> List[str]:
    db = _read_db()
    uid = str(user_id)
    u = db.get(uid, _default_user(user_id))
    new = []
    for f in favs:
        f = f.strip()
        if f and f not in new:
            new.append(f)
    u["favorites"] = new[:20]
    db[uid] = _auto_update_structure(u, user_id)
    _write_db(db)
    return new

# ===== 루틴 =====
def update_routine(user_id: int, weekday: str, new_routine: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    db = _read_db()
    uid = str(user_id)
    u = db.get(uid, _default_user(user_id))
    wd = normalize_weekday(weekday)
    u["routine"][wd] = [{"type": i["type"], **({"minutes": int(i["minutes"])} if "minutes" in i else {})} for i in new_routine]
    db[uid] = _auto_update_structure(u, user_id)
    _write_db(db)
    return u["routine"][wd]

# ===== 알림 =====
def update_notification(user_id: int, ntype: str, time: Optional[str]=None,
                        enabled: Optional[bool]=None, days: Optional[List[str]]=None):
    db = _read_db()
    uid = str(user_id)
    u = db.get(uid, _default_user(user_id))
    notif = u["notifications"].get(ntype, {})
    if time is not None:
        if time == "" or time is False:
            notif["time"] = None
            notif["enabled"] = False
        elif is_valid_time_24h(time):
            notif["time"] = time
            notif["enabled"] = True
    if enabled is not None:
        notif["enabled"] = enabled
    if days is not None:
        notif["days"] = [normalize_weekday(d) for d in days]
    u["notifications"][ntype] = notif
    u = _auto_update_structure(u, user_id)
    db[uid] = u
    _write_db(db)
    return notif

def toggle_notifications(user_id: int, mode: str):
    db = _read_db()
    uid = str(user_id)
    u = db.get(uid, _default_user(user_id))
    if mode == "none_on":
        u["notifications"]["none"] = True
        for k in ("weather_only","combo","workout_only"):
            u["notifications"][k]["enabled"] = False
    else:
        u["notifications"]["none"] = False
    db[uid] = _auto_update_structure(u, user_id)
    _write_db(db)
    return u["notifications"]

# ===== 기록 =====
def record_activity(user_id: int, activity: str, duration: Optional[int]=None):
    db = _read_db()
    uid = str(user_id)
    u = db.get(uid, _default_user(user_id))
    date = datetime.now().strftime("%Y-%m-%d")
    rec = {"date": date, "type": activity}
    if duration:
        rec["duration"] = int(duration)
    u["last_activity"] = rec
    u["history"].append(rec)
    u["usage_stats"][activity] = u["usage_stats"].get(activity, 0) + 1
    db[uid] = _auto_update_structure(u, user_id)
    _write_db(db)
    return rec

# ===== 톤 =====
def set_tone(user_id: int, tone: str) -> str:
    if tone not in TONE_CHOICES:
        raise ValueError("tone은 friendly/coach/healing 중 하나여야 해요.")
    update_user(user_id, "tone", tone)
    return tone
