import os, shutil # shell utilities = allows us to perform various file-related tasks (copying, moving, ect)

import time
from watchdog.observers import Observer # constant watch over any changes
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent, DirCreatedEvent

path = os.path.join(os.path.expanduser("~"), "Desktop", "watch-test")

CATEGORIES = {
    "Images": ('.jpg', '.jpeg', '.png', '.gif', '.webp'),
    "Documents": ('.pdf', '.docx', '.txt', '.xlsx'),
    "Videos": ('.mp4', '.mov'),
    "Audio": ('.mp3', '.wav'),
    "Archives": ('.zip', '.tar.gz', '.tar.xz', '.rar', '.7z'),
    "Executables": ('.exe', '.bat'),
    "Others": ('.psd', '.iso', '.msix')
}
def organize_file(filepath: str) -> None: # move single file to category folder.
    for filename in os.listdir(path):
        for category, extensions in CATEGORIES.items():
            if filename.endswith(extensions):
                dest = os.path.join(path, category, filename)
                os.makedirs(os.path.join(path, category), exist_ok=True)
                if not os.path.exists(dest):
                    shutil.move(os.path.join(path, filename), dest)
                break

def organize_all() -> None: # scans whole downloads folder.
    for filename in os.listdir(path):
        full = os.path.join(path, filename)
        if os.path.isfile(full):
            organize_file(full)

class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            organize_file(event.src_path)

    def on_moved(self, event):
        if isinstance(event, FileMovedEvent) and not event.is_directory:
            organize_file(event.dest_path)

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