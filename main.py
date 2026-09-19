import os, shutil # shell utilities = allows us to perform various file-related tasks (copying, moving, ect)

import time
from watchdog.observers import Observer # constant watch over any changes
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

from concurrent.futures import ThreadPoolExecutor

path = os.path.join(os.path.expanduser("~"), "Downloads")

CATEGORIES = {
    "Documents": {
        "Word":       ('.docx', '.doc', '.odt', '.rtf'),
        "PowerPoint": ('.pptx', '.ppt', '.odp'),
        "Excel":      ('.xlsx', '.xls', '.ods', '.csv'),
        "PDF":        ('.pdf',),
        "Text":       ('.txt', '.md'),
        "Data":       ('.json', '.xml', '.yaml', '.yml', '.toml'),
        "Other":      ('.html', '.htm'),
    },
    "Images": {
        "Photos":   ('.jpg', '.jpeg', '.png', '.heic', '.bmp', '.tiff'),
        "Graphics": ('.svg', '.gif', '.webp', '.tga', '.psd', '.ico'),
    },
    "Videos": {
        "Video": ('.mp4', '.mov', '.avi', '.mkv', '.webm'),
    },
    "Audio": {
        "Audio": ('.mp3', '.wav', '.flac', '.m4a', '.ogg'),
    },
    "Archives": {
        "Archive": ('.zip', '.tar.gz', '.tar.xz', '.rar', '.7z', '.tar'),
    },
    "Executables": {
        "Installer": ('.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'),
        "Script":    ('.bat', '.sh', '.ps1'),
    },
    "Others": {
        "Misc": ('.iso', '.msix', '.rosz'),
    },
}
def wait_until_stable(filepath: str, settle: int = 2, timeout: int = 300) -> bool:
    last_size = -1
    stable_since = time.time()
    start = time.time()

    while time.time() - start < timeout:
        if not os.path.exists(filepath):
            return False
        try:
            size = os.path.getsize(filepath)
        except OSError:
            return False

        if size != last_size:
            last_size = size
            stable_since = time.time()
        elif time.time() - stable_since >= settle:
            return True

        time.sleep(0.5)

    return False

def find_destination(filename: str) -> tuple[str, str] | None: # search nested structure and returns which category/subcat
    for category, subcategories in CATEGORIES.items():
        for subcategory, extensions in subcategories.items():
            if filename.endswith(extensions):
                return category, subcategory
    return None

def organize_file(filepath: str) -> None: # move single file to category folder.
    filename = os.path.basename(filepath)
    match = find_destination(filename)
    if not match:
        return

    category, subcategory = match
    dest_dir = os.path.join(path, category, subcategory)
    dest = os.path.join(dest_dir, filename)
    os.makedirs(dest_dir, exist_ok=True)

    if not os.path.exists(dest):
        try:
            os.rename(filepath, dest)
        except OSError:
            shutil.move(filepath, dest)
        print(f"Moved {filename} -> {category}/{subcategory}")

def organize_all() -> None: # scans whole downloads folder.
    for category, subcategories in CATEGORIES.items():
        for subcategory in subcategories:
            os.makedirs(os.path.join(path, category, subcategory), exist_ok=True)

    files = [
        os.path.join(path, f)
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
    ]
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(organize_file, files)


class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            filepath = str(event.src_path)
            if wait_until_stable(filepath):
                organize_file(filepath)

    def on_moved(self, event):
        if isinstance(event, FileMovedEvent) and not event.is_directory:
            filepath = str(event.dest_path)
            if wait_until_stable(filepath):
                organize_file(filepath)

def watch() -> None:
    organize_all()
    handler = DownloadHandler()
    observer = Observer()
    observer.schedule(handler, path, recursive=False)
    observer.start()
    print(f"Watching {path} (Ctrl+C to exit)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    watch()