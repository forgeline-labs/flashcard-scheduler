"""AC-16 -- JSON output is valid, pretty-printed, 2-space indented."""

import json


def test_ac_16_json_output_formatting(app, write_deck, card_factory):
    deck_path = write_deck({
        "name": "Format Deck",
        "cards": [card_factory("card-1", next_review="2026-01-14", reps=1, interval=1)],
    })

    result = app("due", deck_path, "--reference-date", "2026-01-15", "--json")

    assert result.returncode == 0, result.stderr
    assert result.stdout.endswith("\n")
    parsed = json.loads(result.stdout)
    assert isinstance(parsed, list) and len(parsed) == 1
    # No trailing commas, no comments, canonical 2-space indentation.
    assert result.stdout == json.dumps(parsed, indent=2) + "\n"
    for line in result.stdout.splitlines():
        assert "\t" not in line
