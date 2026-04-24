const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const enableToggle = document.getElementById("enableToggle");
const videoList = document.getElementById("videoList");

// Check app connection
chrome.runtime.sendMessage({ type: "check_status" }, (response) => {
  if (response && response.connected) {
    statusDot.className = "status-dot connected";
    statusText.textContent = "Conectado a KrosDownloadManager";
  } else {
    statusDot.className = "status-dot disconnected";
    statusText.textContent = "App no detectada — ábrela primero";
  }
});

// Load toggle state
chrome.storage.local.get("enabled", (data) => {
  enableToggle.checked = data.enabled !== false;
});

enableToggle.addEventListener("change", () => {
  chrome.storage.local.set({ enabled: enableToggle.checked });
});

// Get detected videos from content script
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (!tabs[0]) return;
  chrome.tabs.sendMessage(tabs[0].id, { type: "get_videos" }, (response) => {
    if (chrome.runtime.lastError || !response || !response.videos || response.videos.length === 0) {
      return;
    }

    videoList.innerHTML = "";
    response.videos.forEach((video) => {
      const item = document.createElement("div");
      item.className = "video-item";
      item.innerHTML = `
        <span class="video-item-icon">&#x25B6;</span>
        <span class="video-item-url">${escapeHtml(truncateUrl(video.url))}</span>
      `;
      item.addEventListener("click", () => {
        chrome.runtime.sendMessage({
          type: "download_video",
          url: video.url,
          title: "",
          pageUrl: tabs[0].url,
        }, (resp) => {
          if (resp && resp.success) {
            item.style.background = "#1a3a1a";
            setTimeout(() => { item.style.background = ""; }, 1000);
          }
        });
      });
      videoList.appendChild(item);
    });
  });
});

function truncateUrl(url) {
  try {
    const u = new URL(url);
    const path = u.pathname;
    if (path.length > 40) {
      return u.hostname + "/..." + path.slice(-30);
    }
    return u.hostname + path;
  } catch (_e) {
    return url.slice(0, 50);
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
