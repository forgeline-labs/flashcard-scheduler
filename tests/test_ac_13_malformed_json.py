"""AC-13 / EC-2 / EC-8 -- malformed input files."""

def test_ac_13_malformed_json(app, tmp_path):
    deck_path = tmp_path / "deck.json"
    deck_path.write_text("{invalid json}", encoding="utf-8")

    result = app("import", deck_path)

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: invalid JSON" in result.stderr


def test_ec_02_missing_required_card_field(app, tmp_path):
    deck_path = tmp_path / "deck.json"
    deck_path.write_text(
        '{"name": "Broken", "cards": [{"card_id": "a", "front": "f"}]}',
        encoding="utf-8",
    )

    result = app("import", deck_path)

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error:" in result.stderr


def test_ec_08_file_not_found(app, tmp_path):
    missing = tmp_path / "does-not-exist.json"

    result = app("import", missing)

    assert result.returncode == 2
    assert result.stdout == ""
    assert "error: file not found" in result.stderr
