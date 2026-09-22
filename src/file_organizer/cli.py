import os
import time
import logging
import argparse

from .config import load_config
from .history import new_batch_id, list_recent_batches
from .organizer import organize_all
from .undo import undo_last_batch
from .watcher import watch

def _setup_logging() -> None:
    logging.basicConfig(
        filename=os.path.join(os.path.expanduser("~"), "organizer.log"),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def show_history() -> None:
    batches = list_recent_batches(10)
    if not batches:
        print("No history yet.")
        return
    for batch_id, ts, count in batches:
        when = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
        print(f"{batch_id}  {when}  {count} file(s)")


def main() -> None:
    _setup_logging()

    parser = argparse.ArgumentParser(description="Organize files by category.")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("watch", help="Watch the folder and organize files as they arrive")
    sub.add_parser("organize", help="Sweep the folder once and exit")
    sub.add_parser("undo", help="Reverse the most recent batch of moves")
    sub.add_parser("history", help="Show recent batches")

    args = parser.parse_args()

    config = load_config()
    watch_path = str(config["watch"])
    destination = str(config["destination"])
    categories = config["categories"]
    batch_id = new_batch_id()

    if args.command == "watch" or args.command is None:
        watch(watch_path, destination, categories, batch_id)
    elif args.command == "organize":
        organize_all(watch_path, destination, categories, batch_id)
        print("Done.")
    elif args.command == "undo":
        undo_last_batch()
    elif args.command == "history":
        show_history()