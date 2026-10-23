"""AC-14 / EC-3 -- duplicate card ids are a logical error."""

def test_ac_14_duplicate_card_ids(app, write_deck, card_factory):
    deck_path = write_deck({
        "name": "Duplicate Deck",
        "cards": [
            card_factory("vocab-1"),
            card_factory("vocab-1", front="other front"),
        ],
    })

    result = app("import", deck_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "error: duplicate card_id: vocab-1" in result.stderr


def test_ac_14_duplicate_detected_by_review(app, write_deck, card_factory):
    deck_path = write_deck({
        "name": "Duplicate Deck",
        "cards": [card_factory("vocab-1"), card_factory("vocab-1")],
    })

    result = app(
        "review", deck_path, "vocab-1", 3, "--reference-date", "2026-01-15"
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "error: duplicate card_id: vocab-1" in result.stderr
