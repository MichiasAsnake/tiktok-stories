from database_helper import TikTokDatabase
import json

def export_dashboard_data():
    db = TikTokDatabase()
    dashboard_data = {
        "stats": db.get_video_stats(),
        "hashtags": db.get_trending_hashtags(20),
        "top_phrases": db.get_top_phrases(30),
        "top_comments": db.get_top_comments(10),
        "recent_videos": db.get_recent_videos(10)
    }
    with open("dashboard_data.json", "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    print("Exported dashboard_data.json")

if __name__ == "__main__":
    export_dashboard_data() 