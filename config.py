import os
import shutil
import tomllib
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.toml"

def _resolve(raw: str, *, default: Path | None = None) -> Path: # config string to resolved absolute path
    if not raw or not raw.strip():
        if default is None:
            raise SystemExit("Error: missing required path in config.toml.")
        path = default
    else:
        # Expand ~ and $VARS, then make absolute
        path = Path(os.path.expandvars(os.path.expanduser(raw.strip())))

    return path.resolve()


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict:
    if not config_path.is_file():
        raise SystemExit(f"Error: config file not found at '{config_path}'.")

    with config_path.open("rb") as f:
        raw = tomllib.load(f)

    paths = raw.get("paths", {})

    watch = _resolve(paths.get("watch", ""), default=Path.home() / "Downloads")
    if not watch.is_dir():
        raise SystemExit(
            f"Error: watch folder '{watch}' does not exist.\n"
            f"Edit 'watch' in the [paths] section of config.toml."
        )

    destination = _resolve(paths.get("destination", ""), default=watch)

    categories_raw = raw.get("categories") # error check if categories is missing from toml
    if not categories_raw:
        raise SystemExit(
            "Error: no [categories] defined in config.toml.\n"
            "Add at least one [categories.<Name>] section."
        )

    categories = {
        category: {sub: tuple(exts) for sub, exts in subs.items()}
        for category, subs in raw["categories"].items()
    }

    return {
        "watch": watch,
        "destination": destination,
        "categories": categories,
    }