import asyncio
import os
from TikTokApi import TikTokApi

async def test_video_attributes():
    # Get ms_token from environment variable
    ms_token = os.getenv("ms_token")
    if not ms_token:
        print("Error: MSTOKEN environment variable not set!")
        return
    
    # Initialize the API
    api = TikTokApi()
    
    try:
        # Create a session with ms_token
        print("Creating session with ms_token...")
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser="firefox", headless=False)
        print("Session created successfully!")
        
        # Get just one trending video for testing
        trending_videos = api.trending.videos(count=1)
        
        async for video in trending_videos:
            print(f"\n=== Video Analysis ===")
            print(f"Video ID: {video.id}")
            print(f"Video URL: {video.url}")
            print(f"Author: {video.author.username if video.author else 'Unknown'}")
            
            # Get the full data dictionary
            video_dict = video.as_dict
            print(f"\n=== Full Video Data Structure ===")
            
            # Look for cover-related fields
            cover_fields = ['cover', 'dynamicCover', 'staticCover', 'videoCover', 'thumbnail', 'coverUrl', 'dynamicCoverUrl']
            print(f"\nCover-related fields:")
            for field in cover_fields:
                if field in video_dict:
                    print(f"  {field}: {video_dict[field]}")
                else:
                    print(f"  {field}: Not found")
            
            # Look for author avatar fields
            if 'author' in video_dict and video_dict['author']:
                author_dict = video_dict['author']
                avatar_fields = ['avatarMedium', 'avatar', 'avatarThumb', 'avatarLarger', 'avatarUrl']
                print(f"\nAuthor avatar fields:")
                for field in avatar_fields:
                    if field in author_dict:
                        print(f"  {field}: {author_dict[field]}")
                    else:
                        print(f"  {field}: Not found")
            
            # Show all available fields in video_dict
            print(f"\n=== All Available Video Fields ===")
            for key, value in video_dict.items():
                if key not in ['author']:  # Skip author for now
                    print(f"  {key}: {value}")
            
            # Show all available fields in author_dict
            if 'author' in video_dict and video_dict['author']:
                print(f"\n=== All Available Author Fields ===")
                for key, value in video_dict['author'].items():
                    print(f"  {key}: {value}")
            
            break  # Only test one video
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_video_attributes()) 