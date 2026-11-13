"""AC-17 / AC-18 -- --version and --help."""

def test_ac_17_version(app):
    result = app("--version")

    assert result.returncode == 0
    assert result.stderr == ""
    assert "0.1.0" in result.stdout


def test_ac_18_help(app):
    result = app("--help")

    assert result.returncode == 0
    assert result.stderr == ""
    for expected in ("import", "review", "due", "stats", "--reference-date", "usage"):
        assert expected in result.stdout
