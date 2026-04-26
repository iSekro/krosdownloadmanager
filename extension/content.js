// Content script: detect videos, media, and downloadable content on pages
// Provides floating download panel like IDM

(function () {
  "use strict";

  const videoSources = new Set();
  const detectedMedia = [];
  let floatingPanel = null;
  let panelMinimized = false;

  const MEDIA_EXTENSIONS = [
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v",
    ".mp3", ".flac", ".wav", ".aac", ".ogg", ".wma", ".m4a",
    ".3gp", ".ts", ".m3u8",
  ];

  const DOWNLOAD_EXTENSIONS = [
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
    ".exe", ".msi", ".dmg", ".deb", ".rpm", ".appimage",
    ".iso", ".img", ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx", ".torrent",
  ];

  function getFilenameFromUrl(url) {
    try {
      const pathname = new URL(url).pathname;
      const parts = pathname.split("/");
      return decodeURIComponent(parts[parts.length - 1]) || "";
    } catch (_e) {
      return "";
    }
  }

  function getFileExtension(url) {
    const filename = getFilenameFromUrl(url);
    const dot = filename.lastIndexOf(".");
    return dot > -1 ? filename.slice(dot).toLowerCase() : "";
  }

  function formatFileSize(bytes) {
    if (!bytes || bytes <= 0) return "";
    const units = ["B", "KB", "MB", "GB"];
    let i = 0;
    let size = bytes;
    while (size >= 1024 && i < units.length - 1) {
      size /= 1024;
      i++;
    }
    return size.toFixed(i > 0 ? 1 : 0) + " " + units[i];
  }

  function isMediaUrl(url) {
    const ext = getFileExtension(url);
    return MEDIA_EXTENSIONS.includes(ext);
  }

  function extractVideoSources() {
    const found = [];

    // <video> elements
    document.querySelectorAll("video").forEach((video) => {
      if (video.src && !video.src.startsWith("blob:") && !video.src.startsWith("data:")) {
        found.push({
          url: video.src,
          type: "video",
          title: video.title || document.title,
          duration: video.duration || 0,
          width: video.videoWidth || 0,
          height: video.videoHeight || 0,
        });
      }
      video.querySelectorAll("source").forEach((source) => {
        if (source.src && !source.src.startsWith("blob:") && !source.src.startsWith("data:")) {
          found.push({
            url: source.src,
            type: source.type || "video",
            title: document.title,
            duration: video.duration || 0,
            width: video.videoWidth || 0,
            height: video.videoHeight || 0,
          });
        }
      });
    });

    // <audio> elements
    document.querySelectorAll("audio").forEach((audio) => {
      if (audio.src && !audio.src.startsWith("blob:") && !audio.src.startsWith("data:")) {
        found.push({ url: audio.src, type: "audio", title: audio.title || document.title });
      }
      audio.querySelectorAll("source").forEach((source) => {
        if (source.src && !source.src.startsWith("blob:") && !source.src.startsWith("data:")) {
          found.push({ url: source.src, type: "audio", title: document.title });
        }
      });
    });

    // <embed> and <object> with media
    document.querySelectorAll("embed[src], object[data]").forEach((el) => {
      const src = el.src || el.data;
      if (src && isMediaUrl(src)) {
        found.push({ url: src, type: "video", title: document.title });
      }
    });

    // <iframe> with media URLs
    document.querySelectorAll("iframe[src]").forEach((iframe) => {
      if (isMediaUrl(iframe.src)) {
        found.push({ url: iframe.src, type: "video", title: document.title });
      }
    });

    // <a> links to media files
    document.querySelectorAll("a[href]").forEach((link) => {
      try {
        const href = link.href;
        if (isMediaUrl(href)) {
          found.push({
            url: href,
            type: getFileExtension(href).match(/\.(mp3|flac|wav|aac|ogg|wma|m4a)/) ? "audio" : "video",
            title: link.textContent.trim() || getFilenameFromUrl(href) || document.title,
          });
        }
      } catch (_e) { /* invalid URL */ }
    });

    return found;
  }

  function extractDownloadableLinks() {
    const found = [];
    document.querySelectorAll("a[href]").forEach((link) => {
      try {
        const href = link.href;
        const ext = getFileExtension(href);
        if (DOWNLOAD_EXTENSIONS.includes(ext)) {
          found.push({
            url: href,
            type: "file",
            title: link.textContent.trim() || getFilenameFromUrl(href),
            extension: ext,
          });
        }
      } catch (_e) { /* skip */ }
    });
    return found;
  }

  function getAllPageLinks() {
    const links = [];
    const seen = new Set();
    document.querySelectorAll("a[href]").forEach((link) => {
      try {
        const href = link.href;
        if (href && !seen.has(href) && href.startsWith("http")) {
          seen.add(href);
          links.push({
            url: href,
            text: link.textContent.trim().slice(0, 100),
            extension: getFileExtension(href),
          });
        }
      } catch (_e) { /* skip */ }
    });
    return links;
  }

  function sendVideosToBackground(videos) {
    videos.forEach((v) => {
      if (!videoSources.has(v.url)) {
        videoSources.add(v.url);
        detectedMedia.push(v);
        chrome.runtime.sendMessage({
          type: "video_found",
          url: v.url,
          mediaType: v.type,
          title: v.title,
          pageUrl: window.location.href,
          width: v.width || 0,
          height: v.height || 0,
          duration: v.duration || 0,
        });
      }
    });
  }

  // Floating "Download Video" panel (like IDM)
  function createFloatingPanel(videoElement) {
    removeFloatingPanel();

    const panel = document.createElement("div");
    panel.id = "kros-download-panel";
    panel.innerHTML = `
      <div id="kros-panel-content">
        <span id="kros-panel-icon">&#x2B07;</span>
        <span id="kros-panel-text">Descargar video</span>
        <span id="kros-panel-close">&times;</span>
      </div>
    `;
    const style = document.createElement("style");
    style.textContent = `
      #kros-download-panel {
        position: absolute;
        z-index: 2147483647;
        background: rgba(29, 185, 84, 0.92);
        border-radius: 8px;
        padding: 6px 14px;
        cursor: pointer;
        font-family: 'Segoe UI', system-ui, sans-serif;
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
        transition: opacity 0.2s, transform 0.2s;
        opacity: 0;
        transform: translateY(-4px);
        backdrop-filter: blur(8px);
        pointer-events: auto;
      }
      #kros-download-panel.visible {
        opacity: 1;
        transform: translateY(0);
      }
      #kros-panel-content {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #fff;
        font-size: 13px;
        font-weight: 600;
        white-space: nowrap;
      }
      #kros-panel-icon { font-size: 15px; }
      #kros-panel-close {
        margin-left: 6px;
        font-size: 16px;
        opacity: 0.7;
        cursor: pointer;
      }
      #kros-panel-close:hover { opacity: 1; }
      #kros-download-panel:hover {
        background: rgba(29, 185, 84, 1);
        box-shadow: 0 6px 20px rgba(0,0,0,0.5);
      }
    `;
    document.head.appendChild(style);
    document.body.appendChild(panel);

    // Position near top-right of video
    const rect = videoElement.getBoundingClientRect();
    panel.style.top = (window.scrollY + rect.top + 10) + "px";
    panel.style.left = (window.scrollX + rect.right - panel.offsetWidth - 10) + "px";

    requestAnimationFrame(() => panel.classList.add("visible"));

    panel.addEventListener("click", (e) => {
      if (e.target.id === "kros-panel-close") {
        removeFloatingPanel();
        return;
      }
      const src = videoElement.src || videoElement.currentSrc ||
        (videoElement.querySelector("source") || {}).src;
      if (src && !src.startsWith("blob:")) {
        chrome.runtime.sendMessage({
          type: "download_video",
          url: src,
          title: document.title,
          pageUrl: window.location.href,
        });
        panel.querySelector("#kros-panel-text").textContent = "Enviado!";
        setTimeout(removeFloatingPanel, 1500);
      }
    });

    panel.querySelector("#kros-panel-close").addEventListener("click", (e) => {
      e.stopPropagation();
      removeFloatingPanel();
    });

    floatingPanel = panel;
  }

  function removeFloatingPanel() {
    if (floatingPanel) {
      floatingPanel.remove();
      floatingPanel = null;
    }
  }

  // Show floating panel on video hover
  function attachVideoHoverListeners() {
    document.querySelectorAll("video").forEach((video) => {
      if (video.dataset.krosAttached) return;
      video.dataset.krosAttached = "true";

      video.addEventListener("mouseenter", () => {
        const src = video.src || video.currentSrc ||
          (video.querySelector("source") || {}).src;
        if (src && !src.startsWith("blob:")) {
          createFloatingPanel(video);
        }
      });

      video.addEventListener("mouseleave", (e) => {
        const panel = document.getElementById("kros-download-panel");
        if (panel && !panel.contains(e.relatedTarget)) {
          setTimeout(() => {
            const p = document.getElementById("kros-download-panel");
            if (p && !p.matches(":hover")) removeFloatingPanel();
          }, 300);
        }
      });
    });
  }

  // Intercept network requests for media (via PerformanceObserver)
  function monitorNetworkRequests() {
    if (!window.PerformanceObserver) return;
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const url = entry.name;
          if (url && isMediaUrl(url) && !videoSources.has(url)) {
            videoSources.add(url);
            const media = {
              url,
              type: "video",
              title: getFilenameFromUrl(url) || document.title,
              pageUrl: window.location.href,
            };
            detectedMedia.push(media);
            chrome.runtime.sendMessage({
              type: "video_found",
              ...media,
              mediaType: "video",
            });
          }
        }
      });
      observer.observe({ entryTypes: ["resource"] });
    } catch (_e) { /* not supported */ }
  }

  // ---- Click Interception for Download Links ----
  // Prevents Chrome's "Save As" dialog by catching clicks before the browser
  // processes them, sending the URL directly to KrosDownloadManager.

  const ALL_INTERCEPT_EXTENSIONS = [...new Set([...DOWNLOAD_EXTENSIONS, ...MEDIA_EXTENSIONS])];

  function shouldInterceptLink(link) {
    if (!link || !link.href) return false;
    const href = link.href;
    if (!href.startsWith("http")) return false;
    if (link.hasAttribute("download")) return true;
    const ext = getFileExtension(href);
    return ALL_INTERCEPT_EXTENSIONS.includes(ext);
  }

  function showCaptureToast(filename) {
    const existing = document.getElementById("kros-toast");
    if (existing) existing.remove();
    const toast = document.createElement("div");
    toast.id = "kros-toast";
    toast.textContent = "\u2B07 " + (filename || "Download") + " \u2192 KrosDownloadManager";
    Object.assign(toast.style, {
      position: "fixed", bottom: "20px", right: "20px", zIndex: "2147483647",
      background: "#1db954", color: "#fff", padding: "10px 18px",
      borderRadius: "8px", fontSize: "13px", fontFamily: "Segoe UI, system-ui, sans-serif",
      fontWeight: "600", boxShadow: "0 4px 16px rgba(0,0,0,.3)",
      opacity: "0", transition: "opacity .3s ease", pointerEvents: "none",
    });
    document.body.appendChild(toast);
    requestAnimationFrame(() => { toast.style.opacity = "1"; });
    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 400);
    }, 2500);
  }

  document.addEventListener("click", async (e) => {
    const link = e.target.closest("a[href]");
    if (!link || !shouldInterceptLink(link)) return;

    try {
      const response = await new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({ type: "check_status" }, (resp) => {
          if (chrome.runtime.lastError) reject(chrome.runtime.lastError);
          else resolve(resp);
        });
      });

      if (response && response.connected) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();

        const href = link.href;
        const filename = link.download || getFilenameFromUrl(href);
        chrome.runtime.sendMessage({
          type: "download_file",
          url: href,
          filename: filename,
          referrer: window.location.href,
        });
        showCaptureToast(filename);
      }
    } catch (_e) {
      // Extension context invalid or app not running — let browser handle normally
    }
  }, true); // Capture phase to intercept before other handlers

  // Initial scan
  setTimeout(() => {
    const videos = extractVideoSources();
    if (videos.length > 0) sendVideosToBackground(videos);
    attachVideoHoverListeners();
    monitorNetworkRequests();
  }, 2000);

  // Watch for dynamically added media
  const observer = new MutationObserver(() => {
    const videos = extractVideoSources();
    if (videos.length > 0) sendVideosToBackground(videos);
    attachVideoHoverListeners();
  });

  observer.observe(document.body, { childList: true, subtree: true });

  // Listen for messages from popup/background
  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type === "get_videos") {
      const videos = extractVideoSources();
      const allMedia = [...detectedMedia];
      videos.forEach((v) => {
        if (!videoSources.has(v.url)) {
          videoSources.add(v.url);
          allMedia.push(v);
        }
      });
      sendResponse({ videos: allMedia });
    } else if (msg.type === "get_all_links") {
      sendResponse({ links: getAllPageLinks() });
    } else if (msg.type === "get_downloadable_files") {
      sendResponse({ files: extractDownloadableLinks() });
    }
  });
})();
