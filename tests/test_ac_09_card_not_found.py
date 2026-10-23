"""AC-9 -- reviewing a nonexistent card is a logical error."""

def test_ac_09_card_not_found(app, fixtures_dir):
    result = app(
        "review", fixtures_dir / "new_cards_deck.json", "vocab-99", 3,
        "--reference-date", "2026-01-15",
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "error: card not found: vocab-99" in result.stderr
