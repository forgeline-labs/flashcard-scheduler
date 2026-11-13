"""AC-22 / EC-11 -- ease factor is clamped to a minimum of 1.3."""

import json


def test_ac_22_ef_floor(app, write_deck, card_factory):
    card = card_factory("card-x", ef=1.5, reps=4, interval=20)
    deck_path = write_deck({"name": "Floor Deck", "cards": [card]})

    result = app("review", deck_path, "card-x", 0, "--reference-date", "2026-01-15")

    assert result.returncode == 0, result.stderr
    updated = json.loads(result.stdout)
    assert updated["ef"] == 1.3
    assert updated["reps"] == 0
    assert updated["interval"] == 1
    assert updated["next_review"] == "2026-01-16"


def test_ec_11_repeated_failures_stay_at_floor(app, write_deck, card_factory):
    card = card_factory("card-x", ef=1.3, reps=0, interval=1)
    deck_path = write_deck({"name": "Floor Deck", "cards": [card]})

    result = app("review", deck_path, "card-x", 0, "--reference-date", "2026-01-15")

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["ef"] == 1.3
