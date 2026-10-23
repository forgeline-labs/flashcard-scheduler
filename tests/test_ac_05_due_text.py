"""AC-5 -- due cards query in human-readable text."""

def test_ac_05_due_cards_text(app, write_deck, card_factory):
    deck = {
        "name": "Due Deck",
        "cards": [
            card_factory("B", front="beta", next_review="2026-01-15", reps=1, interval=1),
            card_factory("A", front="alpha", next_review="2026-01-14", reps=1, interval=1),
            card_factory("C", front="gamma", next_review="2026-01-16", reps=1, interval=1),
        ],
    }
    deck_path = write_deck(deck)

    result = app("due", deck_path, "--reference-date", "2026-01-15")

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout == "A: alpha\nB: beta\n"
