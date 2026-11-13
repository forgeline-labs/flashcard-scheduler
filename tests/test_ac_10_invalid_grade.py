"""AC-10 -- invalid grade."""

import pytest


@pytest.mark.parametrize("grade", ["7", "-1", "abc", "2.5"])
def test_ac_10_invalid_grade(app, fixtures_dir, grade):
    result = app(
        "review", fixtures_dir / "new_cards_deck.json", "word-1", grade,
        "--reference-date", "2026-01-15",
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: invalid grade" in result.stderr
