#!/usr/bin/env python3
"""
Script to run multiple TikTok data collection sessions
This helps build up your database over time without duplicates
"""

import asyncio
import time
from datetime import datetime
from comments import get_trending_data
from database_helper import TikTokDatabase

async def run_collection_session(session_number: int = 1):
    """Run a single data collection session"""
    print(f"\n{'='*60}")
    print(f"🚀 Starting Data Collection Session #{session_number}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Show current database stats before collection
    db = TikTokDatabase()
    stats_before = db.get_video_stats()
    print(f"\n📊 Database Stats Before Collection:")
    print(f"   Videos: {stats_before.get('total_videos', 0)}")
    print(f"   Comments: {stats_before.get('total_comments', 0)}")
    print(f"   Hashtags: {stats_before.get('total_hashtags', 0)}")
    
    # Run the data collection
    start_time = time.time()
    await get_trending_data()
    end_time = time.time()
    
    # Show updated database stats
    stats_after = db.get_video_stats()
    print(f"\n📊 Database Stats After Collection:")
    print(f"   Videos: {stats_after.get('total_videos', 0)} (+{stats_after.get('total_videos', 0) - stats_before.get('total_videos', 0)})")
    print(f"   Comments: {stats_after.get('total_comments', 0)} (+{stats_after.get('total_comments', 0) - stats_before.get('total_comments', 0)})")
    print(f"   Hashtags: {stats_after.get('total_hashtags', 0)} (+{stats_after.get('total_hashtags', 0) - stats_before.get('total_hashtags', 0)})")
    
    print(f"\n⏱️ Session completed in {end_time - start_time:.2f} seconds")
    print(f"{'='*60}")

async def run_multiple_sessions(num_sessions: int = 3, delay_minutes: int = 30):
    """Run multiple data collection sessions with delays"""
    print(f"🎯 Running {num_sessions} data collection sessions")
    print(f"⏰ Delay between sessions: {delay_minutes} minutes")
    
    for session in range(1, num_sessions + 1):
        await run_collection_session(session)
        
        if session < num_sessions:
            print(f"\n⏳ Waiting {delay_minutes} minutes before next session...")
            await asyncio.sleep(delay_minutes * 60)
    
    print(f"\n✅ All {num_sessions} sessions completed!")

def main():
    """Main function to run data collection"""
    print("🎬 TikTok Data Collection Manager")
    print("=" * 40)
    
    # Get user input
    try:
        choice = input("Choose an option:\n1. Run single session\n2. Run multiple sessions\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            asyncio.run(run_collection_session(1))
            
        elif choice == "2":
            num_sessions = int(input("Number of sessions to run (default 3): ") or "3")
            delay_minutes = int(input("Delay between sessions in minutes (default 30): ") or "30")
            asyncio.run(run_multiple_sessions(num_sessions, delay_minutes))
            
        else:
            print("Invalid choice. Running single session...")
            asyncio.run(run_collection_session(1))
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Data collection interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 