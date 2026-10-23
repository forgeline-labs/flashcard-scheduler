"""AC-19 / EC-9 -- permission denied on read and write."""

import json
import os
import stat

import pytest


def _skip_if_root():
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("running as root: permission bits are not enforced")


def test_ac_19_unreadable_deck(app, write_deck, card_factory):
    _skip_if_root()
    deck_path = write_deck({"name": "Locked", "cards": [card_factory("a")]})
    os.chmod(deck_path, 0)
    try:
        result = app("import", deck_path)
    finally:
        os.chmod(deck_path, stat.S_IRUSR | stat.S_IWUSR)

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: permission denied" in result.stderr


def test_ac_19_unwritable_deck_on_persist(app, write_deck, card_factory):
    _skip_if_root()
    deck_path = write_deck({"name": "Read Only", "cards": [card_factory("a")]})
    os.chmod(deck_path, stat.S_IRUSR)
    try:
        result = app(
            "review", deck_path, "a", 4,
            "--reference-date", "2026-01-15", "--persist",
        )
    finally:
        os.chmod(deck_path, stat.S_IRUSR | stat.S_IWUSR)

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: permission denied" in result.stderr


def test_ac_19_file_content_survives_failed_persist(app, write_deck, card_factory):
    _skip_if_root()
    deck_path = write_deck({"name": "Read Only", "cards": [card_factory("a")]})
    before = deck_path.read_text(encoding="utf-8")
    os.chmod(deck_path, stat.S_IRUSR)
    try:
        app("review", deck_path, "a", 4, "--reference-date", "2026-01-15", "--persist")
    finally:
        os.chmod(deck_path, stat.S_IRUSR | stat.S_IWUSR)

    assert json.loads(deck_path.read_text(encoding="utf-8")) == json.loads(before)
