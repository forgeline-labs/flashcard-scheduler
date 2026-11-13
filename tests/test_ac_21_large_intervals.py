"""AC-21 -- large intervals are computed with ceiling."""

import datetime
import json


def test_ac_21_large_intervals(app, write_deck, card_factory):
    card = card_factory(
        "card-x", reps=10, interval=100, ef=2.8,
        last_review="2025-10-07", next_review="2026-01-15",
    )
    deck_path = write_deck({"name": "Long Deck", "cards": [card]})

    result = app("review", deck_path, "card-x", 5, "--reference-date", "2026-01-15")

    assert result.returncode == 0, result.stderr
    updated = json.loads(result.stdout)
    assert updated["interval"] == 290
    expected_next = (
        datetime.date(2026, 1, 15) + datetime.timedelta(days=290)
    ).isoformat()
    assert updated["next_review"] == expected_next
    assert updated["reps"] == 11
