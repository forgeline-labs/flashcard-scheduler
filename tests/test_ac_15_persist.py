"""AC-15 -- --persist writes the updated deck back to disk."""

import json


def test_ac_15_persistence(app, write_deck, load_json, fixtures_dir):
    deck = json.loads((fixtures_dir / "new_cards_deck.json").read_text(encoding="utf-8"))
    deck_path = write_deck(deck)

    result = app(
        "review", deck_path, "word-1", 4,
        "--reference-date", "2026-01-15", "--persist",
    )

    assert result.returncode == 0, result.stderr
    on_disk = load_json(deck_path)
    card = on_disk["cards"][0]
    assert card["card_id"] == "word-1"
    assert card["reps"] == 1
    assert card["interval"] == 1
    assert card["last_review"] == "2026-01-15"
    assert card["next_review"] == "2026-01-16"
    # Other cards are preserved untouched.
    assert on_disk["cards"][1]["reps"] == 0
    assert on_disk["cards"][1]["next_review"] is None


def test_ac_15_without_persist_file_is_unchanged(app, write_deck, load_json, fixtures_dir):
    deck = json.loads((fixtures_dir / "new_cards_deck.json").read_text(encoding="utf-8"))
    deck_path = write_deck(deck)
    before = deck_path.read_text(encoding="utf-8")

    result = app("review", deck_path, "word-1", 4, "--reference-date", "2026-01-15")

    assert result.returncode == 0
    assert deck_path.read_text(encoding="utf-8") == before
