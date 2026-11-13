"""Edge-case coverage (EC-1, EC-10, EC-12 -- EC-15, EC-17)."""

import json


def test_ec_01_empty_deck(app, fixtures_dir):
    deck_path = fixtures_dir / "empty_deck.json"

    imported = app("import", deck_path)
    assert imported.returncode == 0
    assert json.loads(imported.stdout) == {"name": "Empty Deck", "cards": []}

    due = app("due", deck_path, "--reference-date", "2026-01-15")
    assert due.returncode == 0
    assert due.stdout == "no cards due\n"

    stats = app("stats", deck_path, "--json")
    assert stats.returncode == 0
    payload = json.loads(stats.stdout)
    assert payload["total_cards"] == 0
    assert payload["new_cards"] == 0
    assert payload["learning_cards"] == 0
    assert payload["learned_cards"] == 0


def test_ec_10_new_card_grade_3(app, write_deck, card_factory):
    deck_path = write_deck({"name": "D", "cards": [card_factory("a")]})

    result = app("review", deck_path, "a", 3, "--reference-date", "2026-01-15")

    assert result.returncode == 0, result.stderr
    card = json.loads(result.stdout)
    assert card["reps"] == 1
    assert card["interval"] == 1
    assert card["next_review"] == "2026-01-16"


def test_ec_13_leap_year_arithmetic(app, write_deck, card_factory):
    deck_path = write_deck({"name": "D", "cards": [card_factory("a")]})

    result = app("review", deck_path, "a", 3, "--reference-date", "2026-02-28")

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["next_review"] == "2026-03-01"


def test_ec_13_actual_leap_day(app, write_deck, card_factory):
    deck_path = write_deck({"name": "D", "cards": [card_factory("a")]})

    result = app("review", deck_path, "a", 3, "--reference-date", "2028-02-28")

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["next_review"] == "2028-02-29"


def test_ec_14_due_order_same_date(app, write_deck, card_factory):
    cards = [
        card_factory(card_id, next_review="2026-01-15", reps=1, interval=1)
        for card_id in ("C", "A", "B")
    ]
    deck_path = write_deck({"name": "D", "cards": cards})

    result = app("due", deck_path, "--reference-date", "2026-01-15")

    assert result.returncode == 0
    assert [line.split(":")[0] for line in result.stdout.splitlines()] == ["A", "B", "C"]


def test_ec_15_card_ids_are_case_sensitive(app, write_deck, card_factory):
    deck_path = write_deck({
        "name": "D",
        "cards": [card_factory("Vocab-1"), card_factory("vocab-1")],
    })

    result = app("review", deck_path, "vocab-1", 3, "--reference-date", "2026-01-15")

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["card_id"] == "vocab-1"


def test_ec_17_reviews_are_independent(app, write_deck, card_factory):
    deck_path = write_deck({"name": "D", "cards": [card_factory("a")]})

    first = app("review", deck_path, "a", 4, "--reference-date", "2026-01-15")
    second = app("review", deck_path, "a", 4, "--reference-date", "2026-01-15")

    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout
