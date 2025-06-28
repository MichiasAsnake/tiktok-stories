from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS
import subprocess
import threading
import time
import json
import os
import sys

app = Flask(__name__)
CORS(app)

# Global variable to track scraping status
scraping_status = {
    "is_running": False,
    "progress": 0,
    "message": "",
    "error": None
}

def run_scraping():
    """Run the TikTok scraping process in a separate thread"""
    global scraping_status
    
    try:
        scraping_status["is_running"] = True
        scraping_status["progress"] = 0
        scraping_status["message"] = "Starting TikTok scraping..."
        scraping_status["error"] = None
        
        # Step 1: Run data collection
        scraping_status["progress"] = 20
        scraping_status["message"] = "Collecting trending videos..."
        
        # Use python executable path for better compatibility
        python_executable = sys.executable
        
        result = subprocess.run([python_executable, "comments.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise Exception(f"Data collection failed: {result.stderr}")
        
        # Step 2: Export dashboard data
        scraping_status["progress"] = 80
        scraping_status["message"] = "Updating dashboard data..."
        
        result = subprocess.run([python_executable, "export_dashboard_data.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise Exception(f"Dashboard export failed: {result.stderr}")
        
        scraping_status["progress"] = 100
        scraping_status["message"] = "Scraping completed successfully!"
        
    except subprocess.TimeoutExpired:
        scraping_status["error"] = "Scraping timed out after 5 minutes"
        scraping_status["message"] = "Error: Scraping timed out"
    except Exception as e:
        scraping_status["error"] = str(e)
        scraping_status["message"] = f"Error: {str(e)}"
    finally:
        scraping_status["is_running"] = False

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, JSON)"""
    return send_from_directory('.', filename)

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Start the TikTok scraping process"""
    global scraping_status
    
    if scraping_status["is_running"]:
        return jsonify({"error": "Scraping already in progress"}), 400
    
    # Start scraping in a separate thread
    thread = threading.Thread(target=run_scraping)
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Scraping started", "status": "running"})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current scraping status"""
    global scraping_status
    return jsonify(scraping_status)

@app.route('/api/export', methods=['POST'])
def export_dashboard_data():
    """Manually export dashboard data"""
    try:
        # Use python executable path for better compatibility
        python_executable = sys.executable
        
        result = subprocess.run([python_executable, "export_dashboard_data.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return jsonify({"error": f"Export failed: {result.stderr}"}), 500
        
        return jsonify({"message": "Dashboard data exported successfully"})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Export timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get the current dashboard data"""
    try:
        with open('dashboard_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Dashboard data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for deployment platforms"""
    return jsonify({"status": "healthy", "message": "TikTok Dashboard is running"})

if __name__ == '__main__':
    # Get port from environment variable (for deployment platforms)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 