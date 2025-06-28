// Global variables for refresh functionality
let isRefreshing = false;
let statusCheckInterval = null;

// Initialize the dashboard
function loadDashboard() {
  fetch("dashboard_data.json")
    .then((r) => r.json())
    .then((data) => {
      document.getElementById("stats").innerHTML = `
        <h3>Stats</h3>
        <ul class="stats-list">
            <li class="stat-total-videos">Total Videos: ${data.stats.total_videos}</li>
            <li class="stat-total-comments">Total Comments: ${data.stats.total_comments}</li>
            <li class="stat-total-hashtags">Total Hashtags: ${data.stats.total_hashtags}</li>
            <li class="stat-avg-likes">Avg Likes/Video: ${data.stats.avg_likes_per_video}</li>
            <li class="stat-avg-comments">Avg Comments/Video: ${data.stats.avg_comments_per_video}</li>
        </ul>
    `;

      // Show phrases only
      const phrases = data.top_phrases || [];

      document.getElementById("hashtags").innerHTML = `
        <h3>Top Phrases</h3>
        <div class="phrases-container">
          <div class="phrases-scroll">
            <div class="phrases-wrapper">
              ${phrases
                .map(
                  (p) =>
                    `<button class="phrase-button">"${p.phrase}" (${p.count})</button>`
                )
                .join("")}
            </div>
          </div>
        </div>
    `;
      document.getElementById("top-comments").innerHTML = `
        <h3>Top Comments</h3>
        <ul class="comments-list">
            ${data.top_comments
              .map(
                (c) =>
                  `<div class="comment-item"> <p>"${c.text}"</p><small>by ${c.author} (${c.likes_count} likes)</small></div>`
              )
              .join("")}
        </ul>
    `;
      document.getElementById("recent-videos").innerHTML = `
        <h3>Recent Videos</h3>
        <div class="videos-list">
            ${data.recent_videos
              .map((v) => {
                const videoUrl = `https://www.tiktok.com/@${v.author}/video/${v.video_id}`;

                // Better fallback logic for profile photos using correct field name
                const profilePhotoUrl =
                  v.author_avatar_medium ||
                  `https://p16-sign-va.tiktokcdn.com/aweme/100x100/${v.author}.jpeg`;

                // Better fallback logic for video covers using correct field names
                const videoCoverUrl =
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
                                <img src="${profilePhotoUrl}" alt="${
                  v.author
                }" class="profile-photo" onerror="this.style.display='none'">
                                <span class="author-name">@${v.author}</span>
                            </div>
                            <div class="video-stats">
                                <span class="likes">❤️ ${(
                                  v.likes_count / 1000
                                ).toFixed(1)}K</span>
                                <span class="comments">💬 ${(
                                  v.comment_count / 1000
                                ).toFixed(1)}K</span>
                            </div>
                        </div>
                    </div>
                  </a>`;
              })
              .join("")}
            ${data.recent_videos
              .map((v) => {
                const videoUrl = `https://www.tiktok.com/@${v.author}/video/${v.video_id}`;

                // Better fallback logic for profile photos using correct field name
                const profilePhotoUrl =
                  v.author_avatar_medium ||
                  `https://p16-sign-va.tiktokcdn.com/aweme/100x100/${v.author}.jpeg`;

                // Better fallback logic for video covers using correct field names
                const videoCoverUrl =
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
                                <img src="${profilePhotoUrl}" alt="${
                  v.author
                }" class="profile-photo" onerror="this.style.display='none'">
                                <span class="author-name">@${v.author}</span>
                            </div>
                            <div class="video-stats">
                                <span class="likes">❤️ ${(
                                  v.likes_count / 1000
                                ).toFixed(1)}K</span>
                                <span class="comments">💬 ${(
                                  v.comment_count / 1000
                                ).toFixed(1)}K</span>
                            </div>
                        </div>
                    </div>
                  </a>`;
              })
              .join("")}
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
