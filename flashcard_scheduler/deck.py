"""Deck model, due-card queries, statistics, and JSON file storage."""

import json
import os
import stat
import tempfile

from .card import Card
from .dates import parse_date
from .errors import DeckFormatError, DuplicateCardIdError, StorageError


class Deck:
    """Represents a deck of flashcards."""

    def __init__(self, name, cards=None):
        self.name = name
        self.cards = cards or []

    def to_dict(self):
        """Serialize to a JSON-compatible dict."""
        return {
            "name": self.name,
            "cards": [card.to_dict() for card in self.cards],
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize from a dict, validating the documented format."""
        if not isinstance(data, dict):
            raise DeckFormatError("deck must be a JSON object")
        if "name" not in data:
            raise DeckFormatError("missing required field: name")
        if "cards" not in data:
            raise DeckFormatError("missing required field: cards")
        if not isinstance(data["name"], str):
            raise DeckFormatError("invalid value for name")
        if not isinstance(data["cards"], list):
            raise DeckFormatError("invalid value for cards")

        # Validate every card before checking for duplicates so that a format
        # error (exit 2) takes precedence over a duplicate id (exit 1), as
        # documented by the exit-code precedence ``2 > 1 > 0``.
        cards = [Card.from_dict(raw_card) for raw_card in data["cards"]]

        seen = set()
        for card in cards:
            if card.card_id in seen:
                raise DuplicateCardIdError(card.card_id)
            seen.add(card.card_id)
        return cls(name=data["name"], cards=cards)

    def find(self, card_id):
        """Return the card with *card_id*, or ``None``."""
        for card in self.cards:
            if card.card_id == card_id:
                return card
        return None


def get_due_cards(deck, reference_date):
    """Return cards whose ``next_review`` is on or before *reference_date*.

    Results are ordered by ``next_review`` ascending, then ``card_id``
    ascending.  The deck is not modified.  Cards that were never reviewed
    (``next_review`` is ``None``) are not due.
    """
    parse_date(reference_date)
    due = [
        card
        for card in deck.cards
        if card.next_review is not None and card.next_review <= reference_date
    ]
    due.sort(key=lambda card: (card.next_review, card.card_id))
    return due


def deck_stats(deck):
    """Return the aggregate statistics object for *deck*."""
    total = len(deck.cards)
    new_cards = sum(1 for card in deck.cards if card.reps == 0)
    learning_cards = sum(1 for card in deck.cards if 1 <= card.reps <= 2)
    learned_cards = sum(1 for card in deck.cards if card.reps >= 3)
    if total:
        average_ef = round(sum(card.ef for card in deck.cards) / total, 2)
    else:
        average_ef = 0.0
    return {
        "name": deck.name,
        "total_cards": total,
        "new_cards": new_cards,
        "learning_cards": learning_cards,
        "learned_cards": learned_cards,
        "average_ef": average_ef,
    }


def _json_snippet(text, error):
    lines = text.splitlines()
    if 0 < error.lineno <= len(lines):
        snippet = lines[error.lineno - 1].strip()
    else:
        snippet = ""
    if not snippet:
        snippet = error.msg
    if len(snippet) > 120:
        snippet = snippet[:117] + "..."
    return snippet


def load_deck(filepath):
    """Load a :class:`Deck` from a UTF-8 JSON file.

    Raises :class:`StorageError` (exit ``2``) for I/O and JSON parse problems
    and :class:`DuplicateCardIdError` (exit ``1``) for duplicate ids.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as handle:
            text = handle.read()
    except FileNotFoundError:
        raise StorageError("file not found: {}".format(filepath)) from None
    except IsADirectoryError:
        raise StorageError("file not found: {}".format(filepath)) from None
    except PermissionError:
        raise StorageError("permission denied: {}".format(filepath)) from None
    except UnicodeDecodeError:
        raise StorageError("invalid JSON in file: {}".format(filepath)) from None
    except OSError:
        raise StorageError("cannot read file: {}".format(filepath)) from None

    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        snippet = _json_snippet(text, error)
        raise StorageError(
            "invalid JSON at line {}: {}".format(error.lineno, snippet)
        ) from None
    return Deck.from_dict(data)


def save_deck(deck, filepath):
    """Commit a UTF-8 deck only after writing and syncing a sibling temporary."""
    payload = json.dumps(deck.to_dict(), indent=2, ensure_ascii=False) + "\n"
    target = os.path.abspath(filepath)
    temporary = None
    try:
        # Atomic replacement must still respect a deliberately read-only deck.
        mode = stat.S_IMODE(os.stat(target).st_mode) if os.path.exists(target) else None
        if mode is not None and not mode & 0o222:
            raise PermissionError("read-only deck")
        descriptor, temporary = tempfile.mkstemp(dir=os.path.dirname(target), prefix=".deck-")
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, target)
        temporary = None
    except PermissionError:
        raise StorageError("permission denied: {}".format(filepath)) from None
    except OSError:
        raise StorageError("cannot write file: {}".format(filepath)) from None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass
