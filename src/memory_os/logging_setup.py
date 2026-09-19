from __future__ import annotations

import logging
from pathlib import Path

# Marks a handler this module added, so close_logging() only ever
# touches handlers it owns - never a caller's own logging setup
# (e.g. a test runner's own handlers on the root logger).
_MANAGED_ATTR = "_memory_os_managed"


def configure_logging(db_path: str | Path, verbose: bool = False) -> None:
    """Configure file logging under the same directory as the SQLite db.

    Local-first: nothing leaves the machine, log lives beside memory.db.
    Always closes any handler a previous call attached before adding a
    new one - repeated calls (a real re-init, or many `main()` calls in
    one process, as the test suite does) never stack handlers *or*
    leak an open file handle. That leak was a real, Windows-only bug:
    POSIX allows deleting a file that's still open; Windows refuses,
    so a leaked handler pointing into a test's own temporary directory
    made that directory's own cleanup fail with a PermissionError —
    caught only once a real Windows CI runner existed to catch it.
    """
    close_logging()
    log_dir = Path(db_path).resolve().parent
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "memory-os.log"

    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    setattr(file_handler, _MANAGED_ATTR, True)

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
        setattr(stream_handler, _MANAGED_ATTR, True)
        root.addHandler(stream_handler)


def close_logging() -> None:
    """Detach and close every handler `configure_logging` has ever
    attached to the root logger. Safe to call even if nothing was
    configured yet (a no-op then). Called from `cli.main()`'s own
    `finally` block so each CLI invocation cleans up after itself,
    same discipline as `MemoryOSService.close()`.
    """
    root = logging.getLogger()
    for handler in list(root.handlers):
        if getattr(handler, _MANAGED_ATTR, False):
            root.removeHandler(handler)
            handler.close()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


__all__ = ["close_logging", "configure_logging", "get_logger"]
