# -------------------------------
# modules/youtube_module.py
# -------------------------------
import os, requests, random

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# ✅ 카테고리별 검색 키워드
YOUTUBE_KEYWORDS = {
    "상체": ["상체운동", "팔운동", "어깨운동"],
    "하체": ["하체운동", "스쿼트", "엉덩이운동"],
    "코어": ["복근운동", "코어운동", "플랭크"],
    "유산소": ["유산소운동", "홈트유산소", "살빼는운동"],
    "스트레칭": ["전신스트레칭", "아침스트레칭", "저녁스트레칭"],
    "요가": ["요가", "홈요가", "다이어트요가"],
    "전신": ["전신운동", "다이어트운동", "홈트전신"],
    "기타": ["홈트레이닝", "건강운동", "다이어트운동"]
}

# ✅ fallback 기본 추천 영상 (API 오류 시)
FALLBACK_VIDEOS = [
    {
        "title": "전신 스트레칭 20분 루틴 💪",
        "link": "https://www.youtube.com/watch?v=RjEy8v2UB1U",
        "thumbnail": "https://img.youtube.com/vi/RjEy8v2UB1U/hqdefault.jpg"
    },
    {
        "title": "요가로 하루 마무리 🌿",
        "link": "https://www.youtube.com/watch?v=Q7Fz1I2f7lA",
        "thumbnail": "https://img.youtube.com/vi/Q7Fz1I2f7lA/hqdefault.jpg"
    }
]

def fetch_youtube_videos(category="전신", max_results=15):
    """카테고리별 실시간 유튜브 인기 영상 가져오기"""
    keyword = random.choice(YOUTUBE_KEYWORDS.get(category, ["홈트"]))
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&maxResults={max_results}"
        f"&q={keyword}&regionCode=KR&type=video&order=viewCount"
        f"&key={YOUTUBE_API_KEY}"
    )
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json().get("items", [])
        videos = []
        for item in data:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            thumb = item["snippet"]["thumbnails"]["medium"]["url"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            videos.append({
                "title": title,
                "link": link,
                "thumbnail": thumb
            })
        return videos or FALLBACK_VIDEOS
    except Exception as e:
        print(f"[YouTube] API Error: {e}")
        return FALLBACK_VIDEOS

def get_random_video(category="전신"):
    """카테고리 랜덤 추천"""
    videos = fetch_youtube_videos(category)
    if not videos:
        return random.choice(FALLBACK_VIDEOS)
    return random.choice(videos)
