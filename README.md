# TikTok Dashboard

A real-time TikTok analytics dashboard that scrapes trending videos, analyzes comments, and displays insights with beautiful visualizations.

## 🚀 Features

- **Real-time TikTok Scraping**: Collects trending videos and comments
- **Interactive Dashboard**: Beautiful UI with video previews and stats
- **Phrase Analysis**: Identifies trending phrases from comments
- **Video Previews**: Shows actual TikTok video thumbnails
- **Live Updates**: Refresh data with one click
- **Portfolio Ready**: Deployable to any hosting platform

## 🛠️ Tech Stack

- **Backend**: Python, Flask, TikTokApi
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Deployment**: Heroku, Vercel, Railway, or any Python hosting

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd tiktok-stories
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up TikTok API token**

   ```bash
   # Set your ms_token from TikTok cookies
   export ms_token="your_tiktok_ms_token_here"
   ```

4. **Run locally**

   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## 🌐 Deployment

### Heroku Deployment

1. **Create Heroku app**

   ```bash
   heroku create your-tiktok-dashboard
   ```

2. **Set environment variables**

   ```bash
   heroku config:set ms_token="your_tiktok_ms_token_here"
   ```

3. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy TikTok Dashboard"
   git push heroku main
   ```

### Vercel Deployment

1. **Install Vercel CLI**

   ```bash
   npm i -g vercel
   ```

2. **Deploy**

   ```bash
   vercel
   ```

3. **Set environment variables in Vercel dashboard**

### Railway Deployment

1. **Connect your GitHub repo to Railway**
2. **Set environment variables**
3. **Deploy automatically**

## 🔧 Configuration

### Environment Variables

- `ms_token`: Your TikTok ms_token from browser cookies
- `PORT`: Server port (auto-set by hosting platforms)

### Database Setup

The app automatically creates a SQLite database (`tiktok_data.db`) on first run.

## 📊 API Endpoints

- `GET /` - Main dashboard page
- `POST /api/refresh` - Start TikTok scraping
- `GET /api/status` - Get scraping status
- `GET /api/dashboard-data` - Get dashboard data
- `GET /health` - Health check

## 🎨 Customization

### Styling

- Modify `styles.css` for custom themes
- Update color schemes in CSS variables
- Adjust layout in grid system

### Data Collection

- Modify `comments.py` for different scraping strategies
- Update `database_helper.py` for custom analytics
- Add new metrics in `export_dashboard_data.py`

## 🔒 Security Notes

- Keep your `ms_token` secure and private
- Consider rate limiting for production
- Monitor API usage to avoid TikTok restrictions

## 📈 Portfolio Features

This project demonstrates:

- **Full-stack development** with Python/Flask backend
- **Real-time data processing** and analytics
- **Modern web design** with responsive UI
- **API integration** with external services
- **Database management** and data visualization
- **Deployment** and hosting configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use this in your portfolio!

## 🆘 Support

For issues or questions:

1. Check the documentation
2. Review error logs
3. Ensure environment variables are set correctly
4. Verify TikTok API token is valid

---

**Perfect for portfolios!** This project showcases real-world web development skills with modern technologies and deployment practices.
