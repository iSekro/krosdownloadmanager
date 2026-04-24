const API_URL = "http://localhost:29256";
const DOWNLOAD_EXTENSIONS = [
  ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
  ".exe", ".msi", ".dmg", ".deb", ".rpm", ".appimage",
  ".iso", ".img",
  ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
  ".mp3", ".flac", ".wav", ".aac", ".ogg", ".wma", ".m4a",
  ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v",
  ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff",
  ".torrent",
];
const MIN_SIZE_BYTES = 1024 * 512; // 512 KB

let appConnected = false;

async function checkAppStatus() {
  try {
    const resp = await fetch(`${API_URL}/status`, { method: "GET" });
    if (resp.ok) {
      appConnected = true;
      return true;
    }
  } catch (_e) { /* app not running */ }
  appConnected = false;
  return false;
}

async function sendToApp(url, filename, referrer) {
  try {
    const resp = await fetch(`${API_URL}/download`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, filename: filename || "", referrer: referrer || "" }),
    });
    return resp.ok;
  } catch (_e) {
    return false;
  }
}

async function sendVideoToApp(url, title, pageUrl) {
  try {
    const resp = await fetch(`${API_URL}/download`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, filename: title || "", referrer: pageUrl || "", is_video: true }),
    });
    return resp.ok;
  } catch (_e) {
    return false;
  }
}

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

// Intercept downloads
chrome.downloads.onCreated.addListener(async (item) => {
  const enabled = (await chrome.storage.local.get("enabled")).enabled;
  if (enabled === false) return;

  const url = item.finalUrl || item.url;
  if (!url || url.startsWith("blob:") || url.startsWith("data:")) return;

  const isDownloadFile = hasDownloadExtension(url);
  const isLargeFile = item.totalBytes > MIN_SIZE_BYTES;

  if (isDownloadFile || isLargeFile) {
    if (await checkAppStatus()) {
      chrome.downloads.cancel(item.id);
      chrome.downloads.erase({ id: item.id });
      const filename = item.filename ? item.filename.split(/[/\\]/).pop() : getFilenameFromUrl(url);
      await sendToApp(url, filename, item.referrer || "");
    }
  }
});

// Context menu
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
    id: "kros-download-page",
    title: "Enviar a KrosDownloadManager",
    contexts: ["page"],
  });

  chrome.storage.local.set({ enabled: true });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (!(await checkAppStatus())) {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon48.png",
      title: "KrosDownloadManager",
      message: "La aplicación no está ejecutándose. Ábrela primero.",
    });
    return;
  }

  if (info.menuItemId === "kros-download-link") {
    const url = info.linkUrl;
    await sendToApp(url, getFilenameFromUrl(url), tab.url);
  } else if (info.menuItemId === "kros-download-video") {
    const url = info.srcUrl;
    await sendVideoToApp(url, "", tab.url);
  } else if (info.menuItemId === "kros-download-page") {
    const url = tab.url;
    await sendToApp(url, "", "");
  }
});

// Listen for video URLs from content script
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === "video_found") {
    sendResponse({ received: true });
  } else if (msg.type === "download_video") {
    sendVideoToApp(msg.url, msg.title, msg.pageUrl).then((ok) => {
      sendResponse({ success: ok });
    });
    return true;
  } else if (msg.type === "check_status") {
    checkAppStatus().then((ok) => sendResponse({ connected: ok }));
    return true;
  }
});

// Periodic status check
setInterval(checkAppStatus, 10000);
checkAppStatus();
