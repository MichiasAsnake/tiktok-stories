const Tiktok = require("@tobyg74/tiktok-api-dl");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

async function enrichVideoData() {
  const db = new sqlite3.Database("tiktok_data.db");

  try {
    // Get all videos from database
    const videos = await new Promise((resolve, reject) => {
      db.all(
        "SELECT video_id, author FROM videos ORDER BY scraped_at DESC",
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });

    console.log(`Enriching ${videos.length} videos with tiktokdl API...`);

    for (let i = 0; i < videos.length; i++) {
      const video = videos[i];
      const videoId = video.video_id;
      const author = video.author;

      try {
        // Construct TikTok URL
        const url = `https://www.tiktok.com/@${author}/video/${videoId}`;

        console.log(`Processing video ${i + 1}/${videos.length}: ${url}`);

        // Call tiktokdl API using the correct method
        const result = await Tiktok.Downloader(url, {
          version: "v1",
        });

        console.log("API Response:", JSON.stringify(result, null, 2));

        if (result.status === "success" && result.result) {
          const videoData = result.result;

          // Extract avatar URL - avatarMedium is an array, take first element
          const avatarUrl = videoData.author?.avatarMedium?.[0] || null;

          // Extract cover URLs - these are arrays, take first element
          const dynamicCoverUrl =
            videoData.video?.dynamicCover?.[0] ||
            videoData.dynamicCover?.[0] ||
            null;
          const coverUrl =
            videoData.video?.cover?.[0] || videoData.cover?.[0] || null;

          console.log(`Avatar URL: ${avatarUrl}`);
          console.log(`Dynamic Cover URL: ${dynamicCoverUrl}`);
          console.log(`Cover URL: ${coverUrl}`);

          // Update database with cover and avatar data
          await new Promise((resolve, reject) => {
            db.run(
              `
              UPDATE videos 
              SET author_avatar_medium = ?, dynamic_cover = ?, cover = ?
              WHERE video_id = ?
              `,
              [avatarUrl, dynamicCoverUrl, coverUrl, videoId],
              (err) => {
                if (err) reject(err);
                else resolve();
              }
            );
          });

          console.log(`✅ Updated video ${videoId}`);
        } else {
          console.log(`❌ No result for video ${videoId}:`, result);
        }

        // Add a small delay to avoid rate limiting
        await new Promise((resolve) => setTimeout(resolve, 2000));
      } catch (error) {
        console.log(`❌ Error processing video ${videoId}: ${error.message}`);
      }
    }

    console.log("✅ Database updated with enriched video data!");

    // Export updated dashboard data
    console.log("Exporting updated dashboard data...");
    const { exec } = require("child_process");
    exec("python export_dashboard_data.py", (error, stdout, stderr) => {
      if (error) {
        console.error(`❌ Error exporting dashboard data: ${error}`);
      } else {
        console.log("✅ Dashboard data exported!");
      }
    });
  } catch (error) {
    console.error("❌ Error enriching video data:", error);
  } finally {
    db.close();
  }
}

// Run the enrichment
enrichVideoData();
