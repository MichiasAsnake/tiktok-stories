@echo off
echo Starting TikTok scraping...
python comments.py
echo Scraping completed, updating dashboard...
python export_dashboard_data.py
echo Dashboard updated successfully!
pause 