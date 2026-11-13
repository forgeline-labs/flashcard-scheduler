"""AC-1 -- import and normalize a deck."""

import json


def test_ac_01_import_normalizes_deck(app, fixtures_dir):
    deck_path = fixtures_dir / "new_cards_deck.json"
    expected = json.loads(deck_path.read_text(encoding="utf-8"))

    result = app("import", deck_path)

    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == expected
