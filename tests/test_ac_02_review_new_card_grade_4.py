"""AC-2 -- review a new card with grade 4."""

import json


def test_ac_02_review_new_card_grade_4(app, write_deck, card_factory):
    deck_path = write_deck({
        "name": "Spanish 101",
        "cards": [card_factory("word-1", front="hola", back="hello")],
    })

    result = app("review", deck_path, "word-1", 4, "--reference-date", "2026-01-15")

    assert result.returncode == 0
    assert result.stderr == ""
    card = json.loads(result.stdout)
    assert card["reps"] == 1
    assert card["ef"] == 2.5
    assert card["interval"] == 1
    assert card["last_review"] == "2026-01-15"
    assert card["next_review"] == "2026-01-16"
    assert card["created_at"] == "2026-01-01"
