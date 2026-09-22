import os
import shutil
import tomllib
from pathlib import Path

EXAMPLE_CONFIG_PATH = Path(__file__).parent / "config.example.toml"

# User config locations, in priority order.
# First match wins.
USER_CONFIG_LOCATIONS = [
    Path.cwd() / "config.toml",                    # project-local override
    Path.home() / ".file_organizer" / "config.toml" # home fallback
]


def ensure_config() -> Path:
    """Return the path to the user's config, creating it from the example if needed."""
    # If a user config exists in any known location, use it
    for path in USER_CONFIG_LOCATIONS:
        if path.is_file():
            return path

    # No user config exists — create one in the home directory
    target = USER_CONFIG_LOCATIONS[-1]
    target.parent.mkdir(parents=True, exist_ok=True)

    if not EXAMPLE_CONFIG_PATH.is_file():
        raise SystemExit(
            f"Error: example config missing at '{EXAMPLE_CONFIG_PATH}'.\n"
            "The package appears to be corrupted. Try reinstalling."
        )

    shutil.copy(EXAMPLE_CONFIG_PATH, target)
    print(f"Created default config at {target}")
    print("Edit it to change the watch folder or categories.")
    return target


def _resolve(raw: str, *, default: Path | None = None) -> Path:
    if not raw or not raw.strip():
        if default is None:
            raise SystemExit("Error: missing required path in config.toml.")
        path = default
    else:
        path = Path(os.path.expandvars(os.path.expanduser(raw.strip())))
    return path.resolve()


def load_config() -> dict:
    config_path = ensure_config()

    with config_path.open("rb") as f:
        raw = tomllib.load(f)

    paths = raw.get("paths", {})

    watch = _resolve(paths.get("watch", ""), default=Path.home() / "Downloads")
    if not watch.is_dir():
        raise SystemExit(
            f"Error: watch folder '{watch}' does not exist.\n"
            f"Edit 'watch' in the [paths] section of {config_path}."
        )

    destination = _resolve(paths.get("destination", ""), default=watch)

    categories_raw = raw.get("categories")
    if not categories_raw:
        raise SystemExit(
            f"Error: no [categories] defined in {config_path}.\n"
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