import os, shutil # shell utilities = allows us to perform various file-related tasks (copying, moving, ect)

import time
from watchdog.observers import Observer # constant watch over any changes
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent, DirCreatedEvent

from concurrent.futures import ThreadPoolExecutor

path = os.path.join(os.path.expanduser("~"), "Downloads")

CATEGORIES = {
    "Images": ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.tga', '.bmp', '.tiff', '.tif', '.svg', '.heic', '.ico'),
    "Documents": ('.pdf', '.docx', '.txt', '.xlsx'),
    "Videos": ('.mp4', '.mov'),
    "Audio": ('.mp3', '.wav'),
    "Archives": ('.zip', '.tar.gz', '.tar.xz', '.rar', '.7z'),
    "Executables": ('.exe', '.bat'),
    "Others": ('.psd', '.iso', '.msix')
}

def wait_until_stable(filepath: str, settle: int = 1, timeout: int = 300) -> bool:
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

        time.sleep(1)

    return False

def organize_file(filepath: str) -> None: # move single file to category folder.
    filename = os.path.basename(filepath)
    for category, extensions in CATEGORIES.items():
        if filename.endswith(extensions):
            dest_dir = os.path.join(path, category)
            dest = os.path.join(dest_dir, filename)
            os.makedirs(dest_dir, exist_ok=True)
            if not os.path.exists(dest):
                try:
                    os.rename(filepath,dest)
                except OSError:
                    shutil.move(filepath, dest)
                print(f"Moved {filename} -> {category}")
            break

def organize_all() -> None: # scans whole downloads folder.
    for category in CATEGORIES:
        os.makedirs(os.path.join(path, category), exist_ok=True)

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