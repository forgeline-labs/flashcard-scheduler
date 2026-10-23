"""AC-12 / EC-7 -- invalid reference dates."""

import pytest


@pytest.mark.parametrize(
    "value",
    ["01-15-2026", "2026-02-30", "2026-13-01", "not-a-date", "2026-1-5"],
)
def test_ac_12_invalid_date_format(app, fixtures_dir, value):
    result = app(
        "review", fixtures_dir / "new_cards_deck.json", "word-1", 3,
        "--reference-date", value,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: invalid date format" in result.stderr


def test_ac_12_invalid_date_on_import(app, fixtures_dir):
    result = app(
        "import", fixtures_dir / "new_cards_deck.json",
        "--reference-date", "2026-02-30",
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: invalid date format" in result.stderr
