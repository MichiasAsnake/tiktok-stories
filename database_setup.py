import sqlite3
import os

def create_database():
    """Create SQLite database and tables for TikTok data"""
    
    # Create database file
    db_path = "tiktok_data.db"
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create videos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE NOT NULL,
            video_url TEXT,
            author TEXT,
            author_avatar_medium TEXT,
            dynamic_cover TEXT,
            cover TEXT,
            likes_count INTEGER,
            comment_count INTEGER,
            share_count INTEGER,
            play_count INTEGER,
            create_time TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id TEXT UNIQUE NOT NULL,
            video_id TEXT NOT NULL,
            text TEXT NOT NULL,
            author TEXT,
            likes_count INTEGER DEFAULT 0,
            create_time TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos (video_id)
        )
    ''')
    
    # Create hashtags table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hashtags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            hashtag TEXT NOT NULL,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos (video_id)
        )
    ''')
    
    # Create sentiment_analysis table (for future use)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            positive_score REAL,
            negative_score REAL,
            neutral_score REAL,
            dominant_sentiment TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos (video_id)
        )
    ''')
    
    # Add new columns to existing videos table if they don't exist
    try:
        cursor.execute('ALTER TABLE videos ADD COLUMN author_avatar_medium TEXT')
        print("✅ Added author_avatar_medium column")
    except sqlite3.OperationalError:
        print("ℹ️ author_avatar_medium column already exists")
    
    try:
        cursor.execute('ALTER TABLE videos ADD COLUMN dynamic_cover TEXT')
        print("✅ Added dynamic_cover column")
    except sqlite3.OperationalError:
        print("ℹ️ dynamic_cover column already exists")
    
    try:
        cursor.execute('ALTER TABLE videos ADD COLUMN cover TEXT')
        print("✅ Added cover column")
    except sqlite3.OperationalError:
        print("ℹ️ cover column already exists")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"✅ Database created successfully: {db_path}")
    print("📊 Tables created:")
    print("   - videos")
    print("   - comments") 
    print("   - hashtags")
    print("   - sentiment_analysis")

if __name__ == "__main__":
    create_database() 