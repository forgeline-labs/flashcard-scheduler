"""Deterministic storage faults must preserve the original deck byte for byte."""

import builtins
import os
from unittest.mock import patch

import pytest

from flashcard_scheduler.deck import load_deck, save_deck
from flashcard_scheduler.errors import StorageError


class InterruptedWrite:
    def __init__(self, handle):
        self.handle = handle

    def __enter__(self):
        self.handle.__enter__()
        return self

    def __exit__(self, *args):
        return self.handle.__exit__(*args)

    def __getattr__(self, name):
        return getattr(self.handle, name)

    def write(self, payload):
        self.handle.write(payload[:8])
        self.handle.flush()
        raise OSError("simulated interrupted write")


@pytest.mark.parametrize("fault", ["write", "fsync", "replace"])
def test_failed_save_preserves_original(tmp_path, fault):
    target = tmp_path / "café.json"
    original = b'{"name":"original", "cards":[]}\n'
    target.write_bytes(original)
    deck = load_deck(target)
    deck.name = "changed"
    original_open, original_fdopen = builtins.open, os.fdopen

    def interrupted_open(*args, **kwargs):
        handle = original_open(*args, **kwargs)
        return InterruptedWrite(handle) if "w" in str(args[1:2]) else handle

    def interrupted_fdopen(*args, **kwargs):
        return InterruptedWrite(original_fdopen(*args, **kwargs))

    with patch(
        "builtins.open", side_effect=interrupted_open if fault == "write" else original_open
    ):
        with patch(
            "os.fdopen", side_effect=interrupted_fdopen if fault == "write" else original_fdopen
        ):
            with patch(
                "os." + (fault if fault != "write" else "fsync"),
                side_effect=OSError("simulated fault") if fault != "write" else None,
            ):
                with pytest.raises(StorageError):
                    save_deck(deck, target)
    assert target.read_bytes() == original
    assert sorted(p.name for p in tmp_path.iterdir()) == [target.name]


def test_successful_save_fsyncs_before_replace(tmp_path):
    target = tmp_path / "deck.json"
    target.write_text('{"name":"a", "cards":[]}', encoding="utf-8")
    deck = load_deck(target)
    deck.name = "ação"
    events = []
    original_fsync, original_replace = os.fsync, os.replace

    def sync(fd):
        events.append("fsync")
        return original_fsync(fd)

    def replace(source, destination):
        assert os.path.dirname(source) == str(tmp_path)
        events.append("replace")
        return original_replace(source, destination)

    with patch("os.fsync", side_effect=sync), patch("os.replace", side_effect=replace):
        save_deck(deck, target)
    assert events == ["fsync", "replace"]
    assert load_deck(target).name == "ação"
    assert b"\r\n" not in target.read_bytes()


def test_read_permission_error_is_controlled_on_every_platform(tmp_path):
    with patch("builtins.open", side_effect=PermissionError("access denied")):
        with pytest.raises(StorageError, match="permission denied"):
            load_deck(tmp_path / "locked.json")
