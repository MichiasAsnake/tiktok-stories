import asyncio
import json
from TikTokApi import TikTokApi
import os

async def get_trending_data():
    # Get ms_token from environment variable
    ms_token = os.getenv("ms_token")
    if not ms_token:
        print("Error: MSTOKEN environment variable not set!")
        print("Please set your ms_token from TikTok cookies as an environment variable.")
        return
    
    # Initialize the API the basic way
    api = TikTokApi()
    
    print("Type of api:", type(api))
    print("API object:", api)
    
    try:
        # Create a session with ms_token
        print("Creating session with ms_token...")
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser="firefox", headless=False)
        print("Session created successfully!")
        
        # Get trending videos
        trending_videos = api.trending.videos(count=5)  # Start with just 5
        print("Type of trending_videos:", type(trending_videos))
        print("Trending videos object:", trending_videos)
        
        # Try to iterate through videos
        video_count = 0
        async for video in trending_videos:
            print(f"Video {video_count + 1}:")
            print(f"  Video ID: {video.id}")
            print(f"  Video URL: {video.url}")
            print(f"  Author: {video.author.username if video.author else 'Unknown'}")
            print(f"  Stats: {video.stats}")
            
            # Get comments for this video
            print(f"  Getting comments...")
            comment_count = 0
            try:
                async for comment in video.comments(count=10):
                    print(f"    Comment {comment_count + 1}: {comment.text}")
                    print(f"      Author: {comment.author.username if comment.author else 'Unknown'}")
                    print(f"      Likes: {comment.likes_count}")
                    comment_count += 1
                    if comment_count >= 10:  # Stop after 10 comments
                        break
            except Exception as comment_error:
                print(f"    Error getting comments: {comment_error}")
            
            print("---")
            video_count += 1
            if video_count >= 5:
                break

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {str(e)}")

if __name__ == "__main__":
    asyncio.run(get_trending_data())

