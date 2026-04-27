const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const activeDownloads = document.getElementById("activeDownloads");
const enableToggle = document.getElementById("enableToggle");
const videoList = document.getElementById("videoList");
const fileList = document.getElementById("fileList");
const videoCount = document.getElementById("videoCount");
const fileCount = document.getElementById("fileCount");
const btnDownloadAll = document.getElementById("btnDownloadAll");
const btnRefresh = document.getElementById("btnRefresh");

let currentTabId = null;
let allVideos = [];
let allFiles = [];

// Check app connection
chrome.runtime.sendMessage({ type: "check_status" }, (response) => {
  if (response && response.connected) {
    statusDot.className = "status-dot connected";
    statusText.textContent = "Conectado";
    if (response.data && response.data.active_downloads !== undefined) {
      const count = response.data.active_downloads;
      if (count > 0) {
        activeDownloads.textContent = count + " descargando";
      }
    }
  } else {
    statusDot.className = "status-dot disconnected";
    statusText.textContent = "App no detectada";
  }
});

// Load toggle state
chrome.storage.local.get("enabled", (data) => {
  enableToggle.checked = data.enabled !== false;
});

enableToggle.addEventListener("change", () => {
  chrome.storage.local.set({ enabled: enableToggle.checked });
});

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

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

function getFilenameFromUrl(url) {
  try {
    const pathname = new URL(url).pathname;
    const parts = pathname.split("/");
    return decodeURIComponent(parts[parts.length - 1]) || url;
  } catch (_e) {
    return url;
  }
}

function getMediaIcon(type) {
  if (type === "audio") return "&#x1F3B5;";
  return "&#x25B6;";
}

function getFileIcon(ext) {
  const icons = {
    ".zip": "&#x1F4E6;", ".rar": "&#x1F4E6;", ".7z": "&#x1F4E6;",
    ".pdf": "&#x1F4C4;", ".doc": "&#x1F4C4;", ".docx": "&#x1F4C4;",
    ".exe": "&#x1F4BF;", ".msi": "&#x1F4BF;",
    ".iso": "&#x1F4C0;",
  };
  return icons[ext] || "&#x1F4C1;";
}

function formatResolution(w, h) {
  if (w && h) return w + "x" + h;
  return "";
}

function renderVideos(videos) {
  allVideos = videos;
  if (!videos || videos.length === 0) {
    videoList.innerHTML = '<div class="empty-text">Sin media en esta pagina</div>';
    videoCount.style.display = "none";
    return;
  }

  videoCount.textContent = videos.length;
  videoCount.style.display = "inline";
  videoList.innerHTML = "";

  videos.forEach((video) => {
    const item = document.createElement("div");
    item.className = "media-item";

    const name = video.title || getFilenameFromUrl(video.url);
    const meta = [];
    if (video.type) meta.push(video.type);
    const res = formatResolution(video.width, video.height);
    if (res) meta.push(res);

    item.innerHTML = `
      <span class="media-item-icon">${getMediaIcon(video.type)}</span>
      <div class="media-item-info">
        <div class="media-item-name">${escapeHtml(name)}</div>
        <div class="media-item-meta">${escapeHtml(meta.join(" | ") || truncateUrl(video.url))}</div>
      </div>
      <button class="media-item-btn">Descargar</button>
    `;

    const btn = item.querySelector(".media-item-btn");
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      chrome.runtime.sendMessage({
        type: "download_video",
        url: video.url,
        title: video.title || "",
        pageUrl: video.pageUrl || "",
      }, (resp) => {
        if (resp && resp.success) {
          btn.textContent = "Enviado";
          btn.classList.add("sent");
        }
      });
    });

    videoList.appendChild(item);
  });
}

function renderFiles(files) {
  allFiles = files;
  if (!files || files.length === 0) {
    fileList.innerHTML = '<div class="empty-text">Sin archivos detectados</div>';
    fileCount.style.display = "none";
    return;
  }

  fileCount.textContent = files.length;
  fileCount.style.display = "inline";
  fileList.innerHTML = "";

  files.forEach((file) => {
    const item = document.createElement("div");
    item.className = "media-item";

    const name = file.title || getFilenameFromUrl(file.url);
    const ext = file.extension || "";

    item.innerHTML = `
      <span class="media-item-icon">${getFileIcon(ext)}</span>
      <div class="media-item-info">
        <div class="media-item-name">${escapeHtml(name)}</div>
        <div class="media-item-meta">${escapeHtml(ext.toUpperCase().slice(1) || truncateUrl(file.url))}</div>
      </div>
      <button class="media-item-btn">Descargar</button>
    `;

    const btn = item.querySelector(".media-item-btn");
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      chrome.runtime.sendMessage({
        type: "download_file",
        url: file.url,
        filename: getFilenameFromUrl(file.url),
        referrer: "",
      }, (resp) => {
        if (resp && resp.success) {
          btn.textContent = "Enviado";
          btn.classList.add("sent");
        }
      });
    });

    fileList.appendChild(item);
  });
}

function loadContent() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0]) return;
    currentTabId = tabs[0].id;

    // Get videos from background (stored from content script notifications)
    chrome.runtime.sendMessage({ type: "get_detected_videos", tabId: currentTabId }, (bgResp) => {
      const bgVideos = (bgResp && bgResp.videos) || [];

      // Also get from content script directly
      chrome.tabs.sendMessage(currentTabId, { type: "get_videos" }, (csResp) => {
        const csVideos = (csResp && csResp.videos) || [];

        // Merge unique by URL
        const seen = new Set();
        const merged = [];
        [...bgVideos, ...csVideos].forEach((v) => {
          if (!seen.has(v.url)) {
            seen.add(v.url);
            merged.push(v);
          }
        });
        renderVideos(merged);
      });
    });

    // Get downloadable files from content script
    chrome.tabs.sendMessage(currentTabId, { type: "get_downloadable_files" }, (response) => {
      if (chrome.runtime.lastError || !response) return;
      renderFiles(response.files || []);
    });
  });
}

// Download All button
btnDownloadAll.addEventListener("click", () => {
  const allUrls = [];
  allVideos.forEach((v) => allUrls.push({ url: v.url, filename: v.title || "" }));
  allFiles.forEach((f) => allUrls.push({ url: f.url, filename: getFilenameFromUrl(f.url) }));

  if (allUrls.length === 0) return;

  chrome.runtime.sendMessage({ type: "download_batch", urls: allUrls }, (resp) => {
    if (resp && resp.success) {
      btnDownloadAll.textContent = "Enviado (" + allUrls.length + ")";
      btnDownloadAll.style.background = "#1a3a1a";
      setTimeout(() => {
        btnDownloadAll.textContent = "Descargar todo";
        btnDownloadAll.style.background = "";
      }, 2000);
    }
  });
});

// Refresh button
btnRefresh.addEventListener("click", loadContent);

// Initial load
loadContent();
