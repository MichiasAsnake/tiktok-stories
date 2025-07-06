import asyncio
from datetime import datetime
from TikTokApi import TikTokApi
import os
from database_helper import TikTokDatabase

async def get_trending_data():
    # Get ms_token from environment variable
    ms_token = os.getenv("ms_token")
    if not ms_token:
        print("Error: MSTOKEN environment variable not set!")
        print("Please set your ms_token from TikTok cookies as an environment variable.")
        return
    
    # Initialize database
    db = TikTokDatabase()
    
    # Initialize the API
    api = TikTokApi()
    
    print("Type of api:", type(api))
    print("API object:", api)
    
    # Track statistics
    new_videos = 0
    existing_videos = 0
    new_comments = 0
    new_hashtags = 0

    try:
        # Create a session with ms_token
        print("Creating session with ms_token...")
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser="firefox", headless=False)
        print("Session created successfully!")
        
        # Get trending videos
        trending_videos = api.trending.videos(count=20)   # Start with 30 videos
        print("Type of trending_videos:", type(trending_videos))
        print("Trending videos object:", trending_videos)
        
        # Try to iterate through videos
        async for video in trending_videos:
            print(f"Video {new_videos + existing_videos + 1}:")
            print(f"  Video ID: {video.id}")
            print(f"  Video URL: {video.url}")
            print(f"  Author: {video.author.username if video.author else 'Unknown'}")
            print(f"  Stats: {video.stats}")
            
            # Debug: Check available attributes for covers and avatars
            print(f"  Available video attributes: {[attr for attr in dir(video) if not attr.startswith('_')]}")
            if video.author:
                print(f"  Available author attributes: {[attr for attr in dir(video.author) if not attr.startswith('_')]}")
            
            # Check if cover attributes exist
            if hasattr(video, 'dynamic_cover'):
                print(f"  Dynamic cover: {video.dynamic_cover}")
            if hasattr(video, 'cover'):
                print(f"  Cover: {video.cover}")
            if video.author and hasattr(video.author, 'avatarMedium'):
                print(f"  Author avatar: {video.author.avatarMedium}")
            
            # Check if video already exists
            if db.video_exists(video.id):
                print("  ⏭️ Video already exists in database")
                existing_videos += 1
                
                # Still get comments for existing videos (they might have new comments)
                existing_comment_count = db.get_video_comment_count(video.id)
                print(f"  📊 Already have {existing_comment_count} comments for this video")
                
                # Get additional comments
                print(f"  Getting additional comments...")
                comments = []
                comment_count = 0
                try:
                    async for comment in video.comments(count=10):  # Get fewer comments for existing videos
                        comment_data = {
                            'comment_id': comment.id,
                            'text': comment.text,
                            'author': comment.author.username if comment.author else 'Unknown',
                            'likes_count': comment.likes_count,
                            'create_time': None
                        }
                        comments.append(comment_data)
                        comment_count += 1
                        if comment_count >= 10:
                            break
                            
                except Exception as comment_error:
                    print(f"    Error getting comments: {comment_error}")
                
                # Insert new comments
                if comments:
                    comments_inserted = db.insert_comments(video.id, comments)
                    new_comments += comments_inserted
                    print(f"  💬 Added {comments_inserted} new comments")
                
            else:
                print("  🆕 New video - saving to database")
                
                # Get the full video data dictionary
                video_dict = video.as_dict
                
                # Extract author data
                author_dict = video_dict.get('author', {})
                
                # Prepare video data using correct field names
                video_data = {
                    'video_id': video.id,
                    'video_url': video.url,
                    'author': author_dict.get('uniqueId') or author_dict.get('nickname'),
                    'author_avatar_medium': author_dict.get('avatarMedium'),
                    'dynamic_cover': video_dict.get('video', {}).get('dynamicCover'),
                    'cover': video_dict.get('video', {}).get('cover'),
                    'stats': video.stats,
                    'create_time': str(video.create_time) if video.create_time else None
                }
                
                # Insert video into database
                if db.insert_video(video_data):
                    print("  ✅ Video saved to database")
                    new_videos += 1
                
                # Get hashtags for new videos
                hashtags = []
                if video.hashtags:
                    hashtags = [tag.name for tag in video.hashtags]
                    hashtags_inserted = db.insert_hashtags(video.id, hashtags)
                    new_hashtags += hashtags_inserted
                    print(f"  🏷️ {hashtags_inserted} hashtags saved")
                
                # Get comments for new videos
                print(f"  Getting comments...")
                comments = []
                comment_count = 0
                try:
                    async for comment in video.comments(count=20):
                        print(f"    Comment {comment_count + 1}: {comment.text}")
                        print(f"      Author: {comment.author.username if comment.author else 'Unknown'}")
                        print(f"      Likes: {comment.likes_count}")
                        
                        # Prepare comment data
                        comment_data = {
                            'comment_id': comment.id,
                            'text': comment.text,
                            'author': comment.author.username if comment.author else 'Unknown',
                            'likes_count': comment.likes_count,
                            'create_time': None  # Comment objects don't have create_time
                        }
                        comments.append(comment_data)
                        
                        comment_count += 1
                        if comment_count >= 20:
                            break
                            
                except Exception as comment_error:
                    print(f"    Error getting comments: {comment_error}")
                
                # Insert comments into database
                if comments:
                    comments_inserted = db.insert_comments(video.id, comments)
                    new_comments += comments_inserted
                    print(f"  💬 {comments_inserted} comments saved to database")
            
            print("---")
            
            if (new_videos + existing_videos) >= 40:
                break
        
        # Print final statistics
        print(f"\n📊 Data Collection Complete!")
        print(f"🆕 New videos collected: {new_videos}")
        print(f"⏭️ Existing videos skipped: {existing_videos}")
        print(f"💬 New comments collected: {new_comments}")
        print(f"🏷️ New hashtags collected: {new_hashtags}")
        
        # Show database statistics
        stats = db.get_video_stats()
        print(f"\n📈 Database Statistics:")
        print(f"   Total videos in DB: {stats.get('total_videos', 0)}")
        print(f"   Total comments in DB: {stats.get('total_comments', 0)}")
        print(f"   Total hashtags in DB: {stats.get('total_hashtags', 0)}")
        print(f"   Avg likes per video: {stats.get('avg_likes_per_video', 0)}")
        print(f"   Avg comments per video: {stats.get('avg_comments_per_video', 0)}")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {str(e)}")

if __name__ == "__main__":
    asyncio.run(get_trending_data())

