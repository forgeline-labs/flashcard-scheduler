"""Regression tests for review findings (exit-code precedence and overflow)."""


def test_format_error_takes_precedence_over_duplicate(
    app, write_deck, card_factory
):
    """A malformed card (exit 2) wins over duplicate ids (exit 1)."""
    malformed = card_factory("vocab-3")
    del malformed["back"]
    deck_path = write_deck({
        "name": "Broken Deck",
        "cards": [
            card_factory("vocab-1"),
            card_factory("vocab-1"),
            malformed,
        ],
    })

    result = app("import", deck_path)

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: missing required field: back" in result.stderr


def test_non_finite_ef_is_a_format_error(app, write_deck, card_factory):
    """``ef: 1e999`` parses as ``inf`` and must not reach the scheduler."""
    deck_path = write_deck({
        "name": "Infinite EF",
        "cards": [card_factory("vocab-1", ef=float("inf"), interval=100, reps=3)],
    })

    result = app(
        "review", deck_path, "vocab-1", 3, "--reference-date", "2026-01-15"
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error:" in result.stderr


def test_reference_date_overflow_is_a_format_error(app, write_deck, card_factory):
    """Adding the interval to 9999-12-31 overflows ``datetime.date``."""
    deck_path = write_deck({
        "name": "Edge Date",
        "cards": [card_factory("vocab-1")],
    })

    result = app(
        "review", deck_path, "vocab-1", 3, "--reference-date", "9999-12-31"
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error:" in result.stderr


def test_huge_interval_is_a_format_error(app, write_deck, card_factory):
    """An interval too large for SM-2 arithmetic is reported, not a traceback."""
    deck_path = write_deck({
        "name": "Huge Interval",
        "cards": [card_factory("vocab-1", interval=10**400, reps=3)],
    })

    result = app(
        "review", deck_path, "vocab-1", 3, "--reference-date", "2026-01-15"
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error:" in result.stderr
