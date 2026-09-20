# undo.py — reverse the most recent batch of moves recorded in history.db
import os
import logging

from history import get_last_batch, delete_batch

def undo_last_batch() -> int:
    result = get_last_batch()
    if not result:
        print("Nothing to undo.")
        return 0

    batch_id, moves = result
    restored = 0
    for src, dest in moves:
        if not os.path.exists(dest):
            logging.warning(f"Cannot undo: {dest} no longer exists")
            continue
        if os.path.exists(src):
            logging.warning(f"Cannot undo: {src} already exists")
            continue
        try:
            os.makedirs(os.path.dirname(src), exist_ok=True)
            os.rename(dest, src)
            restored += 1
            logging.info(f"Undid: {os.path.basename(dest)} -> {src}")
        except OSError as e:
            logging.error(f"Failed to undo {dest}: {e}")

    if restored == len(moves):
        delete_batch(batch_id)
        logging.info(f"Deleted batch {batch_id} from history")

    print(f"Restored {restored} file(s).")
    return restored