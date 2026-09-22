import time
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

from .organizer import organize_file, organize_all, wait_until_stable

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, destination: str, categories: dict, batch_id: str):
        self.destination = destination
        self.categories = categories
        self.batch_id = batch_id

    def on_created(self, event):
        try:
            if isinstance(event, FileCreatedEvent) and not event.is_directory:
                filepath = str(event.src_path)
                if wait_until_stable(filepath):
                    organize_file(filepath, self.destination, self.categories, self.batch_id)
        except Exception as e:
            logging.exception(f"Error in on_created for {event.src_path}: {e}")

    def on_moved(self, event):
        try:
            if isinstance(event, FileMovedEvent) and not event.is_directory:
                filepath = str(event.dest_path)
                if wait_until_stable(filepath):
                    organize_file(filepath, self.destination, self.categories, self.batch_id)
        except Exception as e:
            logging.exception(f"Error in on_moved for {event.dest_path}: {e}")


def watch(watch_path: str, destination: str, categories: dict, batch_id: str) -> None:
    organize_all(watch_path, destination, categories, batch_id)
    handler = DownloadHandler(destination, categories, batch_id)
    observer = Observer()
    observer.schedule(handler, watch_path, recursive=False)
    observer.start()
    logging.info(f"Watching {watch_path} -> sorting into {destination}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()