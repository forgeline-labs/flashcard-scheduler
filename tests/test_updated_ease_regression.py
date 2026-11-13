"""The current grade affects both the ease factor and this review's interval."""

import json

import pytest


@pytest.mark.parametrize("grade, expected_ef, expected_interval", [(3, 2.06, 19), (5, 2.3, 21)])
def test_interval_uses_this_reviews_ease(app, write_deck, card_factory, grade,
                                     expected_ef, expected_interval):
    deck = write_deck({"name": "Ease update", "cards": [card_factory(
        "practice", reps=4, interval=9, ef=2.2,
    )]})
    before = deck.read_bytes()
    result = app("review", deck, "practice", grade, "--reference-date", "2027-03-01")
    assert result.returncode == 0, result.stderr
    card = json.loads(result.stdout)
    assert card["ef"] == expected_ef
    assert card["interval"] == expected_interval
    assert deck.read_bytes() == before


def test_exact_integer_product_does_not_add_a_spurious_day(app, write_deck, card_factory):
    deck = write_deck({"name": "Exact product", "cards": [card_factory(
        "practice", reps=4, interval=100, ef=2.2,
    )]})
    result = app("review", deck, "practice", 4, "--reference-date", "2027-03-01")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["interval"] == 220
