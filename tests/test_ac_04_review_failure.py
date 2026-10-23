"""AC-4 -- review with grade 2 resets the card and lowers the ease factor."""

import json


def test_ac_04_review_failure(app, write_deck, card_factory):
    reviewed = card_factory(
        "word-1",
        reps=2,
        interval=6,
        ef=2.6,
        last_review="2026-01-22",
        next_review="2026-01-28",
    )
    deck_path = write_deck({"name": "Spanish 101", "cards": [reviewed]})

    result = app("review", deck_path, "word-1", 2, "--reference-date", "2026-02-07")

    assert result.returncode == 0, result.stderr
    card = json.loads(result.stdout)
    assert card["reps"] == 0
    assert card["ef"] == 2.28
    assert card["interval"] == 1
    assert card["next_review"] == "2026-02-08"
