"""AC-20 -- deterministic output."""

def test_ac_20_determinism(app, fixtures_dir):
    first = app("stats", fixtures_dir / "mixed_deck.json", "--json")
    second = app("stats", fixtures_dir / "mixed_deck.json", "--json")

    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout
    assert first.stderr == second.stderr == ""
