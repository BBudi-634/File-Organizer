import os, shutil # shell utilities = allows us to perform various file-related tasks (copying, moving, ect)

import time
from watchdog.observers import Observer # constant watch over any changes
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

from concurrent.futures import ThreadPoolExecutor

import logging

from config import load_config

config = load_config()
watch_path = str(config["watch"])
destination_path = str(config["destination"])
CATEGORIES = config["categories"]

logging.basicConfig( # log file creation
    filename=os.path.join(os.path.expanduser("~"), "organizer.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

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

def unique_destination(dest: str) -> str: # Handle file duplicates
    if not os.path.exists(dest):
        return dest

    stem, ext = os.path.splitext(dest)
    i = 1
    while os.path.exists(f"{stem}_{i}{ext}"):
        i += 1
    return f"{stem}_{i}{ext}"

def organize_file(filepath: str) -> None: # move single file to category folder.
    filename = os.path.basename(filepath)
    match = find_destination(filename)
    if not match:
        return

    category, subcategory = match
    dest_dir = os.path.join(destination_path, category, subcategory)
    dest = unique_destination(os.path.join(dest_dir, filename))

    try:
        os.makedirs(dest_dir, exist_ok=True)
        try:
            os.rename(filepath, dest)
        except OSError:
            shutil.move(filepath, dest)
        logging.info(f"Moved {filename} -> {category}/{subcategory}")
    except (OSError, shutil.Error) as e:
        logging.error(f"Failed to move {filename}: {e}")

def organize_all() -> None: # scans whole downloads folder.
    for category, subcategories in CATEGORIES.items():
        for subcategory in subcategories:
            os.makedirs(os.path.join(destination_path, category, subcategory), exist_ok=True)

    files = [
        os.path.join(watch_path, f)
        for f in os.listdir(watch_path)
        if os.path.isfile(os.path.join(watch_path, f))
    ]
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(organize_file, files)


class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        try:
            if isinstance(event, FileCreatedEvent) and not event.is_directory:
                filepath = str(event.src_path)
                if wait_until_stable(filepath):
                    organize_file(filepath)
        except Exception as e:
            logging.exception(f"Error in on_created for {event.src_path}: {e}")

    def on_moved(self, event):
        try:
            if isinstance(event, FileMovedEvent) and not event.is_directory:
                filepath = str(event.dest_path)
                if wait_until_stable(filepath):
                    organize_file(filepath)
        except Exception as e:
            logging.exception(f"Error in on_moved for {event.dest_path}: {e}")

def watch() -> None:
    organize_all()
    handler = DownloadHandler()
    observer = Observer()
    observer.schedule(handler, watch_path, recursive=False)
    observer.start()
    logging.info(f"Watching {watch_path} -> sorting into {destination_path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    watch()