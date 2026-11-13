"""Shared fixtures for the black-box acceptance test suite.

Tests only ever invoke the ``./app`` executable through a subprocess; they do
not import the implementation package.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def app():
    """Run the CLI and return the completed process."""

    def run(*args, cwd=None, timeout=60):
        return subprocess.run(
            [sys.executable, str(APP)] + [str(arg) for arg in args],
            cwd=str(cwd or ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )

    return run


@pytest.fixture
def card_factory():
    """Build a card dict with documented defaults."""

    def make(card_id="card-1", **overrides):
        card = {
            "card_id": card_id,
            "front": "front of {}".format(card_id),
            "back": "back of {}".format(card_id),
            "ef": 2.5,
            "interval": 0,
            "reps": 0,
            "last_review": None,
            "next_review": None,
            "created_at": "2026-01-01",
        }
        card.update(overrides)
        return card

    return make


@pytest.fixture
def write_deck(tmp_path):
    """Write a deck dict to a temporary JSON file and return its path."""

    def write(deck, name="deck.json"):
        path = tmp_path / name
        path.write_text(json.dumps(deck, indent=2), encoding="utf-8")
        return path

    return write


@pytest.fixture
def load_json():
    """Read a JSON file from disk."""

    def load(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    return load


@pytest.fixture
def fixtures_dir():
    return FIXTURES
