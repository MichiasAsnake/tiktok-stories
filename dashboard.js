// Global variables for refresh functionality
let isRefreshing = false;
let statusCheckInterval = null;

// Number formatting function
function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, "") + "K";
  } else {
    return num.toLocaleString();
  }
}

// Update timestamp function
function updateTimestamp() {
  const now = new Date();
  const dateString = now.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
  const timeString = now.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
  document.getElementById(
    "timestamp"
  ).textContent = `${dateString} ${timeString}`;
}

// Initialize the dashboard
function loadDashboard() {
  updateTimestamp(); // Update timestamp when dashboard loads

  fetch("dashboard_data.json")
    .then((r) => r.json())
    .then((data) => {
      document.getElementById("stats").innerHTML = `
            <h3><img src="icons/top stats.svg" width="25" height="25" style="margin-right: 8px; vertical-align: middle;" alt="Top Stats">Stats</h3>
        <ul class="stats-list">
            <li class="stat-total-videos">Total Videos: <span class="stats-number">${formatNumber(
              data.stats.total_videos
            )}</span></li>
            <li class="stat-total-comments">Total Comments: <span class="stats-number">${formatNumber(
              data.stats.total_comments
            )}</span></li>
            <li class="stat-total-hashtags">Total Hashtags: <span class="stats-number">${formatNumber(
              data.stats.total_hashtags
            )}</span></li>
            <li class="stat-avg-likes">Avg Likes/Video: <span class="stats-number">${formatNumber(
              Math.round(data.stats.avg_likes_per_video)
            )}</span></li>
            <li class="stat-avg-comments">Avg Comments/Video: <span class="stats-number">${formatNumber(
              Math.round(data.stats.avg_comments_per_video)
            )}</span></li>
        </ul>
    `;

      // Show phrases only
      const phrases = data.top_phrases || [];

      document.getElementById("hashtags").innerHTML = `
        <h3><img src="icons/top phrases.svg" width="25" height="25" style="margin-right: 8px; vertical-align: middle;" alt="Top Phrases">Top Phrases</h3>
        <div class="phrases-container">
          <div class="phrases-scroll">
            <div class="phrases-wrapper">
              ${phrases
                .map(
                  (p) =>
                    `<button class="phrase-button"><span class="phrase-text">"${
                      p.phrase
                    }"</span> <span class="phrase-count">(${formatNumber(
                      p.count
                    )})</span></button>`
                )
                .join("")}
            </div>
          </div>
        </div>
    `;
      document.getElementById("top-comments").innerHTML = `
        <h3><img src="icons/top comments.svg" width="25" height="25" style="margin-right: 8px; vertical-align: middle;" alt="Top Comments">Top Comments</h3>
        <ul class="comments-list">
            ${data.top_comments
              .map(
                (c) =>
                  `<div class="comment-item"> <p>"${
                    c.text
                  }"</p><small>by <span class="comment-author">${
                    c.author
                  }</span> <span class="comment-likes">(${formatNumber(
                    c.likes_count
                  )} likes)</span></small></div>`
              )
              .join("")}
        </ul>
    `;
      // Helper function to render a video card
      const renderVideoCard = (v) => {
        const videoUrl = `https://www.tiktok.com/@${v.author}/video/${v.video_id}`;

        // Use local cached images first, then fall back to CDN URLs
        const profilePhotoUrl =
          v.author_avatar_local ||
          v.author_avatar_medium ||
          `https://p16-sign-va.tiktokcdn.com/aweme/100x100/${v.author}.jpeg`;

        // Use local cached cover first, then fall back to CDN URLs
        const videoCoverUrl =
          v.cover_local ||
          v.dynamic_cover ||
          v.cover ||
          `https://p16-sign-va.tiktokcdn.com/obj/aweme/100x100/${v.video_id}.jpeg`;

        return `
          <a href="${videoUrl}" target="_blank" class="video-item-link">
            <div class="video-item">
                <div class="video-preview">
                    <img src="${videoCoverUrl}" alt="Video preview" class="video-cover" onerror="this.style.display='none'">
                    <div class="play-overlay">
                        <span class="play-icon">▶️</span>
                    </div>
                </div>
                <div class="video-info">
                    <div class="author-info">
                        <img src="${profilePhotoUrl}" alt="${v.author}" class="profile-photo" onerror="this.style.display='none'">
                        <span class="author-name">@${v.author}</span>
                    </div>
                    <div class="video-stats">
                        <span class="likes">❤️ ${formatNumber(v.likes_count)}</span>
                        <span class="comments">💬 ${formatNumber(v.comment_count)}</span>
                    </div>
                </div>
            </div>
          </a>`;
      };

      const videosHtml = data.recent_videos.map(renderVideoCard).join("");

      document.getElementById("recent-videos").innerHTML = `
        <h3><img src="icons/recent videos.svg" width="25" height="25" style="margin-right: 8px; vertical-align: middle;" alt="Recent Videos">Recent Videos</h3>
        <div class="videos-scroll-container">
          <div class="videos-list">
            ${videosHtml}
            ${videosHtml}
          </div>
        </div>
    `;
    })
    .catch((error) => {
      console.error("Error loading dashboard:", error);
    });
}

// Refresh functionality
async function refreshData() {
  if (isRefreshing) return;

  isRefreshing = true;
  const refreshBtn = document.getElementById("refresh-btn");
  const loadingOverlay = document.getElementById("loading-overlay");
  const loadingStatus = document.querySelector(".loading-status");

  // Update UI
  refreshBtn.classList.add("loading");
  loadingOverlay.classList.remove("hidden");
  loadingStatus.textContent = "Starting TikTok scraping...";

  try {
    // Start scraping via Flask API
    const response = await fetch("/api/refresh", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to start scraping");
    }

    // Start polling for status
    startStatusPolling();
  } catch (error) {
    console.error("Error starting refresh:", error);
    loadingStatus.textContent = `Error: ${error.message}`;
    setTimeout(() => {
      stopRefresh();
    }, 3000);
  }
}

function startStatusPolling() {
  statusCheckInterval = setInterval(async () => {
    try {
      const response = await fetch("/api/status");
      const status = await response.json();

      const loadingStatus = document.querySelector(".loading-status");
      loadingStatus.textContent = status.message;

      if (!status.is_running) {
        // Scraping completed
        clearInterval(statusCheckInterval);

        if (status.error) {
          loadingStatus.textContent = `Error: ${status.error}`;
          setTimeout(() => {
            stopRefresh();
          }, 3000);
        } else {
          // Success - export dashboard data and reload
          loadingStatus.textContent = "Updating dashboard data...";

          try {
            // Export dashboard data
            const exportResponse = await fetch("/api/export", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
            });

            if (exportResponse.ok) {
              loadingStatus.textContent = "Dashboard updated successfully!";
              setTimeout(() => {
                loadDashboard();
                stopRefresh();
              }, 1000);
            } else {
              throw new Error("Failed to export dashboard data");
            }
          } catch (exportError) {
            console.error("Error exporting dashboard data:", exportError);
            loadingStatus.textContent = "Error updating dashboard data";
            setTimeout(() => {
              stopRefresh();
            }, 3000);
          }
        }
      }
    } catch (error) {
      console.error("Error checking status:", error);
    }
  }, 1000);
}

function stopRefresh() {
  isRefreshing = false;
  const refreshBtn = document.getElementById("refresh-btn");
  const loadingOverlay = document.getElementById("loading-overlay");

  refreshBtn.classList.remove("loading");
  loadingOverlay.classList.add("hidden");

  if (statusCheckInterval) {
    clearInterval(statusCheckInterval);
    statusCheckInterval = null;
  }
}

// Event listeners
document.addEventListener("DOMContentLoaded", function () {
  // Load initial dashboard
  loadDashboard();

  // Add refresh button event listener
  const refreshBtn = document.getElementById("refresh-btn");
  refreshBtn.addEventListener("click", refreshData);
});
