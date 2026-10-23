"""AC-7 -- no cards due."""

import json


def test_ac_07_no_cards_due(app, write_deck, card_factory):
    deck = {
        "name": "Future Deck",
        "cards": [
            card_factory("later", next_review="2026-01-20", reps=1, interval=1),
            card_factory("never"),
        ],
    }
    deck_path = write_deck(deck)

    text = app("due", deck_path, "--reference-date", "2026-01-14")
    assert text.returncode == 0, text.stderr
    assert text.stdout == "no cards due\n"

    json_result = app("due", deck_path, "--reference-date", "2026-01-14", "--json")
    assert json_result.returncode == 0, json_result.stderr
    assert json.loads(json_result.stdout) == []


def test_ac_07_due_includes_cards_reviewed_on_the_reference_date(app, write_deck, card_factory):
    deck = {
        "name": "Boundary Deck",
        "cards": [card_factory("today", next_review="2026-01-15", reps=1, interval=1)],
    }
    deck_path = write_deck(deck)

    result = app("due", deck_path, "--reference-date", "2026-01-15")

    assert result.returncode == 0
    assert result.stdout == "today: front of today\n"
