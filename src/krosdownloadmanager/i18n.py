"""Internationalization (i18n) module for KrosDownloadManager."""

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ---- General / Shared ----
    "app_title": {
        "es": "KrosDownloadManager",
        "en": "KrosDownloadManager",
        "pt": "KrosDownloadManager",
        "fr": "KrosDownloadManager",
        "de": "KrosDownloadManager",
    },
    "ready": {
        "es": "Listo",
        "en": "Ready",
        "pt": "Pronto",
        "fr": "Prêt",
        "de": "Bereit",
    },
    "cancel": {
        "es": "Cancelar",
        "en": "Cancel",
        "pt": "Cancelar",
        "fr": "Annuler",
        "de": "Abbrechen",
    },
    "close": {
        "es": "Cerrar",
        "en": "Close",
        "pt": "Fechar",
        "fr": "Fermer",
        "de": "Schließen",
    },
    "save": {
        "es": "Guardar",
        "en": "Save",
        "pt": "Salvar",
        "fr": "Enregistrer",
        "de": "Speichern",
    },
    "confirm": {
        "es": "Confirmar",
        "en": "Confirm",
        "pt": "Confirmar",
        "fr": "Confirmer",
        "de": "Bestätigen",
    },
    "error": {
        "es": "Error",
        "en": "Error",
        "pt": "Erro",
        "fr": "Erreur",
        "de": "Fehler",
    },
    "unknown": {
        "es": "Desconocido",
        "en": "Unknown",
        "pt": "Desconhecido",
        "fr": "Inconnu",
        "de": "Unbekannt",
    },

    # ---- Download statuses ----
    "status_queued": {
        "es": "En cola",
        "en": "Queued",
        "pt": "Na fila",
        "fr": "En file",
        "de": "Warteschlange",
    },
    "status_downloading": {
        "es": "Descargando",
        "en": "Downloading",
        "pt": "Baixando",
        "fr": "Téléchargement",
        "de": "Herunterladen",
    },
    "status_paused": {
        "es": "Pausado",
        "en": "Paused",
        "pt": "Pausado",
        "fr": "En pause",
        "de": "Pausiert",
    },
    "status_completed": {
        "es": "Completado",
        "en": "Completed",
        "pt": "Concluído",
        "fr": "Terminé",
        "de": "Abgeschlossen",
    },
    "status_error": {
        "es": "Error",
        "en": "Error",
        "pt": "Erro",
        "fr": "Erreur",
        "de": "Fehler",
    },
    "status_merging": {
        "es": "Uniendo...",
        "en": "Merging...",
        "pt": "Mesclando...",
        "fr": "Fusion...",
        "de": "Zusammenführen...",
    },
    "status_cancelled": {
        "es": "Cancelado",
        "en": "Cancelled",
        "pt": "Cancelado",
        "fr": "Annulé",
        "de": "Abgebrochen",
    },

    # ---- Toolbar buttons ----
    "btn_new": {
        "es": "\u2795 Nueva",
        "en": "\u2795 New",
        "pt": "\u2795 Nova",
        "fr": "\u2795 Nouveau",
        "de": "\u2795 Neu",
    },
    "btn_batch": {
        "es": "\U0001F4E5 Lotes",
        "en": "\U0001F4E5 Batch",
        "pt": "\U0001F4E5 Lote",
        "fr": "\U0001F4E5 Lot",
        "de": "\U0001F4E5 Stapel",
    },
    "btn_schedule": {
        "es": "\u23F0 Programar",
        "en": "\u23F0 Schedule",
        "pt": "\u23F0 Agendar",
        "fr": "\u23F0 Planifier",
        "de": "\u23F0 Planen",
    },

    # ---- Sidebar categories ----
    "cat_all": {
        "es": "Todas",
        "en": "All",
        "pt": "Todas",
        "fr": "Toutes",
        "de": "Alle",
    },
    "cat_downloading": {
        "es": "Descargando",
        "en": "Downloading",
        "pt": "Baixando",
        "fr": "En cours",
        "de": "Aktiv",
    },
    "cat_completed": {
        "es": "Completadas",
        "en": "Completed",
        "pt": "Concluídas",
        "fr": "Terminées",
        "de": "Abgeschlossen",
    },
    "cat_paused": {
        "es": "Pausadas",
        "en": "Paused",
        "pt": "Pausadas",
        "fr": "En pause",
        "de": "Pausiert",
    },
    "cat_errors": {
        "es": "Errores",
        "en": "Errors",
        "pt": "Erros",
        "fr": "Erreurs",
        "de": "Fehler",
    },
    "cat_scheduled": {
        "es": "Programadas",
        "en": "Scheduled",
        "pt": "Agendadas",
        "fr": "Planifiées",
        "de": "Geplant",
    },
    "cat_compressed": {
        "es": "Comprimidos",
        "en": "Compressed",
        "pt": "Compactados",
        "fr": "Compressés",
        "de": "Komprimiert",
    },
    "cat_documents": {
        "es": "Documentos",
        "en": "Documents",
        "pt": "Documentos",
        "fr": "Documents",
        "de": "Dokumente",
    },
    "cat_video": {
        "es": "Video",
        "en": "Video",
        "pt": "Vídeo",
        "fr": "Vidéo",
        "de": "Video",
    },
    "cat_music": {
        "es": "Música",
        "en": "Music",
        "pt": "Música",
        "fr": "Musique",
        "de": "Musik",
    },
    "cat_programs": {
        "es": "Programas",
        "en": "Programs",
        "pt": "Programas",
        "fr": "Programmes",
        "de": "Programme",
    },
    "cat_images": {
        "es": "Imágenes",
        "en": "Images",
        "pt": "Imagens",
        "fr": "Images",
        "de": "Bilder",
    },
    "categories": {
        "es": "Categorías",
        "en": "Categories",
        "pt": "Categorias",
        "fr": "Catégories",
        "de": "Kategorien",
    },

    # ---- Shortcuts panel ----
    "shortcuts": {
        "es": "Atajos",
        "en": "Shortcuts",
        "pt": "Atalhos",
        "fr": "Raccourcis",
        "de": "Tastenkürzel",
    },
    "shortcut_new": {
        "es": "Ctrl+N  Nueva",
        "en": "Ctrl+N  New",
        "pt": "Ctrl+N  Nova",
        "fr": "Ctrl+N  Nouveau",
        "de": "Ctrl+N  Neu",
    },
    "shortcut_batch": {
        "es": "Ctrl+B  Lotes",
        "en": "Ctrl+B  Batch",
        "pt": "Ctrl+B  Lote",
        "fr": "Ctrl+B  Lot",
        "de": "Ctrl+B  Stapel",
    },
    "shortcut_schedule": {
        "es": "Ctrl+T  Programar",
        "en": "Ctrl+T  Schedule",
        "pt": "Ctrl+T  Agendar",
        "fr": "Ctrl+T  Planifier",
        "de": "Ctrl+T  Planen",
    },
    "shortcut_pause": {
        "es": "Ctrl+P  Pausar",
        "en": "Ctrl+P  Pause",
        "pt": "Ctrl+P  Pausar",
        "fr": "Ctrl+P  Pause",
        "de": "Ctrl+P  Pause",
    },
    "shortcut_resume": {
        "es": "Ctrl+R  Reanudar",
        "en": "Ctrl+R  Resume",
        "pt": "Ctrl+R  Retomar",
        "fr": "Ctrl+R  Reprendre",
        "de": "Ctrl+R  Fortsetzen",
    },
    "shortcut_delete": {
        "es": "Del     Eliminar",
        "en": "Del     Delete",
        "pt": "Del     Excluir",
        "fr": "Del     Supprimer",
        "de": "Del     Löschen",
    },
    "shortcut_quit": {
        "es": "Ctrl+Q  Salir",
        "en": "Ctrl+Q  Quit",
        "pt": "Ctrl+Q  Sair",
        "fr": "Ctrl+Q  Quitter",
        "de": "Ctrl+Q  Beenden",
    },
    "shortcut_info": {
        "es": "F1      Info",
        "en": "F1      Info",
        "pt": "F1      Info",
        "fr": "F1      Info",
        "de": "F1      Info",
    },

    # ---- Column headers ----
    "col_name": {
        "es": "Nombre",
        "en": "Name",
        "pt": "Nome",
        "fr": "Nom",
        "de": "Name",
    },
    "col_size": {
        "es": "Tamaño",
        "en": "Size",
        "pt": "Tamanho",
        "fr": "Taille",
        "de": "Größe",
    },
    "col_progress": {
        "es": "Progreso",
        "en": "Progress",
        "pt": "Progresso",
        "fr": "Progression",
        "de": "Fortschritt",
    },
    "col_status": {
        "es": "Estado",
        "en": "Status",
        "pt": "Estado",
        "fr": "État",
        "de": "Status",
    },

    # ---- Empty state ----
    "no_downloads": {
        "es": "\u2B07\n\nNo hay descargas\n\nCtrl+N para agregar",
        "en": "\u2B07\n\nNo downloads\n\nCtrl+N to add",
        "pt": "\u2B07\n\nSem downloads\n\nCtrl+N para adicionar",
        "fr": "\u2B07\n\nAucun téléchargement\n\nCtrl+N pour ajouter",
        "de": "\u2B07\n\nKeine Downloads\n\nCtrl+N zum Hinzufügen",
    },

    # ---- Status bar ----
    "downloads_count": {
        "es": "descargas",
        "en": "downloads",
        "pt": "downloads",
        "fr": "téléchargements",
        "de": "Downloads",
    },
    "active_count": {
        "es": "activas",
        "en": "active",
        "pt": "ativas",
        "fr": "actifs",
        "de": "aktiv",
    },
    "scheduled_count": {
        "es": "programadas",
        "en": "scheduled",
        "pt": "agendadas",
        "fr": "planifiés",
        "de": "geplant",
    },
    "total_speed": {
        "es": "Velocidad total",
        "en": "Total speed",
        "pt": "Velocidade total",
        "fr": "Vitesse totale",
        "de": "Gesamtgeschwindigkeit",
    },

    # ---- Add Download Dialog ----
    "new_download": {
        "es": "Nueva Descarga",
        "en": "New Download",
        "pt": "Novo Download",
        "fr": "Nouveau Téléchargement",
        "de": "Neuer Download",
    },
    "url_label": {
        "es": "URL",
        "en": "URL",
        "pt": "URL",
        "fr": "URL",
        "de": "URL",
    },
    "url_placeholder": {
        "es": "https://ejemplo.com/archivo.zip",
        "en": "https://example.com/file.zip",
        "pt": "https://exemplo.com/arquivo.zip",
        "fr": "https://exemple.com/fichier.zip",
        "de": "https://beispiel.de/datei.zip",
    },
    "filename_optional": {
        "es": "Nombre del archivo (opcional)",
        "en": "Filename (optional)",
        "pt": "Nome do arquivo (opcional)",
        "fr": "Nom du fichier (optionnel)",
        "de": "Dateiname (optional)",
    },
    "auto_detected": {
        "es": "Se detecta automáticamente",
        "en": "Auto-detected",
        "pt": "Detectado automaticamente",
        "fr": "Détecté automatiquement",
        "de": "Automatisch erkannt",
    },
    "save_to": {
        "es": "Guardar en",
        "en": "Save to",
        "pt": "Salvar em",
        "fr": "Enregistrer dans",
        "de": "Speichern unter",
    },
    "connections": {
        "es": "Conexiones",
        "en": "Connections",
        "pt": "Conexões",
        "fr": "Connexions",
        "de": "Verbindungen",
    },
    "download_btn": {
        "es": "Descargar",
        "en": "Download",
        "pt": "Baixar",
        "fr": "Télécharger",
        "de": "Herunterladen",
    },

    # ---- Batch Download Dialog ----
    "batch_download": {
        "es": "Descarga por Lotes",
        "en": "Batch Download",
        "pt": "Download em Lote",
        "fr": "Téléchargement par lot",
        "de": "Stapeldownload",
    },
    "one_url_per_line": {
        "es": "Ingresa una URL por línea",
        "en": "Enter one URL per line",
        "pt": "Insira uma URL por linha",
        "fr": "Entrez une URL par ligne",
        "de": "Eine URL pro Zeile eingeben",
    },

    # ---- Schedule Download Dialog ----
    "schedule_download": {
        "es": "Programar Descarga",
        "en": "Schedule Download",
        "pt": "Agendar Download",
        "fr": "Planifier Téléchargement",
        "de": "Download planen",
    },
    "date_time": {
        "es": "Fecha y hora (YYYY-MM-DD HH:MM)",
        "en": "Date and time (YYYY-MM-DD HH:MM)",
        "pt": "Data e hora (YYYY-MM-DD HH:MM)",
        "fr": "Date et heure (AAAA-MM-JJ HH:MM)",
        "de": "Datum und Uhrzeit (JJJJ-MM-TT HH:MM)",
    },
    "schedule_btn": {
        "es": "Programar",
        "en": "Schedule",
        "pt": "Agendar",
        "fr": "Planifier",
        "de": "Planen",
    },

    # ---- Checksum Dialog ----
    "integrity_check": {
        "es": "Verificación de integridad",
        "en": "Integrity Check",
        "pt": "Verificação de integridade",
        "fr": "Vérification d'intégrité",
        "de": "Integritätsprüfung",
    },

    # ---- Settings Dialog ----
    "settings": {
        "es": "Configuración",
        "en": "Settings",
        "pt": "Configurações",
        "fr": "Paramètres",
        "de": "Einstellungen",
    },
    "section_downloads": {
        "es": "Descargas",
        "en": "Downloads",
        "pt": "Downloads",
        "fr": "Téléchargements",
        "de": "Downloads",
    },
    "default_folder": {
        "es": "Carpeta por defecto:",
        "en": "Default folder:",
        "pt": "Pasta padrão:",
        "fr": "Dossier par défaut :",
        "de": "Standardordner:",
    },
    "default_connections": {
        "es": "Conexiones por defecto:",
        "en": "Default connections:",
        "pt": "Conexões padrão:",
        "fr": "Connexions par défaut :",
        "de": "Standardverbindungen:",
    },
    "concurrent_downloads": {
        "es": "Descargas simultáneas:",
        "en": "Concurrent downloads:",
        "pt": "Downloads simultâneos:",
        "fr": "Téléchargements simultanés :",
        "de": "Gleichzeitige Downloads:",
    },
    "section_speed_limit": {
        "es": "Límite de velocidad",
        "en": "Speed Limit",
        "pt": "Limite de velocidade",
        "fr": "Limite de vitesse",
        "de": "Geschwindigkeitslimit",
    },
    "speed_limit_label": {
        "es": "Límite (KB/s, 0 = sin límite):",
        "en": "Limit (KB/s, 0 = no limit):",
        "pt": "Limite (KB/s, 0 = sem limite):",
        "fr": "Limite (Ko/s, 0 = sans limite) :",
        "de": "Limit (KB/s, 0 = kein Limit):",
    },
    "section_proxy": {
        "es": "Proxy",
        "en": "Proxy",
        "pt": "Proxy",
        "fr": "Proxy",
        "de": "Proxy",
    },
    "use_proxy": {
        "es": "Usar proxy",
        "en": "Use proxy",
        "pt": "Usar proxy",
        "fr": "Utiliser un proxy",
        "de": "Proxy verwenden",
    },
    "proxy_label": {
        "es": "Proxy (ej: http://proxy:8080):",
        "en": "Proxy (e.g. http://proxy:8080):",
        "pt": "Proxy (ex: http://proxy:8080):",
        "fr": "Proxy (ex : http://proxy:8080) :",
        "de": "Proxy (z.B. http://proxy:8080):",
    },
    "section_interface": {
        "es": "Interfaz",
        "en": "Interface",
        "pt": "Interface",
        "fr": "Interface",
        "de": "Oberfläche",
    },
    "theme_label": {
        "es": "Tema:",
        "en": "Theme:",
        "pt": "Tema:",
        "fr": "Thème :",
        "de": "Thema:",
    },
    "theme_dark": {
        "es": "Oscuro",
        "en": "Dark",
        "pt": "Escuro",
        "fr": "Sombre",
        "de": "Dunkel",
    },
    "theme_light": {
        "es": "Claro",
        "en": "Light",
        "pt": "Claro",
        "fr": "Clair",
        "de": "Hell",
    },
    "clipboard_monitoring": {
        "es": "Monitorear portapapeles",
        "en": "Monitor clipboard",
        "pt": "Monitorar área de transferência",
        "fr": "Surveiller le presse-papiers",
        "de": "Zwischenablage überwachen",
    },
    "minimize_to_tray": {
        "es": "Minimizar a bandeja del sistema",
        "en": "Minimize to system tray",
        "pt": "Minimizar para a bandeja do sistema",
        "fr": "Réduire dans la barre des tâches",
        "de": "In den Infobereich minimieren",
    },
    "section_language": {
        "es": "Idioma",
        "en": "Language",
        "pt": "Idioma",
        "fr": "Langue",
        "de": "Sprache",
    },
    "language_label": {
        "es": "Idioma de la interfaz:",
        "en": "Interface language:",
        "pt": "Idioma da interface:",
        "fr": "Langue de l'interface :",
        "de": "Sprache der Oberfläche:",
    },
    "restart_required": {
        "es": "Reinicia la app para aplicar el cambio de idioma.",
        "en": "Restart the app to apply the language change.",
        "pt": "Reinicie o app para aplicar a mudança de idioma.",
        "fr": "Redémarrez l'application pour appliquer le changement de langue.",
        "de": "Starten Sie die App neu, um die Sprachänderung anzuwenden.",
    },

    # ---- About Dialog ----
    "about": {
        "es": "Acerca de",
        "en": "About",
        "pt": "Sobre",
        "fr": "À propos",
        "de": "Über",
    },
    "about_description": {
        "es": "Gestor de descargas portable para Windows",
        "en": "Portable download manager for Windows",
        "pt": "Gerenciador de downloads portátil para Windows",
        "fr": "Gestionnaire de téléchargements portable pour Windows",
        "de": "Portabler Download-Manager für Windows",
    },
    "about_features": {
        "es": "Multi-hilo · Pausar/Reanudar · Programar\nProxy · Checksums · Lotes · Portapapeles\nMediaFire · Google Drive · Dropbox · YouTube",
        "en": "Multi-threaded · Pause/Resume · Schedule\nProxy · Checksums · Batch · Clipboard\nMediaFire · Google Drive · Dropbox · YouTube",
        "pt": "Multi-thread · Pausar/Retomar · Agendar\nProxy · Checksums · Lote · Área de transferência\nMediaFire · Google Drive · Dropbox · YouTube",
        "fr": "Multi-thread · Pause/Reprise · Planifier\nProxy · Checksums · Lot · Presse-papiers\nMediaFire · Google Drive · Dropbox · YouTube",
        "de": "Multi-Thread · Pause/Fortsetzen · Planen\nProxy · Checksums · Stapel · Zwischenablage\nMediaFire · Google Drive · Dropbox · YouTube",
    },
    "made_by": {
        "es": "Hecho por iSekro",
        "en": "Made by iSekro",
        "pt": "Feito por iSekro",
        "fr": "Fait par iSekro",
        "de": "Erstellt von iSekro",
    },

    # ---- Context Menu ----
    "ctx_pause": {
        "es": "\u23F8 Pausar",
        "en": "\u23F8 Pause",
        "pt": "\u23F8 Pausar",
        "fr": "\u23F8 Pause",
        "de": "\u23F8 Pause",
    },
    "ctx_resume": {
        "es": "\u25B6 Reanudar",
        "en": "\u25B6 Resume",
        "pt": "\u25B6 Retomar",
        "fr": "\u25B6 Reprendre",
        "de": "\u25B6 Fortsetzen",
    },
    "ctx_cancel": {
        "es": "\u23F9 Cancelar",
        "en": "\u23F9 Cancel",
        "pt": "\u23F9 Cancelar",
        "fr": "\u23F9 Annuler",
        "de": "\u23F9 Abbrechen",
    },
    "ctx_open_folder": {
        "es": "\U0001F4C2 Abrir carpeta",
        "en": "\U0001F4C2 Open folder",
        "pt": "\U0001F4C2 Abrir pasta",
        "fr": "\U0001F4C2 Ouvrir le dossier",
        "de": "\U0001F4C2 Ordner öffnen",
    },
    "ctx_checksums": {
        "es": "\U0001F512 Ver checksums",
        "en": "\U0001F512 View checksums",
        "pt": "\U0001F512 Ver checksums",
        "fr": "\U0001F512 Voir les checksums",
        "de": "\U0001F512 Prüfsummen anzeigen",
    },
    "ctx_copy_url": {
        "es": "\U0001F4CB Copiar URL",
        "en": "\U0001F4CB Copy URL",
        "pt": "\U0001F4CB Copiar URL",
        "fr": "\U0001F4CB Copier l'URL",
        "de": "\U0001F4CB URL kopieren",
    },
    "ctx_remove_from_list": {
        "es": "\U0001F5D1 Eliminar de la lista",
        "en": "\U0001F5D1 Remove from list",
        "pt": "\U0001F5D1 Remover da lista",
        "fr": "\U0001F5D1 Retirer de la liste",
        "de": "\U0001F5D1 Aus Liste entfernen",
    },
    "ctx_delete_with_file": {
        "es": "\U0001F5D1 Eliminar con archivo",
        "en": "\U0001F5D1 Delete with file",
        "pt": "\U0001F5D1 Excluir com arquivo",
        "fr": "\U0001F5D1 Supprimer avec le fichier",
        "de": "\U0001F5D1 Mit Datei löschen",
    },

    # ---- Confirmation messages ----
    "confirm_delete_file": {
        "es": "¿Eliminar '{filename}' y su archivo?",
        "en": "Delete '{filename}' and its file?",
        "pt": "Excluir '{filename}' e seu arquivo?",
        "fr": "Supprimer '{filename}' et son fichier ?",
        "de": "'{filename}' und die Datei löschen?",
    },
    "confirm_delete_active": {
        "es": "La descarga está en progreso. ¿Eliminar?",
        "en": "Download is in progress. Delete?",
        "pt": "O download está em andamento. Excluir?",
        "fr": "Téléchargement en cours. Supprimer ?",
        "de": "Download läuft. Löschen?",
    },
    "confirm_quit_active": {
        "es": "Hay descargas en progreso. ¿Seguro que deseas salir?",
        "en": "There are active downloads. Are you sure you want to quit?",
        "pt": "Há downloads em andamento. Tem certeza que deseja sair?",
        "fr": "Des téléchargements sont en cours. Voulez-vous vraiment quitter ?",
        "de": "Es laufen Downloads. Wirklich beenden?",
    },
    "active_downloads_title": {
        "es": "Descargas activas",
        "en": "Active Downloads",
        "pt": "Downloads ativos",
        "fr": "Téléchargements actifs",
        "de": "Aktive Downloads",
    },

    # ---- Validation messages ----
    "url_empty_title": {
        "es": "URL vacía",
        "en": "Empty URL",
        "pt": "URL vazia",
        "fr": "URL vide",
        "de": "Leere URL",
    },
    "url_empty_msg": {
        "es": "Por favor, ingresa una URL.",
        "en": "Please enter a URL.",
        "pt": "Por favor, insira uma URL.",
        "fr": "Veuillez entrer une URL.",
        "de": "Bitte geben Sie eine URL ein.",
    },
    "url_invalid_title": {
        "es": "URL inválida",
        "en": "Invalid URL",
        "pt": "URL inválida",
        "fr": "URL invalide",
        "de": "Ungültige URL",
    },
    "url_invalid_msg": {
        "es": "La URL proporcionada no es válida.",
        "en": "The provided URL is not valid.",
        "pt": "A URL fornecida não é válida.",
        "fr": "L'URL fournie n'est pas valide.",
        "de": "Die angegebene URL ist ungültig.",
    },
    "folder_empty_title": {
        "es": "Carpeta vacía",
        "en": "Empty Folder",
        "pt": "Pasta vazia",
        "fr": "Dossier vide",
        "de": "Leerer Ordner",
    },
    "folder_empty_msg": {
        "es": "Selecciona una carpeta de destino.",
        "en": "Select a destination folder.",
        "pt": "Selecione uma pasta de destino.",
        "fr": "Sélectionnez un dossier de destination.",
        "de": "Wählen Sie einen Zielordner.",
    },
    "time_empty_title": {
        "es": "Hora vacía",
        "en": "Empty Time",
        "pt": "Hora vazia",
        "fr": "Heure vide",
        "de": "Leere Uhrzeit",
    },
    "time_empty_msg": {
        "es": "Ingresa la fecha y hora.",
        "en": "Enter the date and time.",
        "pt": "Insira a data e hora.",
        "fr": "Entrez la date et l'heure.",
        "de": "Geben Sie Datum und Uhrzeit ein.",
    },

    # ---- Status messages ----
    "resolving_link": {
        "es": "Resolviendo enlace de descarga...",
        "en": "Resolving download link...",
        "pt": "Resolvendo link de download...",
        "fr": "Résolution du lien de téléchargement...",
        "de": "Download-Link wird aufgelöst...",
    },
    "getting_info": {
        "es": "Obteniendo info de {url}...",
        "en": "Getting info from {url}...",
        "pt": "Obtendo informações de {url}...",
        "fr": "Obtention des informations de {url}...",
        "de": "Informationen werden abgerufen von {url}...",
    },
    "download_from_extension": {
        "es": "Descarga desde extensión: {url}",
        "en": "Download from extension: {url}",
        "pt": "Download da extensão: {url}",
        "fr": "Téléchargement depuis l'extension : {url}",
        "de": "Download von Erweiterung: {url}",
    },
    "downloading_status": {
        "es": "Descargando: {filename}",
        "en": "Downloading: {filename}",
        "pt": "Baixando: {filename}",
        "fr": "Téléchargement : {filename}",
        "de": "Herunterladen: {filename}",
    },
    "completed_status": {
        "es": "Completado: {filename}",
        "en": "Completed: {filename}",
        "pt": "Concluído: {filename}",
        "fr": "Terminé : {filename}",
        "de": "Abgeschlossen: {filename}",
    },
    "error_status": {
        "es": "Error: {filename} - {error}",
        "en": "Error: {filename} - {error}",
        "pt": "Erro: {filename} - {error}",
        "fr": "Erreur : {filename} - {error}",
        "de": "Fehler: {filename} - {error}",
    },
    "scheduling_download": {
        "es": "Programando descarga de {url}...",
        "en": "Scheduling download of {url}...",
        "pt": "Agendando download de {url}...",
        "fr": "Planification du téléchargement de {url}...",
        "de": "Download wird geplant von {url}...",
    },
    "scheduled_status": {
        "es": "Programada: {filename} para {time}",
        "en": "Scheduled: {filename} for {time}",
        "pt": "Agendado: {filename} para {time}",
        "fr": "Planifié : {filename} pour {time}",
        "de": "Geplant: {filename} für {time}",
    },
    "schedule_error": {
        "es": "No se pudo programar la descarga:\n{error}",
        "en": "Could not schedule the download:\n{error}",
        "pt": "Não foi possível agendar o download:\n{error}",
        "fr": "Impossible de planifier le téléchargement :\n{error}",
        "de": "Download konnte nicht geplant werden:\n{error}",
    },
    "download_error": {
        "es": "No se pudo iniciar la descarga:\n{error}",
        "en": "Could not start the download:\n{error}",
        "pt": "Não foi possível iniciar o download:\n{error}",
        "fr": "Impossible de démarrer le téléchargement :\n{error}",
        "de": "Download konnte nicht gestartet werden:\n{error}",
    },

    # ---- Tray menu ----
    "tray_show": {
        "es": "Mostrar",
        "en": "Show",
        "pt": "Mostrar",
        "fr": "Afficher",
        "de": "Anzeigen",
    },
    "tray_new_download": {
        "es": "Nueva descarga",
        "en": "New download",
        "pt": "Novo download",
        "fr": "Nouveau téléchargement",
        "de": "Neuer Download",
    },
    "tray_quit": {
        "es": "Salir",
        "en": "Quit",
        "pt": "Sair",
        "fr": "Quitter",
        "de": "Beenden",
    },

    # ---- Clipboard ----
    "url_detected": {
        "es": "URL detectada",
        "en": "URL Detected",
        "pt": "URL detectada",
        "fr": "URL détectée",
        "de": "URL erkannt",
    },
    "clipboard_prompt": {
        "es": "Se detectó una URL en el portapapeles:\n\n{url}...\n\n¿Descargar?",
        "en": "A URL was detected in the clipboard:\n\n{url}...\n\nDownload?",
        "pt": "Uma URL foi detectada na área de transferência:\n\n{url}...\n\nBaixar?",
        "fr": "Une URL a été détectée dans le presse-papiers :\n\n{url}...\n\nTélécharger ?",
        "de": "Eine URL wurde in der Zwischenablage erkannt:\n\n{url}...\n\nHerunterladen?",
    },

    # ---- File browser dialogs ----
    "select_download_folder": {
        "es": "Seleccionar carpeta de descarga",
        "en": "Select download folder",
        "pt": "Selecionar pasta de download",
        "fr": "Sélectionner le dossier de téléchargement",
        "de": "Download-Ordner auswählen",
    },
    "select_folder": {
        "es": "Seleccionar carpeta",
        "en": "Select folder",
        "pt": "Selecionar pasta",
        "fr": "Sélectionner un dossier",
        "de": "Ordner auswählen",
    },

    # ---- Search ----
    "search_placeholder": {
        "es": "Buscar descargas...",
        "en": "Search downloads...",
        "pt": "Buscar downloads...",
        "fr": "Rechercher des téléchargements...",
        "de": "Downloads suchen...",
    },

    # ---- Empty state ----
    "empty_hint": {
        "es": "Ctrl+N para agregar  \u2022  Arrastra una URL aquí",
        "en": "Ctrl+N to add  \u2022  Drop a URL here",
        "pt": "Ctrl+N para adicionar  \u2022  Arraste uma URL aqui",
        "fr": "Ctrl+N pour ajouter  \u2022  Glissez une URL ici",
        "de": "Ctrl+N zum Hinzufügen  \u2022  URL hierher ziehen",
    },

    # ---- Toast notifications ----
    "toast_complete": {
        "es": "{filename} \u2014 descarga completada",
        "en": "{filename} \u2014 download complete",
        "pt": "{filename} \u2014 download concluído",
        "fr": "{filename} \u2014 téléchargement terminé",
        "de": "{filename} \u2014 Download abgeschlossen",
    },
    "toast_error": {
        "es": "{filename} \u2014 error en la descarga",
        "en": "{filename} \u2014 download failed",
        "pt": "{filename} \u2014 erro no download",
        "fr": "{filename} \u2014 échec du téléchargement",
        "de": "{filename} \u2014 Download fehlgeschlagen",
    },
    "toast_dropped": {
        "es": "{count} URL(s) agregada(s)",
        "en": "{count} URL(s) added",
        "pt": "{count} URL(s) adicionada(s)",
        "fr": "{count} URL(s) ajoutée(s)",
        "de": "{count} URL(s) hinzugefügt",
    },

    # ---- Context menu: open file ----
    "ctx_open_file": {
        "es": "Abrir archivo",
        "en": "Open file",
        "pt": "Abrir arquivo",
        "fr": "Ouvrir le fichier",
        "de": "Datei öffnen",
    },
}

AVAILABLE_LANGUAGES = {
    "es": "Español",
    "en": "English",
    "pt": "Português",
    "fr": "Français",
    "de": "Deutsch",
}

_current_language = "es"


def set_language(lang: str) -> None:
    """Set the active language."""
    global _current_language
    if lang in AVAILABLE_LANGUAGES:
        _current_language = lang


def get_language() -> str:
    """Return the current language code."""
    return _current_language


def t(key: str, **kwargs: str) -> str:
    """Translate a key to the current language.

    Supports format placeholders via keyword arguments.
    Falls back to Spanish, then to the key itself.
    """
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    text = entry.get(_current_language) or entry.get("es", key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
