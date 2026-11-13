"""AC-11 / EC-6 / EC-16 -- --reference-date is required for review and due."""

import pytest


def test_ac_11_missing_reference_date_review(app, fixtures_dir):
    result = app("review", fixtures_dir / "new_cards_deck.json", "word-1", 3)

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: --reference-date is required" in result.stderr


def test_ec_06_missing_reference_date_due(app, fixtures_dir):
    result = app("due", fixtures_dir / "new_cards_deck.json")

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: --reference-date is required" in result.stderr


@pytest.mark.parametrize("extra", [[], ["--persist"]])
def test_ec_16_persist_without_reference_date(app, fixtures_dir, extra):
    result = app(
        "review", fixtures_dir / "new_cards_deck.json", "word-1", 4, *extra
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: --reference-date is required" in result.stderr
