"""AC-6 -- due cards query as JSON."""

import json


def test_ac_06_due_cards_json(app, write_deck, card_factory):
    deck = {
        "name": "Due Deck",
        "cards": [
            card_factory("B", front="beta", next_review="2026-01-15", reps=1, interval=1),
            card_factory("A", front="alpha", next_review="2026-01-14", reps=1, interval=1),
            card_factory("C", front="gamma", next_review="2026-01-16", reps=1, interval=1),
        ],
    }
    deck_path = write_deck(deck)

    result = app("due", deck_path, "--reference-date", "2026-01-15", "--json")

    assert result.returncode == 0, result.stderr
    cards = json.loads(result.stdout)
    assert [card["card_id"] for card in cards] == ["A", "B"]
    assert cards[0]["front"] == "alpha"
    assert cards[1]["front"] == "beta"
