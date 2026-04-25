// Background service worker for KrosDownloadManager extension
// Intercepts downloads, manages context menus, communicates with app

const API_URL = "http://localhost:29256";

const DOWNLOAD_EXTENSIONS = [
  ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
  ".exe", ".msi", ".dmg", ".deb", ".rpm", ".appimage",
  ".iso", ".img",
  ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
  ".mp3", ".flac", ".wav", ".aac", ".ogg", ".wma", ".m4a",
  ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v",
  ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff",
  ".torrent", ".apk", ".cab", ".bin",
];

const MIN_SIZE_BYTES = 1024 * 512; // 512 KB

let appConnected = false;
const detectedVideos = {};  // tabId -> [{url, title, type, ...}]

// ---- App Communication ----

async function checkAppStatus() {
  try {
    const resp = await fetch(`${API_URL}/status`, { method: "GET" });
    if (resp.ok) {
      const data = await resp.json();
      appConnected = true;
      return data;
    }
  } catch (_e) { /* app not running */ }
  appConnected = false;
  return null;
}

async function sendToApp(url, filename, referrer, isVideo) {
  try {
    const resp = await fetch(`${API_URL}/download`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url,
        filename: filename || "",
        referrer: referrer || "",
        is_video: isVideo || false,
      }),
    });
    return resp.ok;
  } catch (_e) {
    return false;
  }
}

async function sendBatchToApp(urls) {
  try {
    const resp = await fetch(`${API_URL}/download_batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urls }),
    });
    return resp.ok;
  } catch (_e) {
    return false;
  }
}

async function getFileInfo(url) {
  try {
    const resp = await fetch(`${API_URL}/file_info`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    if (resp.ok) return resp.json();
  } catch (_e) { /* ignore */ }
  return null;
}

// ---- Helpers ----

function hasDownloadExtension(url) {
  try {
    const pathname = new URL(url).pathname.toLowerCase();
    return DOWNLOAD_EXTENSIONS.some((ext) => pathname.endsWith(ext));
  } catch (_e) {
    return false;
  }
}

function getFilenameFromUrl(url) {
  try {
    const pathname = new URL(url).pathname;
    const parts = pathname.split("/");
    return decodeURIComponent(parts[parts.length - 1]) || "";
  } catch (_e) {
    return "";
  }
}

function isMediaContentType(contentType) {
  if (!contentType) return false;
  return contentType.startsWith("video/") ||
    contentType.startsWith("audio/") ||
    contentType === "application/octet-stream";
}

// ---- Download Interception ----

chrome.downloads.onCreated.addListener(async (item) => {
  const data = await chrome.storage.local.get("enabled");
  if (data.enabled === false) return;

  const url = item.finalUrl || item.url;
  if (!url || url.startsWith("blob:") || url.startsWith("data:") || url.startsWith("chrome:")) return;

  const isDownloadFile = hasDownloadExtension(url);
  const isLargeFile = item.totalBytes > MIN_SIZE_BYTES || item.totalBytes === -1;

  if (isDownloadFile || isLargeFile) {
    if (await checkAppStatus()) {
      chrome.downloads.cancel(item.id);
      chrome.downloads.erase({ id: item.id });
      const filename = item.filename ? item.filename.split(/[/\\]/).pop() : getFilenameFromUrl(url);
      await sendToApp(url, filename, item.referrer || "", false);
    }
  }
});

// ---- Context Menu ----

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "kros-download-link",
    title: "Descargar con KrosDownloadManager",
    contexts: ["link"],
  });
  chrome.contextMenus.create({
    id: "kros-download-video",
    title: "Descargar video con KrosDownloadManager",
    contexts: ["video", "audio"],
  });
  chrome.contextMenus.create({
    id: "kros-download-image",
    title: "Descargar imagen con KrosDownloadManager",
    contexts: ["image"],
  });
  chrome.contextMenus.create({
    id: "kros-download-all",
    title: "Descargar todos los enlaces de esta pagina",
    contexts: ["page"],
  });
  chrome.contextMenus.create({
    id: "kros-separator",
    type: "separator",
    contexts: ["page"],
  });
  chrome.contextMenus.create({
    id: "kros-send-page",
    title: "Enviar pagina a KrosDownloadManager",
    contexts: ["page"],
  });

  chrome.storage.local.set({ enabled: true });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const status = await checkAppStatus();

  if (info.menuItemId === "kros-download-link") {
    if (!status) { notifyAppNotRunning(); return; }
    const url = info.linkUrl;
    await sendToApp(url, getFilenameFromUrl(url), tab.url, false);
  } else if (info.menuItemId === "kros-download-video") {
    if (!status) { notifyAppNotRunning(); return; }
    const url = info.srcUrl;
    await sendToApp(url, "", tab.url, true);
  } else if (info.menuItemId === "kros-download-image") {
    if (!status) { notifyAppNotRunning(); return; }
    const url = info.srcUrl;
    await sendToApp(url, getFilenameFromUrl(url), tab.url, false);
  } else if (info.menuItemId === "kros-download-all") {
    if (!status) { notifyAppNotRunning(); return; }
    // Get all links from page and send to app
    chrome.tabs.sendMessage(tab.id, { type: "get_all_links" }, async (response) => {
      if (response && response.links) {
        const urls = response.links
          .filter((l) => hasDownloadExtension(l.url))
          .map((l) => ({ url: l.url, filename: getFilenameFromUrl(l.url) }));
        if (urls.length > 0) {
          await sendBatchToApp(urls);
        }
      }
    });
  } else if (info.menuItemId === "kros-send-page") {
    if (!status) { notifyAppNotRunning(); return; }
    await sendToApp(tab.url, "", "", false);
  }
});

function notifyAppNotRunning() {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/icon48.png",
    title: "KrosDownloadManager",
    message: "La aplicacion no esta ejecutandose. Abrela primero.",
  });
}

// ---- Message Handling ----

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "video_found") {
    const tabId = sender.tab ? sender.tab.id : -1;
    if (tabId >= 0) {
      if (!detectedVideos[tabId]) detectedVideos[tabId] = [];
      // Avoid duplicates
      if (!detectedVideos[tabId].some((v) => v.url === msg.url)) {
        detectedVideos[tabId].push({
          url: msg.url,
          title: msg.title,
          type: msg.mediaType,
          width: msg.width || 0,
          height: msg.height || 0,
          duration: msg.duration || 0,
          pageUrl: msg.pageUrl,
        });
      }
      // Update badge
      chrome.action.setBadgeText({
        text: String(detectedVideos[tabId].length),
        tabId,
      });
      chrome.action.setBadgeBackgroundColor({ color: "#1db954", tabId });
    }
    sendResponse({ received: true });
  } else if (msg.type === "download_video") {
    sendToApp(msg.url, msg.title || "", msg.pageUrl || "", true).then((ok) => {
      sendResponse({ success: ok });
    });
    return true;
  } else if (msg.type === "download_file") {
    sendToApp(msg.url, msg.filename || "", msg.referrer || "", false).then((ok) => {
      sendResponse({ success: ok });
    });
    return true;
  } else if (msg.type === "download_batch") {
    sendBatchToApp(msg.urls).then((ok) => {
      sendResponse({ success: ok });
    });
    return true;
  } else if (msg.type === "check_status") {
    checkAppStatus().then((data) => sendResponse({ connected: !!data, data }));
    return true;
  } else if (msg.type === "get_detected_videos") {
    const tabId = msg.tabId;
    sendResponse({ videos: detectedVideos[tabId] || [] });
  } else if (msg.type === "get_file_info") {
    getFileInfo(msg.url).then((info) => sendResponse({ info }));
    return true;
  }
});

// Clean up when tab closes
chrome.tabs.onRemoved.addListener((tabId) => {
  delete detectedVideos[tabId];
});

// Reset badge on navigation
chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "loading") {
    detectedVideos[tabId] = [];
    chrome.action.setBadgeText({ text: "", tabId });
  }
});

// Periodic status check
setInterval(checkAppStatus, 10000);
checkAppStatus();
