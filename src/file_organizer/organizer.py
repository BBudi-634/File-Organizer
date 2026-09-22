import os
import shutil
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from .history import record_move

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

def find_destination(filename: str, categories: dict) -> tuple[str, str] | None: # search nested structure and returns which category/subcat
    filename = filename.lower()
    for category, subcategories in categories.items():
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

def organize_file(
    filepath: str,
    destination: str,
    categories: dict,
    batch_id: str,
) -> None: # move single file to category folder.
    filename = os.path.basename(filepath)
    match = find_destination(filename, categories)
    if not match:
        return

    category, subcategory = match
    dest_dir = os.path.join(destination, category, subcategory)
    dest = unique_destination(os.path.join(dest_dir, filename))

    try:
        os.makedirs(dest_dir, exist_ok=True)
        try:
            os.rename(filepath, dest)
        except OSError:
            shutil.move(filepath, dest)
        logging.info(f"Moved {filename} -> {category}/{subcategory}")
        record_move(batch_id, filepath, dest)
    except (OSError, shutil.Error) as e:
        logging.error(f"Failed to move {filename}: {e}")

def organize_all(
    watch_path: str,
    destination: str,
    categories: dict,
    batch_id: str,
) -> None: # scans whole downloads folder.
    for category, subcategories in categories.items():
        for subcategory in subcategories:
            os.makedirs(os.path.join(destination, category, subcategory), exist_ok=True)

    files = [
        os.path.join(watch_path, f)
        for f in os.listdir(watch_path)
        if os.path.isfile(os.path.join(watch_path, f))
    ]

    def move_one(filepath: str) -> None:
        organize_file(filepath, destination, categories, batch_id)

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(move_one, files)