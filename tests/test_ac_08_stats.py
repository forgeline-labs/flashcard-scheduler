"""AC-8 -- aggregate statistics."""

import json

EXPECTED = {
    "name": "Mixed Deck",
    "total_cards": 5,
    "new_cards": 2,
    "learning_cards": 1,
    "learned_cards": 2,
    "average_ef": 2.56,
}


def test_ac_08_stats_text(app, fixtures_dir):
    result = app("stats", fixtures_dir / "mixed_deck.json")

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout == (
        "average_ef: 2.56\n"
        "learned_cards: 2\n"
        "learning_cards: 1\n"
        "name: Mixed Deck\n"
        "new_cards: 2\n"
        "total_cards: 5\n"
    )


def test_ac_08_stats_json(app, fixtures_dir):
    result = app("stats", fixtures_dir / "mixed_deck.json", "--json")

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == EXPECTED
