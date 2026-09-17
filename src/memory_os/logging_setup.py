from __future__ import annotations

import logging
from pathlib import Path

_CONFIGURED = False


def configure_logging(db_path: str | Path, verbose: bool = False) -> None:
    """Configure file logging under the same directory as the SQLite db.

    Local-first: nothing leaves the machine, log lives beside memory.db.
    Idempotent so repeated calls (e.g. in tests) don't stack handlers.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return
    log_dir = Path(db_path).resolve().parent
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "memory-os.log"

    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Attach to the true root logger, not a fixed "memory_os" name — a
    # module run via `python -m memory_os.cli` gets __name__ == "__main__",
    # not "memory_os.cli", so a per-module logger.getLogger(__name__) call
    # from the entrypoint would never reach a handler attached only to a
    # "memory_os"-named logger. Root catches every name, always.
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
    root.addHandler(file_handler)

    if verbose:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root.addHandler(stream_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger"]
