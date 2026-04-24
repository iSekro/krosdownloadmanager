// Content script: detect videos and downloadable media on pages

(function () {
  "use strict";

  const videoSources = new Set();

  function extractVideoSources() {
    const found = [];

    // <video> elements
    document.querySelectorAll("video").forEach((video) => {
      if (video.src && !video.src.startsWith("blob:")) {
        found.push({ url: video.src, type: "video", title: document.title });
      }
      video.querySelectorAll("source").forEach((source) => {
        if (source.src && !source.src.startsWith("blob:")) {
          found.push({ url: source.src, type: "video", title: document.title });
        }
      });
    });

    // <audio> elements
    document.querySelectorAll("audio").forEach((audio) => {
      if (audio.src && !audio.src.startsWith("blob:")) {
        found.push({ url: audio.src, type: "audio", title: document.title });
      }
      audio.querySelectorAll("source").forEach((source) => {
        if (source.src && !source.src.startsWith("blob:")) {
          found.push({ url: source.src, type: "audio", title: document.title });
        }
      });
    });

    // <a> links to media files
    const mediaExtensions = [
      ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v",
      ".mp3", ".flac", ".wav", ".aac", ".ogg", ".wma", ".m4a",
    ];
    document.querySelectorAll("a[href]").forEach((link) => {
      try {
        const href = link.href.toLowerCase();
        if (mediaExtensions.some((ext) => href.includes(ext))) {
          found.push({
            url: link.href,
            type: href.match(/\.(mp3|flac|wav|aac|ogg|wma|m4a)/) ? "audio" : "video",
            title: link.textContent.trim() || document.title,
          });
        }
      } catch (_e) { /* invalid URL */ }
    });

    return found;
  }

  function sendVideosToBackground(videos) {
    videos.forEach((v) => {
      if (!videoSources.has(v.url)) {
        videoSources.add(v.url);
        chrome.runtime.sendMessage({
          type: "video_found",
          url: v.url,
          mediaType: v.type,
          title: v.title,
          pageUrl: window.location.href,
        });
      }
    });
  }

  // Initial scan
  setTimeout(() => {
    const videos = extractVideoSources();
    if (videos.length > 0) {
      sendVideosToBackground(videos);
    }
  }, 2000);

  // Watch for dynamically added media
  const observer = new MutationObserver(() => {
    const videos = extractVideoSources();
    if (videos.length > 0) {
      sendVideosToBackground(videos);
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type === "get_videos") {
      sendResponse({ videos: Array.from(videoSources).map((url) => ({ url })) });
    }
  });
})();
