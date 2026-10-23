"""Command line interface for the flashcard scheduler.

The CLI is a thin adapter over the library: it parses arguments, maps errors to
the documented exit codes, and renders JSON or human-readable text.  It never
consults the system clock; ``--reference-date`` is the only source of "now".
"""

import json
import sys

from . import __version__
from .dates import parse_date
from .deck import deck_stats, get_due_cards, load_deck, save_deck
from .errors import (
    ArgumentError,
    CardNotFoundError,
    FlashcardError,
    InvalidGradeError,
)
from .sm2 import review_card

USAGE = """\
usage:
  app import <deck.json> [--reference-date <YYYY-MM-DD>]
  app review <deck.json> <card-id> <grade> [--reference-date <YYYY-MM-DD>] [--persist]
  app due <deck.json> --reference-date <YYYY-MM-DD> [--json]
  app stats <deck.json> [--json]
  app --version
  app --help

subcommands:
  import   validate and normalize a deck JSON file, print it to stdout
  review   record a grade (0-5) for one card using SM-2
  due      list cards whose next_review is on or before the reference date
  stats    print aggregate deck statistics

options:
  --reference-date <YYYY-MM-DD>  explicit "today" (required by review and due)
  --json                         JSON output for due and stats
  --persist                      write the updated deck back after review

exit codes:
  0  success
  1  logical error (card not found, duplicate card_id)
  2  I/O, parse, argument, or format error
"""

_BOOL_OPTIONS = {"--json", "--persist"}
_VALUE_OPTIONS = {"--reference-date"}


def _parse_options(tokens, allowed_bools, allowed_values):
    """Split tokens into positionals and options.

    Supports both ``--opt value`` and ``--opt=value``.  Unknown options raise
    :class:`ArgumentError` (exit ``2``).
    """
    positionals = []
    options = {}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            positionals.extend(tokens[index + 1 :])
            break
        if token.startswith("--"):
            name, separator, inline_value = token.partition("=")
            if name in allowed_bools and name in _BOOL_OPTIONS:
                options[name] = True
            elif name in allowed_values and name in _VALUE_OPTIONS:
                if separator:
                    value = inline_value
                else:
                    index += 1
                    if index >= len(tokens):
                        raise ArgumentError("{} requires a value".format(name))
                    value = tokens[index]
                options[name] = value
            else:
                raise ArgumentError("unknown option: {}".format(name))
        else:
            # Single-dash tokens (e.g. a negative grade like "-1") are
            # positionals; only long "--options" are parsed as options.
            positionals.append(token)
        index += 1
    return positionals, options


def _require_positionals(positionals, names):
    if len(positionals) < len(names):
        missing = names[len(positionals)]
        raise ArgumentError("missing argument: {}".format(missing))
    if len(positionals) > len(names):
        raise ArgumentError("unexpected argument: {}".format(positionals[len(names)]))


def _parse_grade(text):
    try:
        grade = int(text, 10)
    except (TypeError, ValueError):
        raise InvalidGradeError(text) from None
    if grade < 0 or grade > 5:
        raise InvalidGradeError(text)
    return grade


def _required_reference_date(options):
    if "--reference-date" not in options:
        raise ArgumentError("--reference-date is required for this command")
    value = options["--reference-date"]
    parse_date(value)
    return value


def _optional_reference_date(options):
    if "--reference-date" not in options:
        return None
    value = options["--reference-date"]
    parse_date(value)
    return value


def _dump_json(payload):
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _cmd_import(tokens):
    positionals, options = _parse_options(
        tokens, allowed_bools={"--json"}, allowed_values={"--reference-date"}
    )
    _require_positionals(positionals, ["deck.json"])
    _optional_reference_date(options)
    deck = load_deck(positionals[0])
    sys.stdout.write(_dump_json(deck.to_dict()))
    return 0


def _cmd_review(tokens):
    positionals, options = _parse_options(
        tokens,
        allowed_bools={"--json", "--persist"},
        allowed_values={"--reference-date"},
    )
    _require_positionals(positionals, ["deck.json", "card-id", "grade"])
    deck_path, card_id, grade_text = positionals
    grade = _parse_grade(grade_text)
    reference_date = _required_reference_date(options)

    deck = load_deck(deck_path)
    card = deck.find(card_id)
    if card is None:
        raise CardNotFoundError(card_id)

    updated = review_card(card, grade, reference_date)
    if "--persist" in options:
        for index, existing in enumerate(deck.cards):
            if existing.card_id == card_id:
                deck.cards[index] = updated
                break
        save_deck(deck, deck_path)

    sys.stdout.write(_dump_json(updated.to_dict()))
    return 0


def _cmd_due(tokens):
    positionals, options = _parse_options(
        tokens, allowed_bools={"--json"}, allowed_values={"--reference-date"}
    )
    _require_positionals(positionals, ["deck.json"])
    reference_date = _required_reference_date(options)

    deck = load_deck(positionals[0])
    due = get_due_cards(deck, reference_date)

    if "--json" in options:
        sys.stdout.write(_dump_json([card.to_dict() for card in due]))
    elif due:
        sys.stdout.write("".join(
            "{}: {}\n".format(card.card_id, card.front) for card in due
        ))
    else:
        sys.stdout.write("no cards due\n")
    return 0


def _cmd_stats(tokens):
    positionals, options = _parse_options(
        tokens, allowed_bools={"--json"}, allowed_values={"--reference-date"}
    )
    _require_positionals(positionals, ["deck.json"])
    # Statistics are computed from stored state; a reference date is accepted
    # for symmetry but is not used.
    _optional_reference_date(options)

    deck = load_deck(positionals[0])
    stats = deck_stats(deck)

    if "--json" in options:
        sys.stdout.write(_dump_json(stats))
    else:
        sys.stdout.write("".join(
            "{}: {}\n".format(key, stats[key]) for key in sorted(stats)
        ))
    return 0


_COMMANDS = {
    "import": _cmd_import,
    "review": _cmd_review,
    "due": _cmd_due,
    "stats": _cmd_stats,
}


def main(argv=None):
    """Run the CLI and return the process exit code."""
    tokens = list(sys.argv[1:] if argv is None else argv)

    if not tokens:
        sys.stderr.write("error: missing command\n")
        return 2

    if tokens[0] in ("--version", "-V"):
        sys.stdout.write(__version__ + "\n")
        return 0

    if tokens[0] in ("--help", "-h") or "-h" in tokens or "--help" in tokens:
        sys.stdout.write(USAGE)
        return 0

    command = tokens[0]
    handler = _COMMANDS.get(command)
    if handler is None:
        sys.stderr.write("error: unknown command: {}\n".format(command))
        return 2

    try:
        return handler(tokens[1:])
    except FlashcardError as error:
        sys.stderr.write("error: {}\n".format(error.message))
        return error.exit_code
    except (OSError, ValueError) as error:
        sys.stderr.write("error: {}\n".format(error))
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
