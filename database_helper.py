import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import re
from collections import Counter

class TikTokDatabase:
    def __init__(self, db_path: str = "tiktok_data.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def video_exists(self, video_id: str) -> bool:
        """Check if a video already exists in the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM videos WHERE video_id = ?', (video_id,))
            count = cursor.fetchone()[0]
            
            conn.close()
            return count > 0
            
        except Exception as e:
            print(f"Error checking if video exists: {e}")
            return False
    
    def comment_exists(self, comment_id: str) -> bool:
        """Check if a comment already exists in the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM comments WHERE comment_id = ?', (comment_id,))
            count = cursor.fetchone()[0]
            
            conn.close()
            return count > 0
            
        except Exception as e:
            print(f"Error checking if comment exists: {e}")
            return False
    
    def get_video_comment_count(self, video_id: str) -> int:
        """Get the number of comments already stored for a video"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM comments WHERE video_id = ?', (video_id,))
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            print(f"Error getting video comment count: {e}")
            return 0
    
    def insert_video(self, video_data: Dict) -> bool:
        """Insert video data into database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Extract stats
            stats = video_data.get('stats', {})
            
            cursor.execute('''
                INSERT OR REPLACE INTO videos 
                (video_id, video_url, author, author_avatar_medium, dynamic_cover, cover, likes_count, comment_count, share_count, play_count, create_time, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_data.get('video_id'),
                video_data.get('video_url'),
                video_data.get('author'),
                video_data.get('author_avatar_medium'),
                video_data.get('dynamic_cover'),
                video_data.get('cover'),
                stats.get('diggCount', 0),
                stats.get('commentCount', 0),
                stats.get('shareCount', 0),
                stats.get('playCount', 0),
                video_data.get('create_time'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error inserting video: {e}")
            return False
    
    def insert_comments(self, video_id: str, comments: List[Dict]) -> int:
        """Insert comments for a video, skipping existing ones"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            inserted_count = 0
            skipped_count = 0
            
            for comment in comments:
                comment_id = comment.get('comment_id')
                
                # Check if comment already exists
                if comment_id and self.comment_exists(comment_id):
                    skipped_count += 1
                    continue
                
                cursor.execute('''
                    INSERT OR REPLACE INTO comments 
                    (comment_id, video_id, text, author, likes_count, create_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    comment_id,
                    video_id,
                    comment.get('text'),
                    comment.get('author'),
                    comment.get('likes_count', 0),
                    comment.get('create_time')
                ))
                inserted_count += 1
            
            conn.commit()
            conn.close()
            
            if skipped_count > 0:
                print(f"  ⏭️ Skipped {skipped_count} existing comments")
            
            return inserted_count
            
        except Exception as e:
            print(f"Error inserting comments: {e}")
            return 0
    
    def insert_hashtags(self, video_id: str, hashtags: List[str]) -> int:
        """Insert hashtags for a video, avoiding duplicates"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            inserted_count = 0
            for hashtag in hashtags:
                # Check if this hashtag already exists for this video
                cursor.execute('''
                    SELECT COUNT(*) FROM hashtags 
                    WHERE video_id = ? AND hashtag = ?
                ''', (video_id, hashtag))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO hashtags (video_id, hashtag)
                        VALUES (?, ?)
                    ''', (video_id, hashtag))
                    inserted_count += 1
            
            conn.commit()
            conn.close()
            return inserted_count
            
        except Exception as e:
            print(f"Error inserting hashtags: {e}")
            return 0
    
    def get_trending_hashtags(self, limit: int = 20) -> List[Dict]:
        """Get most popular hashtags"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT hashtag, COUNT(*) as count
                FROM hashtags
                GROUP BY hashtag
                ORDER BY count DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'hashtag': row[0],
                    'count': row[1]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error getting trending hashtags: {e}")
            return []
    
    def get_top_comments(self, limit: int = 10) -> List[Dict]:
        """Get comments with highest likes"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.text, c.author, c.likes_count, v.video_id
                FROM comments c
                JOIN videos v ON c.video_id = v.video_id
                ORDER BY c.likes_count DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'text': row[0],
                    'author': row[1],
                    'likes_count': row[2],
                    'video_id': row[3]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error getting top comments: {e}")
            return []
    
    def get_video_stats(self) -> Dict:
        """Get overall video statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get total counts
            cursor.execute('SELECT COUNT(*) FROM videos')
            total_videos = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM comments')
            total_comments = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM hashtags')
            total_hashtags = cursor.fetchone()[0]
            
            # Get average engagement
            cursor.execute('''
                SELECT AVG(likes_count) as avg_likes, AVG(comment_count) as avg_comments
                FROM videos
            ''')
            avg_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_videos': total_videos,
                'total_comments': total_comments,
                'total_hashtags': total_hashtags,
                'avg_likes_per_video': round(avg_stats[0] or 0, 2),
                'avg_comments_per_video': round(avg_stats[1] or 0, 2)
            }
            
        except Exception as e:
            print(f"Error getting video stats: {e}")
            return {}
    
    def get_recent_videos(self, limit: int = 10) -> List[Dict]:
        """Get most recently scraped videos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT video_id, author, author_avatar_medium, dynamic_cover, cover, likes_count, comment_count, scraped_at
                FROM videos
                ORDER BY scraped_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'video_id': row[0],
                    'author': row[1],
                    'author_avatar_medium': row[2],
                    'dynamic_cover': row[3],
                    'cover': row[4],
                    'likes_count': row[5],
                    'comment_count': row[6],
                    'scraped_at': row[7]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error getting recent videos: {e}")
            return []
    
    def get_top_phrases(self, limit: int = 20) -> List[Dict]:
        """Get most common 2-4 word phrases from comments"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT text FROM comments')
            all_comments = [row[0] for row in cursor.fetchall()]
            conn.close()

            # More reasonable stopwords - only the most common function words
            stopwords = set([
                'the', 'and', 'for', 'that', 'with', 'this', 'you', 'your', 'are', 'was', 'but', 'not', 'have', 'has',
                'just', 'like', 'get', 'got', 'all', 'out', 'too', 'can', 'she', 'him', 'her', 'his', 'our', 'they',
                'from', 'who', 'had', 'did', 'its', 'i', 'me', 'my', 'we', 'he', 'it', 'to', 'of', 'in', 'on', 'is', 'a', 'an', 'at', 'as', 'so', 'be', 'by', 'or', 'if', 'do', 'no', 'yes', 'up', 'down', 'off', 'this', 'that', 'these', 'those', 'their', 'them', 'then', 'than', 'will', 'would', 'should', 'could', 'about', 'over', 'under', 'again', 'when', 'where', 'why', 'how', 'what', 'which', 'because', 'while', 'were', 'been', 'am', 'im', 'u', 'ur', 'isnt', 'dont', 'doesnt', 'cant', 'wont', 'youre', 'youve', 'youll', 'youd', 'hes', 'shes', 'theyre', 'weve', "we're", 'ive', 'ill', 'id', 'didnt', 'wasnt', 'arent', 'havent', 'hasnt', 'hadnt', 'couldnt', 'shouldnt', 'wouldnt', 'oh', 'ok', 'okay', 'yeah', 'nah', 'huh', 'hmm', 'lol', 'lmao', 'omg', 'pls', 'please', 'thanks', 'thank', 'welcome', 'hi', 'hey', 'yo', 'sup', 'bye', 'goodbye', 'see', 'ya', 'later', 'soon', 'now', 'then', 'never', 'always', 'sometimes', 'often', 'usually', 'rarely', 'seldom', 'once', 'twice', 'first', 'last', 'next', 'new', 'old', 'young', 'big', 'small', 'large', 'little', 'long', 'short', 'high', 'low', 'early', 'late', 'best', 'worst', 'better', 'worse', 'same', 'different', 'other', 'another', 'more', 'most', 'less', 'least', 'many', 'much', 'few', 'several', 'some', 'any', 'every', 'each', 'either', 'neither', 'both', 'all', 'none', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'
            ])

            def clean_text(text):
                # Better text cleaning - preserve meaningful punctuation and handle emojis
                # Remove emojis and special characters but keep basic punctuation
                text = re.sub(r'[^\w\s\.\,\!\?\-\']', ' ', text)
                # Normalize whitespace
                text = re.sub(r'\s+', ' ', text)
                return text.lower().strip()

            def get_ngrams(words, n):
                return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

            def is_quality_phrase(phrase):
                """Check if phrase is meaningful"""
                words = phrase.split()
                # Filter out phrases that are too repetitive
                if len(set(words)) < len(words) * 0.7:  # At least 70% unique words
                    return False
                # Filter out very short words in longer phrases
                if len(words) > 2:
                    short_words = sum(1 for w in words if len(w) < 3)
                    if short_words > len(words) * 0.5:  # More than 50% short words
                        return False
                return True

            phrase_counter = Counter()
            for comment in all_comments:
                if not comment or len(comment.strip()) < 5:  # Skip very short comments
                    continue
                    
                cleaned = clean_text(comment)
                words = [w for w in cleaned.split() if w not in stopwords and len(w) > 1]  # Reduced min length to 2
                
                if len(words) < 2:  # Skip comments with too few words
                    continue
                
                for n in range(2, 6):  # Extended to 2-5 word phrases
                    ngrams = get_ngrams(words, n)
                    for ng in ngrams:
                        if len(ng.split()) == n and is_quality_phrase(ng):
                            phrase_counter[ng] += 1

            # Get more phrases and then filter for quality
            top_phrases = phrase_counter.most_common(limit * 2)  # Get more candidates
            
            # Filter out very similar phrases and low-quality ones
            filtered_phrases = []
            seen_phrases = set()
            
            for phrase, count in top_phrases:
                if count < 3:  # Minimum frequency threshold
                    continue
                    
                # Check for duplicates (case-insensitive)
                phrase_lower = phrase.lower()
                if phrase_lower in seen_phrases:
                    continue
                    
                # Check for very similar phrases (one is substring of another)
                is_duplicate = False
                for existing_phrase, _ in filtered_phrases:
                    if phrase in existing_phrase or existing_phrase in phrase:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    filtered_phrases.append((phrase, count))
                    seen_phrases.add(phrase_lower)
                
                if len(filtered_phrases) >= limit:
                    break

            return [{"phrase": p, "count": c} for p, c in filtered_phrases]
        except Exception as e:
            print(f"Error getting top phrases: {e}")
            return []
    
    def update_video_media(self, video_data: Dict) -> bool:
        """Update video media data (covers and avatars)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE videos 
                SET author_avatar_medium = ?, dynamic_cover = ?, cover = ?
                WHERE video_id = ?
            ''', (
                video_data.get('author_avatar_medium'),
                video_data.get('dynamic_cover'),
                video_data.get('cover'),
                video_data.get('video_id')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating video media: {e}")
            return False 