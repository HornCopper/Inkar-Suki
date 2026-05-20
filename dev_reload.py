import os
import subprocess
import sys
from pathlib import Path

from watchfiles import watch


ROOT = Path(__file__).resolve().parent
WATCH_PATHS = [ROOT / "bot.py", ROOT / "src"]
IGNORED_PARTS = {
    "__pycache__",
    "data",
    "cache",
    "assets",
    "templates",
}
SOURCE_SUFFIXES = {".py", ".toml", ".yml", ".yaml", ".json"}


def source_filter(_, path: str) -> bool:
    file_path = Path(path)
    if file_path.name == "bot.py":
        return True
    if not file_path.is_file() or file_path.suffix not in SOURCE_SUFFIXES:
        return False
    try:
        relative_parts = file_path.relative_to(ROOT / "src").parts
    except ValueError:
        return False
    return not any(part in IGNORED_PARTS for part in relative_parts)


def start_bot() -> subprocess.Popen:
    env = os.environ.copy()
    for key in ("RELOAD", "HOT_RELOAD", "FASTAPI_RELOAD", "FASTAPI_RELOAD_DIRS"):
        env.pop(key, None)
    return subprocess.Popen([sys.executable, "bot.py"], cwd=ROOT, env=env)


def stop_bot(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def main() -> None:
    os.environ.setdefault("WATCHFILES_FORCE_POLLING", "true")
    process = start_bot()
    print(f"Started bot process: {process.pid}", flush=True)
    try:
        for changes in watch(*WATCH_PATHS, watch_filter=source_filter):
            changed_files = [str(path) for _, path in changes]
            print("Changes detected, restarting bot:", ", ".join(changed_files), flush=True)
            stop_bot(process)
            process = start_bot()
            print(f"Restarted bot process: {process.pid}", flush=True)
    finally:
        stop_bot(process)


if __name__ == "__main__":
    main()
