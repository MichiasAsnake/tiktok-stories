# 📊 TikTok Analytics Dashboard

<img width="1163" height="842" alt="whats trending" src="https://github.com/user-attachments/assets/a6dcfbd2-dcd0-43e8-8694-3145a466fd26" />

A dashboard that visualizes trending TikTok video performance metrics, engagement insights, and comment trends.

**Live Demo:** [View on Vercel](https://tiktok-stories.vercel.app)

---

## ⚙️ Features

- **📈 Real-time Stats** - Video counts, engagement averages, trending metrics
- **🏷️ Trending Hashtags** - Most popular hashtags from viral content
- **💬 Top Comments** - Highest-liked comments with engagement data
- **🎬 Recent Videos** - Latest trending videos with cached thumbnails
- **🔄 Daily Auto-Refresh** - GitHub Actions updates data every day

---

## 🚀 How It Works

1. **GitHub Actions** runs daily at 8:00 AM UTC
2. **TikHub API** fetches trending TikTok videos and comments
3. **Images are cached** locally (no expiring CDN URLs!)
4. **Vercel auto-deploys** when the repo updates

---

## 🛠️ Setup

### 1. Fork this repo

### 2. Add GitHub Secret

Go to **Settings → Secrets → Actions** and add:

- `TIKHUB_API_KEY` - Your TikHub API key ([get one here](https://tikhub.io))

### 3. Deploy to Vercel

Connect your GitHub repo to Vercel - it will auto-deploy on every push.

### 4. Manual Refresh (Optional)

Trigger a data refresh anytime:

```bash
# Go to Actions → Refresh TikTok Data → Run workflow
```

---

## 📁 Project Structure

```
├── fetch_tikhub.py          # Data fetcher (TikHub API)
├── dashboard_data.json      # Generated dashboard data
├── dashboard.js             # Frontend JavaScript
├── styles.css               # Styling
├── index.html               # Main page
├── images/
│   ├── covers/              # Cached video thumbnails
│   └── avatars/             # Cached profile pictures
└── .github/workflows/
    └── refresh-data.yml     # Daily automation
```

---

## 📊 Data Sources

- **TikHub API** - Trending videos, comments, hashtags
- Videos and images are cached locally to avoid CDN expiration issues

---

## 🧪 Local Development

```bash
# Install dependencies
pip install requests

# Set API key and run
export TIKHUB_API_KEY="your-key-here"
python fetch_tikhub.py

# Serve locally
python -m http.server 8000
```

---

## 📝 License

MIT
