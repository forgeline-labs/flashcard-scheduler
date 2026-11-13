#!/usr/bin/env python3
"""Repository entry point for the Flashcard Scheduler CLI."""

import os
import sys

for stream in (sys.stdin, sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", newline="\n")

# Make the package importable no matter which directory the wrapper is run
# from (e.g. ``/path/to/repo/app due deck.json ...``).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flashcard_scheduler.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
