"""PyInstaller entry point for the packaged desktop application.

Deliberately not the CLI's `main()` — a packaged end-user build always
launches straight into the GUI, with no argument parsing, no console
window, and an implicit `init` (`MemoryOSService()`'s own constructor
creates the database/schema in the OS-appropriate app-data directory
if it doesn't exist yet). The CLI (`memory_os.cli:main`) remains a
separate, unpackaged entry point for development/testing use.
"""

from __future__ import annotations

import sys

from memory_os.logging_setup import configure_logging
from memory_os.service import MemoryOSService, default_data_dir


def main() -> int:
    db_path = default_data_dir() / "memory.db"
    configure_logging(db_path, verbose=False)
    service = MemoryOSService(db_path)
    try:
        from memory_os.gui import run_app

        return run_app(service)
    finally:
        service.close()


if __name__ == "__main__":
    sys.exit(main())
