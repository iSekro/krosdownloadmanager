"""Main application window for KrosDownloadManager."""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from krosdownloadmanager import __version__
from krosdownloadmanager.core.config import ConfigManager
from krosdownloadmanager.core.download_engine import DownloadEngine, DownloadItem, DownloadStatus
from krosdownloadmanager.utils.helpers import (
    extract_urls_from_text,
    format_size,
    format_speed,
    get_asset_path,
    is_valid_url,
)

COLORS = {
    "bg_dark": "#1c1c1e",
    "bg_medium": "#2c2c2e",
    "bg_light": "#3a3a3c",
    "bg_sidebar": "#252528",
    "bg_elevated": "#323234",
    "accent": "#0a84ff",
    "accent_hover": "#409cff",
    "accent_subtle": "#0a84ff20",
    "text_primary": "#f5f5f7",
    "text_secondary": "#86868b",
    "text_tertiary": "#636366",
    "success": "#30d158",
    "warning": "#ff9f0a",
    "error": "#ff453a",
    "progress_bg": "#38383a",
    "row_even": "#1c1c1e",
    "row_odd": "#222224",
    "row_hover": "#2c2c2e",
    "border": "#38383a",
    "border_light": "#48484a",
    "separator": "#2c2c2e",
    "glass": "#2c2c2e",
}

FONT_FAMILY = "Segoe UI"


class DownloadRow(ctk.CTkFrame):
    """A single download row in the download list."""

    def __init__(self, master, item: DownloadItem, app: "MainWindow", **kwargs):
        super().__init__(master, **kwargs)
        self.item = item
        self.app = app
        self.selected = False

        self.configure(
            fg_color=COLORS["row_even"],
            corner_radius=10,
            height=62,
            border_width=1,
            border_color=COLORS["border"],
        )

        self.grid_columnconfigure(1, weight=1)

        icon = self._get_file_icon()
        self.icon_label = ctk.CTkLabel(
            self, text=icon, font=("Segoe UI Emoji", 18),
            width=44, height=44,
            text_color=COLORS["accent"],
            fg_color=COLORS["bg_elevated"],
            corner_radius=10,
        )
        self.icon_label.grid(row=0, column=0, padx=(12, 8), pady=9, rowspan=2)

        self.name_label = ctk.CTkLabel(
            self, text=item.filename, font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text_primary"], anchor="w",
        )
        self.name_label.grid(row=0, column=1, padx=4, pady=(10, 0), sticky="w")

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=1, column=1, padx=4, pady=(0, 10), sticky="w")

        size_text = format_size(item.file_size) if item.file_size > 0 else "Desconocido"
        self.size_label = ctk.CTkLabel(
            info_frame, text=size_text, font=(FONT_FAMILY, 10),
            text_color=COLORS["text_secondary"],
        )
        self.size_label.pack(side="left", padx=(0, 12))

        self.speed_label = ctk.CTkLabel(
            info_frame, text="", font=(FONT_FAMILY, 10),
            text_color=COLORS["text_tertiary"],
        )
        self.speed_label.pack(side="left", padx=(0, 12))

        self.eta_label = ctk.CTkLabel(
            info_frame, text="", font=(FONT_FAMILY, 10),
            text_color=COLORS["text_tertiary"],
        )
        self.eta_label.pack(side="left", padx=(0, 12))

        self.progress_bar = ctk.CTkProgressBar(
            self, width=160, height=6,
            progress_color=COLORS["accent"],
            fg_color=COLORS["progress_bg"],
            corner_radius=3,
        )
        self.progress_bar.grid(row=0, column=2, padx=8, pady=9, rowspan=2, sticky="e")
        self.progress_bar.set(item.progress / 100.0 if item.progress else 0)

        self.percent_label = ctk.CTkLabel(
            self, text=f"{item.progress:.0f}%", font=(FONT_FAMILY, 11),
            text_color=COLORS["text_secondary"], width=44,
        )
        self.percent_label.grid(row=0, column=3, padx=4, pady=9, rowspan=2)

        self.status_label = ctk.CTkLabel(
            self, text=self._status_text(), font=(FONT_FAMILY, 10, "bold"),
            text_color=self._status_color(), width=80,
        )
        self.status_label.grid(row=0, column=4, padx=4, pady=9, rowspan=2)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=0, column=5, padx=(4, 12), pady=9, rowspan=2)

        self.action_btn = ctk.CTkButton(
            btn_frame, text=self._action_icon(), width=30, height=30,
            font=("Segoe UI Emoji", 13),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["accent"],
            command=self._on_action,
            corner_radius=8,
            border_width=0,
        )
        self.action_btn.pack(side="left", padx=2)

        self.cancel_btn = ctk.CTkButton(
            btn_frame, text="\u2716", width=30, height=30,
            font=("Segoe UI Emoji", 13),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["error"],
            command=self._on_cancel,
            corner_radius=8,
            border_width=0,
        )
        self.cancel_btn.pack(side="left", padx=2)

        for widget in [self, self.icon_label, self.name_label, info_frame]:
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Button-3>", self._on_right_click)

        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)

    def _on_hover_enter(self, event=None) -> None:
        if not self.selected:
            self.configure(fg_color=COLORS["row_hover"], border_color=COLORS["border_light"])

    def _on_hover_leave(self, event=None) -> None:
        if not self.selected:
            self.configure(fg_color=COLORS["row_even"], border_color=COLORS["border"])

    def _get_file_icon(self) -> str:
        ext = os.path.splitext(self.item.filename)[1].lower()
        icon_map = {
            ".zip": "\U0001F4E6", ".rar": "\U0001F4E6", ".7z": "\U0001F4E6",
            ".tar": "\U0001F4E6", ".gz": "\U0001F4E6",
            ".pdf": "\U0001F4C4", ".doc": "\U0001F4C4", ".docx": "\U0001F4C4",
            ".txt": "\U0001F4C4",
            ".mp4": "\U0001F3AC", ".mkv": "\U0001F3AC", ".avi": "\U0001F3AC",
            ".mov": "\U0001F3AC", ".webm": "\U0001F3AC",
            ".mp3": "\U0001F3B5", ".flac": "\U0001F3B5", ".wav": "\U0001F3B5",
            ".aac": "\U0001F3B5",
            ".exe": "\U0001F4BF", ".msi": "\U0001F4BF",
            ".jpg": "\U0001F5BC", ".jpeg": "\U0001F5BC", ".png": "\U0001F5BC",
            ".gif": "\U0001F5BC", ".svg": "\U0001F5BC",
            ".iso": "\U0001F4C0",
        }
        return icon_map.get(ext, "\U0001F4C1")

    def _status_text(self) -> str:
        status_map = {
            DownloadStatus.QUEUED: "En cola",
            DownloadStatus.DOWNLOADING: "Descargando",
            DownloadStatus.PAUSED: "Pausado",
            DownloadStatus.COMPLETED: "Completado",
            DownloadStatus.ERROR: "Error",
            DownloadStatus.MERGING: "Uniendo...",
            DownloadStatus.CANCELLED: "Cancelado",
        }
        return status_map.get(self.item.status, "Desconocido")

    def _status_color(self) -> str:
        color_map = {
            DownloadStatus.QUEUED: COLORS["text_secondary"],
            DownloadStatus.DOWNLOADING: COLORS["accent"],
            DownloadStatus.PAUSED: COLORS["warning"],
            DownloadStatus.COMPLETED: COLORS["success"],
            DownloadStatus.ERROR: COLORS["error"],
            DownloadStatus.MERGING: COLORS["accent"],
            DownloadStatus.CANCELLED: COLORS["text_secondary"],
        }
        return color_map.get(self.item.status, COLORS["text_secondary"])

    def _action_icon(self) -> str:
        if self.item.status == DownloadStatus.DOWNLOADING:
            return "\u23F8"
        elif self.item.status in (DownloadStatus.PAUSED, DownloadStatus.ERROR, DownloadStatus.QUEUED):
            return "\u25B6"
        elif self.item.status == DownloadStatus.COMPLETED:
            return "\U0001F4C2"
        return "\u25B6"

    def _on_action(self) -> None:
        if self.item.status == DownloadStatus.DOWNLOADING:
            self.app.engine.pause_download(self.item.id)
        elif self.item.status in (DownloadStatus.PAUSED, DownloadStatus.ERROR, DownloadStatus.QUEUED):
            self.app.engine.resume_download(self.item.id)
        elif self.item.status == DownloadStatus.COMPLETED:
            path = self.item.save_path
            if os.path.exists(path):
                os.startfile(path) if hasattr(os, "startfile") else os.system(f'xdg-open "{path}"')

    def _on_cancel(self) -> None:
        self.app.engine.cancel_download(self.item.id)

    def _on_click(self, event=None) -> None:
        self.app.select_row(self)

    def _on_right_click(self, event=None) -> None:
        self.app.select_row(self)
        self.app.show_context_menu(event, self.item)

    def set_selected(self, selected: bool) -> None:
        self.selected = selected
        if selected:
            self.configure(fg_color=COLORS["bg_elevated"], border_color=COLORS["accent"])
        else:
            self.configure(fg_color=COLORS["row_even"], border_color=COLORS["border"])

    def update_display(self) -> None:
        self.progress_bar.set(self.item.progress / 100.0)
        self.percent_label.configure(text=f"{self.item.progress:.1f}%")
        self.status_label.configure(text=self._status_text(), text_color=self._status_color())
        self.action_btn.configure(text=self._action_icon())

        if self.item.status == DownloadStatus.DOWNLOADING:
            self.speed_label.configure(text=format_speed(self.item.speed))
            self.eta_label.configure(text=f"ETA: {self.item.eta}")
        else:
            self.speed_label.configure(text="")
            self.eta_label.configure(text="")

        downloaded_text = format_size(self.item.downloaded_bytes)
        total_text = format_size(self.item.file_size) if self.item.file_size > 0 else "?"
        self.size_label.configure(text=f"{downloaded_text} / {total_text}")


class AddDownloadDialog(ctk.CTkToplevel):
    """Dialog to add a new download."""

    def __init__(self, master, app: "MainWindow"):
        super().__init__(master)
        self.app = app
        self.result = None

        self.title("Nueva Descarga")
        self.geometry("560x400")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.after(100, self._center_window)

        header = ctk.CTkLabel(
            self, text="Nueva Descarga",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["text_primary"],
        )
        header.pack(pady=(24, 16))

        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.pack(fill="x", padx=28, pady=4)
        ctk.CTkLabel(url_frame, text="URL", font=(FONT_FAMILY, 11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.url_entry = ctk.CTkEntry(
            url_frame, height=36, font=(FONT_FAMILY, 12),
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
            placeholder_text="https://ejemplo.com/archivo.zip",
        )
        self.url_entry.pack(fill="x", pady=(4, 0))

        try:
            import pyperclip
            clip = pyperclip.paste()
            if clip and is_valid_url(clip.strip()):
                self.url_entry.insert(0, clip.strip())
        except Exception:
            pass

        name_frame = ctk.CTkFrame(self, fg_color="transparent")
        name_frame.pack(fill="x", padx=28, pady=4)
        ctk.CTkLabel(name_frame, text="Nombre del archivo (opcional)", font=(FONT_FAMILY, 11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(
            name_frame, height=36, font=(FONT_FAMILY, 12),
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
            placeholder_text="Se detecta autom\u00e1ticamente",
        )
        self.name_entry.pack(fill="x", pady=(4, 0))

        dir_frame = ctk.CTkFrame(self, fg_color="transparent")
        dir_frame.pack(fill="x", padx=28, pady=4)
        ctk.CTkLabel(dir_frame, text="Guardar en", font=(FONT_FAMILY, 11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")

        dir_inner = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_inner.pack(fill="x", pady=(4, 0))
        dir_inner.grid_columnconfigure(0, weight=1)

        self.dir_entry = ctk.CTkEntry(
            dir_inner, height=36, font=(FONT_FAMILY, 12),
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
        )
        self.dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.dir_entry.insert(0, app.config_manager.config.download_dir)

        browse_btn = ctk.CTkButton(
            dir_inner, text="\U0001F4C1", width=36, height=36,
            font=("Segoe UI Emoji", 14),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_light"],
            command=self._browse_dir, corner_radius=8,
        )
        browse_btn.grid(row=0, column=1)

        conn_frame = ctk.CTkFrame(self, fg_color="transparent")
        conn_frame.pack(fill="x", padx=28, pady=4)
        ctk.CTkLabel(conn_frame, text="Conexiones", font=(FONT_FAMILY, 11),
                      text_color=COLORS["text_secondary"]).pack(side="left")
        self.conn_slider = ctk.CTkSlider(
            conn_frame, from_=1, to=16, number_of_steps=15,
            width=180, progress_color=COLORS["accent"],
            fg_color=COLORS["progress_bg"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
        )
        self.conn_slider.set(app.config_manager.config.default_connections)
        self.conn_slider.pack(side="left", padx=10)
        self.conn_label = ctk.CTkLabel(
            conn_frame, text=str(app.config_manager.config.default_connections),
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["accent"], width=28,
        )
        self.conn_label.pack(side="left")
        self.conn_slider.configure(command=self._on_conn_change)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=28, pady=(18, 16))

        ctk.CTkButton(
            btn_frame, text="Descargar", font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            height=38, corner_radius=10,
            command=self._on_download,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="Cancelar", font=(FONT_FAMILY, 13),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_light"],
            text_color=COLORS["text_secondary"],
            height=38, corner_radius=10,
            command=self.destroy,
        ).pack(side="right")

    def _center_window(self) -> None:
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 560) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 400) // 2
        self.geometry(f"+{x}+{y}")

    def _browse_dir(self) -> None:
        directory = filedialog.askdirectory(
            initialdir=self.dir_entry.get(),
            title="Seleccionar carpeta de descarga",
        )
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def _on_conn_change(self, value) -> None:
        self.conn_label.configure(text=str(int(value)))

    def _on_download(self) -> None:
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("URL vac\u00eda", "Por favor, ingresa una URL.", parent=self)
            return

        if not is_valid_url(url):
            messagebox.showwarning("URL inv\u00e1lida", "La URL proporcionada no es v\u00e1lida.", parent=self)
            return

        save_path = self.dir_entry.get().strip()
        if not save_path:
            messagebox.showwarning("Carpeta vac\u00eda", "Selecciona una carpeta de destino.", parent=self)
            return

        self.result = {
            "url": url,
            "filename": self.name_entry.get().strip(),
            "save_path": save_path,
            "connections": int(self.conn_slider.get()),
        }
        self.destroy()


class BatchDownloadDialog(ctk.CTkToplevel):
    """Dialog to add multiple downloads at once."""

    def __init__(self, master, app: "MainWindow"):
        super().__init__(master)
        self.app = app
        self.result: list[dict] | None = None

        self.title("Descarga por Lotes")
        self.geometry("600x500")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.after(100, self._center_window)

        header = ctk.CTkLabel(
            self, text="Descarga por Lotes",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["text_primary"],
        )
        header.pack(pady=(24, 12))

        ctk.CTkLabel(
            self, text="Ingresa una URL por l\u00ednea",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=28)

        self.urls_text = ctk.CTkTextbox(
            self, height=200, font=("Consolas", 11),
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=10,
        )
        self.urls_text.pack(fill="x", padx=28, pady=(4, 8))

        dir_frame = ctk.CTkFrame(self, fg_color="transparent")
        dir_frame.pack(fill="x", padx=28, pady=4)
        ctk.CTkLabel(dir_frame, text="Guardar en", font=(FONT_FAMILY, 11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")

        dir_inner = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_inner.pack(fill="x", pady=(4, 0))
        dir_inner.grid_columnconfigure(0, weight=1)

        self.dir_entry = ctk.CTkEntry(
            dir_inner, height=36, font=(FONT_FAMILY, 12),
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
        )
        self.dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.dir_entry.insert(0, app.config_manager.config.download_dir)

        ctk.CTkButton(
            dir_inner, text="\U0001F4C1", width=36, height=36,
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_light"],
            command=self._browse_dir, corner_radius=8,
        ).grid(row=0, column=1)

        conn_frame = ctk.CTkFrame(self, fg_color="transparent")
        conn_frame.pack(fill="x", padx=28, pady=4)
        ctk.CTkLabel(conn_frame, text="Conexiones", font=(FONT_FAMILY, 11),
                      text_color=COLORS["text_secondary"]).pack(side="left")
        self.conn_slider = ctk.CTkSlider(
            conn_frame, from_=1, to=16, number_of_steps=15,
            width=160, progress_color=COLORS["accent"],
            fg_color=COLORS["progress_bg"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
        )
        self.conn_slider.set(app.config_manager.config.default_connections)
        self.conn_slider.pack(side="left", padx=10)
        self.conn_label = ctk.CTkLabel(
            conn_frame, text=str(app.config_manager.config.default_connections),
            font=(FONT_FAMILY, 12, "bold"), text_color=COLORS["accent"], width=28,
        )
        self.conn_label.pack(side="left")
        self.conn_slider.configure(command=lambda v: self.conn_label.configure(text=str(int(v))))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=28, pady=(14, 16))

        ctk.CTkButton(
            btn_frame, text="Descargar Todo", font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            height=38, corner_radius=10,
            command=self._on_download,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="Cancelar", font=(FONT_FAMILY, 13),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_light"],
            text_color=COLORS["text_secondary"],
            height=38, corner_radius=10,
            command=self.destroy,
        ).pack(side="right")

    def _center_window(self) -> None:
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 600) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 500) // 2
        self.geometry(f"+{x}+{y}")

    def _browse_dir(self) -> None:
        directory = filedialog.askdirectory(
            initialdir=self.dir_entry.get(),
            title="Seleccionar carpeta de descarga",
        )
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def _on_download(self) -> None:
        text = self.urls_text.get("1.0", tk.END).strip()
        urls = extract_urls_from_text(text)

        if not urls:
            messagebox.showwarning("Sin URLs", "No se encontraron URLs v\u00e1lidas.", parent=self)
            return

        save_path = self.dir_entry.get().strip()
        if not save_path:
            messagebox.showwarning("Carpeta vac\u00eda", "Selecciona una carpeta de destino.", parent=self)
            return

        self.result = [
            {
                "url": url,
                "filename": "",
                "save_path": save_path,
                "connections": int(self.conn_slider.get()),
            }
            for url in urls
        ]
        self.destroy()


class ScheduleDialog(ctk.CTkToplevel):
    """Dialog to schedule a download for a specific time."""

    def __init__(self, master, app: "MainWindow"):
        super().__init__(master)
        self.app = app
        self.result = None

        self.title("Programar Descarga")
        self.geometry("560x460")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.after(100, self._center_window)

        header = ctk.CTkLabel(
            self, text="Programar Descarga",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["text_primary"],
        )
        header.pack(pady=(24, 16))

        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.pack(fill="x", padx=28, pady=4)
        ctk.CTkLabel(url_frame, text="URL", font=(FONT_FAMILY, 11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.url_entry = ctk.CTkEntry(
            url_frame, height=36, font=(FONT_FAMILY, 12),
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
            placeholder_text="https://ejemplo.com/archivo.zip",
        )
        self.url_entry.pack(fill="x", pady=(4, 0))

        dir_frame = ctk.CTkFrame(self, fg_color="transparent")
        dir_frame.pack(fill="x", padx=28, pady=4)
        ctk.CTkLabel(dir_frame, text="Guardar en", font=(FONT_FAMILY, 11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")
        dir_inner = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_inner.pack(fill="x", pady=(4, 0))
        dir_inner.grid_columnconfigure(0, weight=1)
        self.dir_entry = ctk.CTkEntry(
            dir_inner, height=36, font=(FONT_FAMILY, 12),
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
        )
        self.dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.dir_entry.insert(0, app.config_manager.config.download_dir)
        ctk.CTkButton(
            dir_inner, text="\U0001F4C1", width=36, height=36,
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_light"],
            command=self._browse_dir, corner_radius=8,
        ).grid(row=0, column=1)

        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.pack(fill="x", padx=28, pady=8)
        ctk.CTkLabel(time_frame, text="Fecha y hora (AAAA-MM-DD HH:MM)", font=(FONT_FAMILY, 11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")

        import time as time_mod
        default_time = time_mod.strftime("%Y-%m-%d %H:%M", time_mod.localtime(time_mod.time() + 3600))

        self.time_entry = ctk.CTkEntry(
            time_frame, height=36, font=(FONT_FAMILY, 12),
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
            placeholder_text="2025-12-31 23:00",
        )
        self.time_entry.pack(fill="x", pady=(4, 0))
        self.time_entry.insert(0, default_time)

        conn_frame = ctk.CTkFrame(self, fg_color="transparent")
        conn_frame.pack(fill="x", padx=28, pady=4)
        ctk.CTkLabel(conn_frame, text="Conexiones", font=(FONT_FAMILY, 11),
                      text_color=COLORS["text_secondary"]).pack(side="left")
        self.conn_slider = ctk.CTkSlider(
            conn_frame, from_=1, to=16, number_of_steps=15,
            width=180, progress_color=COLORS["accent"],
            fg_color=COLORS["progress_bg"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
        )
        self.conn_slider.set(app.config_manager.config.default_connections)
        self.conn_slider.pack(side="left", padx=10)
        self.conn_label = ctk.CTkLabel(
            conn_frame, text=str(app.config_manager.config.default_connections),
            font=(FONT_FAMILY, 12, "bold"), text_color=COLORS["accent"], width=28,
        )
        self.conn_label.pack(side="left")
        self.conn_slider.configure(command=lambda v: self.conn_label.configure(text=str(int(v))))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=28, pady=(18, 16))

        ctk.CTkButton(
            btn_frame, text="Programar", font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            height=38, corner_radius=10,
            command=self._on_schedule,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="Cancelar", font=(FONT_FAMILY, 13),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_light"],
            text_color=COLORS["text_secondary"],
            height=38, corner_radius=10,
            command=self.destroy,
        ).pack(side="right")

    def _center_window(self) -> None:
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 560) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 460) // 2
        self.geometry(f"+{x}+{y}")

    def _browse_dir(self) -> None:
        directory = filedialog.askdirectory(
            initialdir=self.dir_entry.get(),
            title="Seleccionar carpeta de descarga",
        )
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def _on_schedule(self) -> None:
        url = self.url_entry.get().strip()
        if not url or not is_valid_url(url):
            messagebox.showwarning("URL inv\u00e1lida", "Ingresa una URL v\u00e1lida.", parent=self)
            return

        scheduled_time = self.time_entry.get().strip()
        if not scheduled_time:
            messagebox.showwarning("Hora vac\u00eda", "Ingresa la fecha y hora.", parent=self)
            return

        self.result = {
            "url": url,
            "filename": "",
            "save_path": self.dir_entry.get().strip(),
            "connections": int(self.conn_slider.get()),
            "scheduled_time": scheduled_time,
        }
        self.destroy()


class ChecksumDialog(ctk.CTkToplevel):
    """Dialog to show checksums for a completed download."""

    def __init__(self, master, item: DownloadItem):
        super().__init__(master)
        self.title(f"Checksums - {item.filename}")
        self.geometry("500x260")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.after(100, self._center_window)

        ctk.CTkLabel(
            self, text="Verificaci\u00f3n de integridad",
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(20, 12))

        ctk.CTkLabel(
            self, text=item.filename,
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=28, pady=(0, 10))

        for label, value in [("MD5", item.checksum_md5), ("SHA-256", item.checksum_sha256)]:
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", padx=28, pady=2)
            ctk.CTkLabel(frame, text=label, font=(FONT_FAMILY, 11, "bold"),
                          text_color=COLORS["text_secondary"], width=70).pack(side="left")
            entry = ctk.CTkEntry(
                frame, font=("Consolas", 10),
                fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
                text_color=COLORS["text_primary"], corner_radius=6,
            )
            entry.pack(side="left", fill="x", expand=True, padx=(4, 0))
            entry.insert(0, value or "N/A")
            entry.configure(state="disabled")

        ctk.CTkButton(
            self, text="Cerrar", font=(FONT_FAMILY, 12),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_light"],
            text_color=COLORS["text_secondary"],
            height=34, corner_radius=10,
            command=self.destroy,
        ).pack(pady=(12, 14))

    def _center_window(self) -> None:
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 500) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 260) // 2
        self.geometry(f"+{x}+{y}")


class SettingsDialog(ctk.CTkToplevel):
    """Settings dialog."""

    def __init__(self, master, app: "MainWindow"):
        super().__init__(master)
        self.app = app
        self.config = app.config_manager.config

        self.title("Configuraci\u00f3n")
        self.geometry("520x580")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.after(100, self._center_window)

        header = ctk.CTkLabel(
            self, text="Configuraci\u00f3n",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["text_primary"],
        )
        header.pack(pady=(24, 16))

        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
        )
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self._add_section(scroll, "Descargas")

        dir_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        dir_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(dir_frame, text="Carpeta por defecto:",
                      font=(FONT_FAMILY, 12), text_color=COLORS["text_primary"]).pack(anchor="w")
        dir_inner = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_inner.pack(fill="x", pady=(3, 0))
        dir_inner.grid_columnconfigure(0, weight=1)
        self.dir_entry = ctk.CTkEntry(
            dir_inner, height=35, font=(FONT_FAMILY, 11),
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
        )
        self.dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.dir_entry.insert(0, self.config.download_dir)
        ctk.CTkButton(
            dir_inner, text="\U0001F4C1", width=35, height=35,
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_light"],
            command=self._browse_dir, corner_radius=8,
        ).grid(row=0, column=1)

        conn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        conn_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(conn_frame, text="Conexiones por defecto:",
                      font=(FONT_FAMILY, 12), text_color=COLORS["text_primary"]).pack(anchor="w")
        conn_inner = ctk.CTkFrame(conn_frame, fg_color="transparent")
        conn_inner.pack(fill="x", pady=(3, 0))
        self.conn_slider = ctk.CTkSlider(
            conn_inner, from_=1, to=32, number_of_steps=31,
            width=200, progress_color=COLORS["accent"],
            fg_color=COLORS["progress_bg"], button_color=COLORS["accent"],
        )
        self.conn_slider.set(self.config.default_connections)
        self.conn_slider.pack(side="left")
        self.conn_label = ctk.CTkLabel(
            conn_inner, text=str(self.config.default_connections),
            font=(FONT_FAMILY, 12, "bold"), text_color=COLORS["accent"], width=30,
        )
        self.conn_label.pack(side="left", padx=10)
        self.conn_slider.configure(command=lambda v: self.conn_label.configure(text=str(int(v))))

        concurrent_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        concurrent_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(concurrent_frame, text="Descargas simult\u00e1neas:",
                      font=(FONT_FAMILY, 12), text_color=COLORS["text_primary"]).pack(anchor="w")
        concurrent_inner = ctk.CTkFrame(concurrent_frame, fg_color="transparent")
        concurrent_inner.pack(fill="x", pady=(3, 0))
        self.concurrent_slider = ctk.CTkSlider(
            concurrent_inner, from_=1, to=10, number_of_steps=9,
            width=200, progress_color=COLORS["accent"],
            fg_color=COLORS["progress_bg"], button_color=COLORS["accent"],
        )
        self.concurrent_slider.set(self.config.max_concurrent_downloads)
        self.concurrent_slider.pack(side="left")
        self.concurrent_label = ctk.CTkLabel(
            concurrent_inner, text=str(self.config.max_concurrent_downloads),
            font=(FONT_FAMILY, 12, "bold"), text_color=COLORS["accent"], width=30,
        )
        self.concurrent_label.pack(side="left", padx=10)
        self.concurrent_slider.configure(
            command=lambda v: self.concurrent_label.configure(text=str(int(v)))
        )

        self._add_section(scroll, "L\u00edmite de velocidad")
        speed_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        speed_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(speed_frame, text="L\u00edmite (KB/s, 0 = sin l\u00edmite):",
                      font=(FONT_FAMILY, 12), text_color=COLORS["text_primary"]).pack(anchor="w")
        self.speed_entry = ctk.CTkEntry(
            speed_frame, height=35, font=(FONT_FAMILY, 11), width=120,
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
        )
        self.speed_entry.pack(anchor="w", pady=(3, 0))
        self.speed_entry.insert(0, str(self.config.speed_limit // 1024))

        self._add_section(scroll, "Proxy")
        self.proxy_var = ctk.BooleanVar(value=self.config.proxy_enabled)
        ctk.CTkCheckBox(
            scroll, text="Usar proxy", variable=self.proxy_var,
            font=(FONT_FAMILY, 12), text_color=COLORS["text_primary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
        ).pack(anchor="w", pady=5)

        proxy_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        proxy_frame.pack(fill="x", pady=3)
        ctk.CTkLabel(proxy_frame, text="Proxy (ej: http://proxy:8080):",
                      font=(FONT_FAMILY, 12), text_color=COLORS["text_primary"]).pack(anchor="w")
        self.proxy_entry = ctk.CTkEntry(
            proxy_frame, height=35, font=(FONT_FAMILY, 11),
            fg_color=COLORS["bg_medium"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text="http://proxy:8080",
        )
        self.proxy_entry.pack(fill="x", pady=(3, 0))
        if self.config.proxy:
            self.proxy_entry.insert(0, self.config.proxy)

        self._add_section(scroll, "Interfaz")
        self.theme_var = ctk.StringVar(value=self.config.theme)
        theme_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        theme_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(theme_frame, text="Tema:", font=(FONT_FAMILY, 12),
                      text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkRadioButton(
            theme_frame, text="Oscuro", variable=self.theme_var, value="dark",
            font=(FONT_FAMILY, 11), text_color=COLORS["text_primary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
        ).pack(side="left", padx=(15, 10))
        ctk.CTkRadioButton(
            theme_frame, text="Claro", variable=self.theme_var, value="light",
            font=(FONT_FAMILY, 11), text_color=COLORS["text_primary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
        ).pack(side="left")

        self.clipboard_var = ctk.BooleanVar(value=self.config.clipboard_monitoring)
        ctk.CTkCheckBox(
            scroll, text="Monitorear portapapeles", variable=self.clipboard_var,
            font=(FONT_FAMILY, 12), text_color=COLORS["text_primary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
        ).pack(anchor="w", pady=5)

        self.tray_var = ctk.BooleanVar(value=self.config.minimize_to_tray)
        ctk.CTkCheckBox(
            scroll, text="Minimizar a bandeja del sistema", variable=self.tray_var,
            font=(FONT_FAMILY, 12), text_color=COLORS["text_primary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
        ).pack(anchor="w", pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkButton(
            btn_frame, text="Guardar", font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            height=38, corner_radius=10,
            command=self._save,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="Cancelar", font=(FONT_FAMILY, 13),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_light"],
            text_color=COLORS["text_secondary"],
            height=38, corner_radius=10,
            command=self.destroy,
        ).pack(side="right")

    def _add_section(self, parent, text: str) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(14, 4))
        ctk.CTkLabel(
            frame, text=text, font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w")
        separator = ctk.CTkFrame(frame, fg_color=COLORS["border"], height=1)
        separator.pack(fill="x", pady=(4, 0))

    def _center_window(self) -> None:
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 520) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 580) // 2
        self.geometry(f"+{x}+{y}")

    def _browse_dir(self) -> None:
        directory = filedialog.askdirectory(
            initialdir=self.dir_entry.get(),
            title="Seleccionar carpeta",
        )
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def _save(self) -> None:
        self.config.download_dir = self.dir_entry.get().strip()
        self.config.default_connections = int(self.conn_slider.get())
        self.config.max_concurrent_downloads = int(self.concurrent_slider.get())
        self.config.theme = self.theme_var.get()
        self.config.clipboard_monitoring = self.clipboard_var.get()
        self.config.minimize_to_tray = self.tray_var.get()
        self.config.proxy_enabled = self.proxy_var.get()
        self.config.proxy = self.proxy_entry.get().strip()

        try:
            speed_kb = int(self.speed_entry.get().strip())
            self.config.speed_limit = max(0, speed_kb * 1024)
        except ValueError:
            self.config.speed_limit = 0

        self.app.config_manager.save_config()
        self.app.engine.global_speed_limit = self.config.speed_limit
        self.app.engine.default_connections = self.config.default_connections
        self.app.engine.proxy = self.config.proxy if self.config.proxy_enabled else ""

        self.destroy()


class AboutDialog(ctk.CTkToplevel):
    """About dialog showing app information."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Acerca de")
        self.geometry("400x360")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.after(100, self._center_window)

        ctk.CTkLabel(
            self, text="\u2B07",
            font=("Segoe UI Emoji", 40),
            text_color=COLORS["accent"],
        ).pack(pady=(24, 4))

        ctk.CTkLabel(
            self, text="KrosDownloadManager",
            font=(FONT_FAMILY, 20, "bold"),
            text_color=COLORS["text_primary"],
        ).pack()

        ctk.CTkLabel(
            self, text=f"Versi\u00f3n {__version__}",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text_secondary"],
        ).pack(pady=(2, 12))

        info_text = (
            "Gestor de descargas portable para Windows\n\n"
            "Multi-hilo \u00b7 Pausar/Reanudar \u00b7 Programar\n"
            "Proxy \u00b7 Checksums \u00b7 Lotes \u00b7 Portapapeles\n"
            "MediaFire \u00b7 Google Drive \u00b7 Dropbox"
        )
        ctk.CTkLabel(
            self, text=info_text,
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_tertiary"],
            justify="center",
        ).pack(padx=28)

        ctk.CTkLabel(
            self, text="Hecho por iSekro",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=COLORS["accent"],
        ).pack(pady=(12, 4))

        ctk.CTkButton(
            self, text="Cerrar", font=(FONT_FAMILY, 12),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_light"],
            text_color=COLORS["text_secondary"],
            height=32, corner_radius=10,
            command=self.destroy,
        ).pack(pady=(4, 14))

    def _center_window(self) -> None:
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 400) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 360) // 2
        self.geometry(f"+{x}+{y}")


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.config_manager = ConfigManager()
        config = self.config_manager.config

        ctk.set_appearance_mode("dark" if config.theme == "dark" else "light")

        self.title("KrosDownloadManager v1.0")
        self.geometry(f"{config.window_width}x{config.window_height}")
        self.minsize(900, 500)
        self.configure(fg_color=COLORS["bg_dark"])

        self._set_icon()

        proxy = config.proxy if config.proxy_enabled else ""
        self.engine = DownloadEngine(
            temp_dir=config.temp_dir,
            max_concurrent_downloads=config.max_concurrent_downloads,
            default_connections=config.default_connections,
            speed_limit=config.speed_limit,
            proxy=proxy,
        )

        self.engine.on_progress = self._on_progress
        self.engine.on_status_change = self._on_status_change
        self.engine.on_complete = self._on_complete
        self.engine.on_error = self._on_error

        self.download_rows: dict[str, DownloadRow] = {}
        self.selected_row: DownloadRow | None = None
        self._update_pending = False
        self._clipboard_last = ""
        self._filter = "all"
        self._tray_icon = None

        self._build_ui()
        self._bind_shortcuts()
        self._load_downloads()

        if config.clipboard_monitoring:
            self._start_clipboard_monitor()

        self._start_ui_updater()

        if config.minimize_to_tray:
            self._setup_tray()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _set_icon(self) -> None:
        """Set the window icon."""
        try:
            icon_path = get_asset_path("icon.png")
            if os.path.exists(icon_path):
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.iconphoto(True, photo)
                self._icon_photo = photo
        except Exception:
            pass

    def _setup_tray(self) -> None:
        """Set up system tray icon."""
        try:
            import pystray
            from PIL import Image

            icon_path = get_asset_path("icon.png")
            if not os.path.exists(icon_path):
                return

            tray_image = Image.open(icon_path).resize((64, 64))

            menu = pystray.Menu(
                pystray.MenuItem("Mostrar", self._tray_show),
                pystray.MenuItem("Nueva descarga", self._tray_new_download),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Salir", self._tray_quit),
            )

            self._tray_icon = pystray.Icon(
                "KrosDownloadManager",
                tray_image,
                "KrosDownloadManager",
                menu,
            )
            threading.Thread(target=self._tray_icon.run, daemon=True).start()
        except Exception:
            pass

    def _tray_show(self, *args) -> None:
        self.after(0, self._show_window)

    def _show_window(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()

    def _tray_new_download(self, *args) -> None:
        self.after(0, self._show_and_add_download)

    def _show_and_add_download(self) -> None:
        self._show_window()
        self._add_download()

    def _tray_quit(self, *args) -> None:
        self.after(0, self._force_close)

    def _force_close(self) -> None:
        self._save_downloads()
        self.config_manager.config.window_width = self.winfo_width()
        self.config_manager.config.window_height = self.winfo_height()
        self.config_manager.save_config()
        self.engine.shutdown()
        if self._tray_icon:
            self._tray_icon.stop()
        self.destroy()

    def _bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts."""
        self.bind("<Control-n>", lambda e: self._add_download())
        self.bind("<Control-N>", lambda e: self._add_download())
        self.bind("<Control-b>", lambda e: self._batch_download())
        self.bind("<Control-B>", lambda e: self._batch_download())
        self.bind("<Control-t>", lambda e: self._schedule_download())
        self.bind("<Control-T>", lambda e: self._schedule_download())
        self.bind("<Delete>", lambda e: self._delete_selected())
        self.bind("<Control-p>", lambda e: self._pause_selected())
        self.bind("<Control-P>", lambda e: self._pause_selected())
        self.bind("<Control-r>", lambda e: self._resume_selected())
        self.bind("<Control-R>", lambda e: self._resume_selected())
        self.bind("<Control-a>", lambda e: self._resume_all())
        self.bind("<Control-A>", lambda e: self._resume_all())
        self.bind("<Control-q>", lambda e: self._on_close())
        self.bind("<Control-Q>", lambda e: self._on_close())
        self.bind("<F1>", lambda e: self._show_about())
        self.bind("<Control-comma>", lambda e: self._open_settings())

    def _build_ui(self) -> None:
        """Build the main user interface."""
        self._build_toolbar()
        self._build_sidebar()
        self._build_main_area()
        self._build_statusbar()

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], height=48, corner_radius=0)
        toolbar.pack(fill="x", padx=0, pady=0)
        toolbar.pack_propagate(False)

        sep = ctk.CTkFrame(self, fg_color=COLORS["border"], height=1, corner_radius=0)
        sep.pack(fill="x")

        logo = ctk.CTkLabel(
            toolbar, text="\u2B07 Kros",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLORS["accent"],
        )
        logo.pack(side="left", padx=(16, 12))

        btn_data = [
            ("\u2795 Nueva", self._add_download),
            ("\U0001F4E5 Lotes", self._batch_download),
            ("\u23F0 Programar", self._schedule_download),
            (None, None),
            ("\u25B6", self._resume_selected),
            ("\u23F8", self._pause_selected),
            ("\u23F9", self._cancel_selected),
            ("\U0001F5D1", self._delete_selected),
            (None, None),
            ("\u25B6\u25B6", self._resume_all),
            ("\u23F8\u23F8", self._pause_all),
            (None, None),
            ("\u2699", self._open_settings),
            ("\u2139", self._show_about),
        ]

        for text, cmd in btn_data:
            if text is None:
                div = ctk.CTkFrame(toolbar, fg_color=COLORS["border"], width=1, height=24)
                div.pack(side="left", padx=4, pady=12)
                continue
            btn = ctk.CTkButton(
                toolbar, text=text, font=(FONT_FAMILY, 11),
                fg_color="transparent", hover_color=COLORS["bg_medium"],
                text_color=COLORS["text_secondary"],
                height=32, corner_radius=8,
                command=cmd,
                width=0,
            )
            btn.pack(side="left", padx=2, pady=8)

    def _build_sidebar(self) -> None:
        self._main_container = ctk.CTkFrame(self, fg_color="transparent")
        self._main_container.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(
            self._main_container, fg_color=COLORS["bg_sidebar"],
            width=170, corner_radius=0,
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar, text="Categor\u00edas", font=(FONT_FAMILY, 11, "bold"),
            text_color=COLORS["text_tertiary"],
        ).pack(pady=(14, 8), padx=12, anchor="w")

        categories = [
            ("Todas", "all", "\U0001F4E5"),
            ("Descargando", "downloading", "\u2B07"),
            ("Completadas", "completed", "\u2705"),
            ("Pausadas", "paused", "\u23F8"),
            ("Errores", "error", "\u26A0"),
            ("Programadas", "scheduled", "\u23F0"),
            ("Comprimidos", "compressed", "\U0001F4E6"),
            ("Documentos", "documents", "\U0001F4C4"),
            ("Video", "video", "\U0001F3AC"),
            ("M\u00fasica", "music", "\U0001F3B5"),
            ("Programas", "programs", "\U0001F4BF"),
            ("Im\u00e1genes", "images", "\U0001F5BC"),
        ]

        self._category_buttons = {}
        for name, filter_key, icon in categories:
            is_active = filter_key == "all"
            btn = ctk.CTkButton(
                sidebar, text=f" {icon}  {name}",
                font=(FONT_FAMILY, 11), anchor="w",
                fg_color=COLORS["bg_elevated"] if is_active else "transparent",
                hover_color=COLORS["bg_elevated"],
                text_color=COLORS["text_primary"] if is_active else COLORS["text_secondary"],
                height=32, corner_radius=8,
                command=lambda fk=filter_key: self._set_filter(fk),
            )
            btn.pack(fill="x", padx=8, pady=1)
            self._category_buttons[filter_key] = btn

        shortcut_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        shortcut_frame.pack(side="bottom", fill="x", padx=12, pady=10)
        ctk.CTkLabel(
            shortcut_frame, text="Atajos",
            font=(FONT_FAMILY, 9, "bold"),
            text_color=COLORS["text_tertiary"],
        ).pack(anchor="w", pady=(0, 2))
        shortcuts = [
            "Ctrl+N  Nueva",
            "Ctrl+B  Lotes",
            "Ctrl+T  Programar",
            "Ctrl+P  Pausar",
            "Ctrl+R  Reanudar",
            "Del     Eliminar",
            "Ctrl+Q  Salir",
            "F1      Info",
        ]
        for s in shortcuts:
            ctk.CTkLabel(
                shortcut_frame, text=s,
                font=("Consolas", 8),
                text_color=COLORS["text_tertiary"],
                anchor="w",
            ).pack(anchor="w")

    def _build_main_area(self) -> None:
        main_frame = ctk.CTkFrame(self._main_container, fg_color=COLORS["bg_dark"], corner_radius=0)
        main_frame.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_dark"], height=32, corner_radius=0)
        header.pack(fill="x", padx=8, pady=(6, 0))
        header.pack_propagate(False)

        cols = [
            ("", 44), ("Nombre", 0), ("Tama\u00f1o", 90),
            ("Progreso", 200), ("Estado", 80), ("", 76),
        ]
        for col_name, width in cols:
            lbl = ctk.CTkLabel(
                header, text=col_name, font=(FONT_FAMILY, 10),
                text_color=COLORS["text_tertiary"],
                width=width if width > 0 else 0,
            )
            if width > 0:
                lbl.pack(side="left", padx=4)
            else:
                lbl.pack(side="left", padx=4, expand=True, fill="x")

        sep = ctk.CTkFrame(main_frame, fg_color=COLORS["border"], height=1, corner_radius=0)
        sep.pack(fill="x", padx=8)

        self.download_list = ctk.CTkScrollableFrame(
            main_frame, fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["border"],
        )
        self.download_list.pack(fill="both", expand=True, padx=6, pady=4)

        self._empty_label = ctk.CTkLabel(
            self.download_list,
            text="\u2B07\n\nNo hay descargas\n\nCtrl+N para agregar",
            font=(FONT_FAMILY, 14),
            text_color=COLORS["text_tertiary"],
        )

    def _build_statusbar(self) -> None:
        sep = ctk.CTkFrame(self, fg_color=COLORS["border"], height=1, corner_radius=0)
        sep.pack(fill="x", side="bottom")
        statusbar = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], height=26, corner_radius=0)
        statusbar.pack(fill="x", side="bottom")
        statusbar.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            statusbar, text="Listo", font=(FONT_FAMILY, 9),
            text_color=COLORS["text_tertiary"],
        )
        self.status_label.pack(side="left", padx=12)

        self.speed_status = ctk.CTkLabel(
            statusbar, text="", font=(FONT_FAMILY, 9),
            text_color=COLORS["text_tertiary"],
        )
        self.speed_status.pack(side="right", padx=12)

        self.count_label = ctk.CTkLabel(
            statusbar, text="0 descargas", font=(FONT_FAMILY, 9),
            text_color=COLORS["text_tertiary"],
        )
        self.count_label.pack(side="right", padx=12)

    def show_context_menu(self, event, item: DownloadItem) -> None:
        """Show right-click context menu for a download."""
        menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_elevated"], fg=COLORS["text_primary"],
                       activebackground=COLORS["accent"], activeforeground=COLORS["text_primary"],
                       font=(FONT_FAMILY, 10), relief="flat", bd=1)

        if item.status == DownloadStatus.DOWNLOADING:
            menu.add_command(label="\u23F8 Pausar", command=lambda: self.engine.pause_download(item.id))
        elif item.status in (DownloadStatus.PAUSED, DownloadStatus.ERROR, DownloadStatus.QUEUED):
            menu.add_command(label="\u25B6 Reanudar", command=lambda: self.engine.resume_download(item.id))

        if item.status == DownloadStatus.DOWNLOADING:
            menu.add_command(label="\u23F9 Cancelar", command=lambda: self.engine.cancel_download(item.id))

        menu.add_separator()

        if item.status == DownloadStatus.COMPLETED:
            menu.add_command(label="\U0001F4C2 Abrir carpeta", command=lambda: self._open_folder(item))
            menu.add_command(label="\U0001F512 Ver checksums", command=lambda: ChecksumDialog(self, item))
            menu.add_separator()

        menu.add_command(label="\U0001F4CB Copiar URL", command=lambda: self._copy_url(item))
        menu.add_separator()
        menu.add_command(label="\U0001F5D1 Eliminar de la lista", command=self._delete_selected)
        menu.add_command(label="\U0001F5D1 Eliminar con archivo",
                         command=lambda: self._delete_with_file(item))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _open_folder(self, item: DownloadItem) -> None:
        """Open the folder containing the downloaded file."""
        path = item.save_path
        if os.path.exists(path):
            if hasattr(os, "startfile"):
                os.startfile(path)
            else:
                os.system(f'xdg-open "{path}"')

    def _copy_url(self, item: DownloadItem) -> None:
        """Copy download URL to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(item.url)

    def _delete_with_file(self, item: DownloadItem) -> None:
        """Delete download and the downloaded file."""
        if not messagebox.askyesno("Confirmar", f"\u00bfEliminar '{item.filename}' y su archivo?"):
            return
        self.engine.remove_download(item.id, delete_file=True)
        row = self.download_rows.get(item.id)
        if row:
            row.destroy()
            del self.download_rows[item.id]
        self.selected_row = None
        self._update_counts()
        if not self.download_rows:
            self._empty_label.pack(pady=50)

    def _add_download(self) -> None:
        dialog = AddDownloadDialog(self, self)
        self.wait_window(dialog)

        if dialog.result:
            r = dialog.result
            threading.Thread(
                target=self._add_download_thread,
                args=(r["url"], r["save_path"], r["filename"], r["connections"]),
                daemon=True,
            ).start()

    def _batch_download(self) -> None:
        """Open batch download dialog."""
        dialog = BatchDownloadDialog(self, self)
        self.wait_window(dialog)

        if dialog.result:
            for r in dialog.result:
                threading.Thread(
                    target=self._add_download_thread,
                    args=(r["url"], r["save_path"], r["filename"], r["connections"]),
                    daemon=True,
                ).start()

    def _schedule_download(self) -> None:
        """Open schedule download dialog."""
        dialog = ScheduleDialog(self, self)
        self.wait_window(dialog)

        if dialog.result:
            r = dialog.result
            threading.Thread(
                target=self._add_scheduled_download_thread,
                args=(r["url"], r["save_path"], r["filename"],
                      r["connections"], r["scheduled_time"]),
                daemon=True,
            ).start()

    def _add_scheduled_download_thread(
        self, url: str, save_path: str, filename: str, connections: int, scheduled_time: str
    ) -> None:
        self.after(0, lambda: self.status_label.configure(
            text=f"Programando descarga de {url[:50]}..."
        ))

        try:
            info = self.engine.get_file_info(url)
            if not filename:
                filename = info["filename"]

            import time as time_mod

            from krosdownloadmanager.core.download_engine import DownloadItem as DI

            actual_url = info.get("url", url)
            item = DI(
                url=actual_url,
                save_path=save_path,
                filename=filename,
                file_size=info["file_size"],
                supports_resume=info["supports_resume"],
                content_type=info["content_type"],
                num_connections=connections or self.engine.default_connections,
                date_added=time_mod.strftime("%Y-%m-%d %H:%M:%S"),
                speed_limit=self.engine.global_speed_limit,
                scheduled_time=scheduled_time,
            )

            if not item.supports_resume or item.file_size == 0:
                item.num_connections = 1

            self.engine.downloads[item.id] = item
            self.engine._stop_events[item.id] = threading.Event()
            self.engine._pause_events[item.id] = threading.Event()
            self.engine._pause_events[item.id].set()

            self.after(0, lambda: self._add_row(item))
            self.after(0, lambda: self.status_label.configure(
                text=f"Programada: {item.filename} para {scheduled_time}"
            ))
        except Exception as exc:
            err_msg = str(exc)
            self.after(0, lambda: messagebox.showerror(
                "Error", f"No se pudo programar la descarga:\n{err_msg}"
            ))

    def _add_download_thread(self, url: str, save_path: str, filename: str, connections: int) -> None:
        from krosdownloadmanager.utils.url_resolver import needs_resolution
        if needs_resolution(url):
            self.after(0, lambda: self.status_label.configure(text="Resolviendo enlace de descarga..."))
        else:
            self.after(0, lambda: self.status_label.configure(text=f"Obteniendo info de {url[:50]}..."))

        try:
            item = self.engine.add_download(
                url=url,
                save_path=save_path,
                filename=filename,
                num_connections=connections,
                start_immediately=True,
            )
            self.after(0, lambda: self._add_row(item))
            self.after(0, lambda: self.status_label.configure(
                text=f"Descargando: {item.filename}"
            ))
        except Exception as exc:
            err_msg = str(exc)
            self.after(0, lambda: messagebox.showerror("Error", f"No se pudo iniciar la descarga:\n{err_msg}"))

    def _add_row(self, item: DownloadItem) -> None:
        if self._empty_label.winfo_ismapped():
            self._empty_label.pack_forget()

        row = DownloadRow(self.download_list, item, self)
        row.pack(fill="x", padx=4, pady=2)
        self.download_rows[item.id] = row
        self._update_counts()

    def select_row(self, row: DownloadRow) -> None:
        if self.selected_row:
            self.selected_row.set_selected(False)
        self.selected_row = row
        row.set_selected(True)

    def _resume_selected(self) -> None:
        if self.selected_row:
            self.engine.resume_download(self.selected_row.item.id)

    def _pause_selected(self) -> None:
        if self.selected_row:
            self.engine.pause_download(self.selected_row.item.id)

    def _cancel_selected(self) -> None:
        if self.selected_row:
            self.engine.cancel_download(self.selected_row.item.id)

    def _delete_selected(self) -> None:
        if not self.selected_row:
            return

        item = self.selected_row.item
        if item.status == DownloadStatus.DOWNLOADING:
            if not messagebox.askyesno("Confirmar", "La descarga est\u00e1 en progreso. \u00bfEliminar?"):
                return

        self.engine.remove_download(item.id, delete_file=False)
        self.selected_row.destroy()
        del self.download_rows[item.id]
        self.selected_row = None
        self._update_counts()

        if not self.download_rows:
            self._empty_label.pack(pady=50)

    def _resume_all(self) -> None:
        for download_id, item in self.engine.downloads.items():
            if item.status in (DownloadStatus.PAUSED, DownloadStatus.QUEUED, DownloadStatus.ERROR):
                self.engine.resume_download(download_id)

    def _pause_all(self) -> None:
        for download_id, item in self.engine.downloads.items():
            if item.status == DownloadStatus.DOWNLOADING:
                self.engine.pause_download(download_id)

    def _open_settings(self) -> None:
        SettingsDialog(self, self)

    def _show_about(self) -> None:
        AboutDialog(self)

    def _set_filter(self, filter_key: str) -> None:
        self._filter = filter_key

        for key, btn in self._category_buttons.items():
            is_active = key == filter_key
            btn.configure(
                fg_color=COLORS["bg_elevated"] if is_active else "transparent",
                text_color=COLORS["text_primary"] if is_active else COLORS["text_secondary"],
            )

        self._apply_filter()

    def _apply_filter(self) -> None:
        status_map = {
            "downloading": DownloadStatus.DOWNLOADING,
            "completed": DownloadStatus.COMPLETED,
            "paused": DownloadStatus.PAUSED,
            "error": DownloadStatus.ERROR,
        }

        category_ext_map = {
            "compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
            "documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"],
            "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
            "music": [".mp3", ".flac", ".wav", ".aac", ".ogg", ".wma", ".m4a"],
            "programs": [".exe", ".msi", ".dmg", ".deb", ".rpm", ".apk"],
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        }

        for download_id, row in self.download_rows.items():
            show = True

            if self._filter in status_map:
                show = row.item.status == status_map[self._filter]
            elif self._filter == "scheduled":
                show = bool(row.item.scheduled_time) and row.item.status == DownloadStatus.QUEUED
            elif self._filter in category_ext_map:
                ext = os.path.splitext(row.item.filename)[1].lower()
                show = ext in category_ext_map[self._filter]

            if show:
                if not row.winfo_ismapped():
                    row.pack(fill="x", padx=4, pady=2)
            else:
                if row.winfo_ismapped():
                    row.pack_forget()

    def _on_progress(self, item: DownloadItem) -> None:
        if not self._update_pending:
            self._update_pending = True
            self.after(100, self._batch_update)

    def _on_status_change(self, item: DownloadItem) -> None:
        self.after(0, lambda: self._update_row(item.id))

    def _on_complete(self, item: DownloadItem) -> None:
        self.after(0, lambda: self.status_label.configure(
            text=f"Completado: {item.filename}"
        ))
        self._save_downloads()

    def _on_error(self, item: DownloadItem) -> None:
        self.after(0, lambda: self.status_label.configure(
            text=f"Error: {item.filename} - {item.error_message}"
        ))

    def _batch_update(self) -> None:
        self._update_pending = False
        for download_id, row in self.download_rows.items():
            if row.item.status == DownloadStatus.DOWNLOADING:
                row.update_display()

        total_speed = sum(
            item.speed for item in self.engine.downloads.values()
            if item.status == DownloadStatus.DOWNLOADING
        )
        if total_speed > 0:
            self.speed_status.configure(text=f"Velocidad total: {format_speed(total_speed)}")
        else:
            self.speed_status.configure(text="")

    def _update_row(self, download_id: str) -> None:
        row = self.download_rows.get(download_id)
        if row:
            row.update_display()
        self._update_counts()

    def _update_counts(self) -> None:
        total = len(self.engine.downloads)
        active = sum(
            1 for item in self.engine.downloads.values()
            if item.status == DownloadStatus.DOWNLOADING
        )
        scheduled = sum(
            1 for item in self.engine.downloads.values()
            if item.scheduled_time and item.status == DownloadStatus.QUEUED
        )
        parts = [f"{total} descargas", f"{active} activas"]
        if scheduled > 0:
            parts.append(f"{scheduled} programadas")
        self.count_label.configure(text=" | ".join(parts))

    def _start_ui_updater(self) -> None:
        """Periodic UI update for smooth progress display."""
        self._batch_update()
        self.after(250, self._start_ui_updater)

    def _start_clipboard_monitor(self) -> None:
        """Monitor clipboard for URLs."""
        def check():
            try:
                import pyperclip
                current = pyperclip.paste()
                if current != self._clipboard_last and is_valid_url(current.strip()):
                    self._clipboard_last = current
                    url = current.strip()
                    ext = os.path.splitext(url.split("?")[0])[1].lower()
                    if ext in self.config_manager.config.confirmed_extensions:
                        self.after(0, lambda: self._prompt_clipboard_download(url))
            except Exception:
                pass
            self.after(2000, check)
        self.after(2000, check)

    def _prompt_clipboard_download(self, url: str) -> None:
        if messagebox.askyesno(
            "URL detectada",
            f"Se detect\u00f3 una URL en el portapapeles:\n\n{url[:80]}...\n\n\u00bfDescargar?",
        ):
            threading.Thread(
                target=self._add_download_thread,
                args=(url, self.config_manager.config.download_dir, "", self.config_manager.config.default_connections),
                daemon=True,
            ).start()

    def _save_downloads(self) -> None:
        downloads = [item.to_dict() for item in self.engine.downloads.values()]
        self.config_manager.save_downloads(downloads)

    def _load_downloads(self) -> None:
        downloads = self.config_manager.load_downloads()
        for data in downloads:
            item = DownloadItem.from_dict(data)
            if item.status == DownloadStatus.DOWNLOADING:
                item.status = DownloadStatus.PAUSED
            self.engine.downloads[item.id] = item
            self._add_row(item)

        if not self.download_rows:
            self._empty_label.pack(pady=50)

    def _on_close(self) -> None:
        active_downloads = any(
            item.status == DownloadStatus.DOWNLOADING
            for item in self.engine.downloads.values()
        )

        if self.config_manager.config.minimize_to_tray and self._tray_icon:
            self.withdraw()
            return

        if active_downloads:
            if not messagebox.askyesno(
                "Descargas activas",
                "Hay descargas en progreso. \u00bfSeguro que deseas salir?",
            ):
                return

        self._save_downloads()

        self.config_manager.config.window_width = self.winfo_width()
        self.config_manager.config.window_height = self.winfo_height()
        self.config_manager.save_config()

        self.engine.shutdown()
        if self._tray_icon:
            self._tray_icon.stop()
        self.destroy()
