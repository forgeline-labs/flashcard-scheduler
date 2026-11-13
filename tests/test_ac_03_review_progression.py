"""AC-3 -- two consecutive grade-5 reviews, first one persisted."""

import json


def test_ac_03_review_twice_grade_5(app, write_deck, load_json, card_factory):
    # State after AC-2.
    state_after_ac2 = card_factory(
        "word-1",
        front="hola",
        back="hello",
        reps=1,
        interval=1,
        ef=2.5,
        last_review="2026-01-15",
        next_review="2026-01-16",
    )
    deck_path = write_deck({"name": "Spanish 101", "cards": [state_after_ac2]})

    first = app(
        "review", deck_path, "word-1", 5,
        "--reference-date", "2026-01-16", "--persist",
    )
    assert first.returncode == 0, first.stderr
    assert first.stderr == ""
    card = json.loads(first.stdout)
    assert card["reps"] == 2
    assert card["ef"] == 2.6
    assert card["interval"] == 6
    assert card["next_review"] == "2026-01-22"

    # --persist wrote the updated state to disk.
    persisted = load_json(deck_path)["cards"][0]
    assert persisted["reps"] == 2
    assert persisted["interval"] == 6
    assert persisted["next_review"] == "2026-01-22"

    second = app("review", deck_path, "word-1", 5, "--reference-date", "2026-01-22")
    assert second.returncode == 0, second.stderr
    card = json.loads(second.stdout)
    assert card["reps"] == 3
    assert card["interval"] == 17
    assert card["next_review"] == "2026-02-08"
