"""The :class:`Card` value object."""

import math

from .dates import is_valid_date
from .errors import DeckFormatError

_REQUIRED_FIELDS = ("card_id", "front", "back")


def _as_float(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DeckFormatError("invalid value for {}: {!r}".format(field, value))
    try:
        number = float(value)
    except OverflowError:
        raise DeckFormatError(
            "invalid value for {}: {!r}".format(field, value)
        ) from None
    if not math.isfinite(number):
        # ``json`` accepts non-standard literals such as ``1e999`` (``inf``);
        # they cannot be scheduled and are therefore a format error.
        raise DeckFormatError("invalid value for {}: {!r}".format(field, value))
    return number


def _as_int(value, field):
    if isinstance(value, bool):
        raise DeckFormatError("invalid value for {}: {!r}".format(field, value))
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    raise DeckFormatError("invalid value for {}: {!r}".format(field, value))


def _as_text(value, field):
    if not isinstance(value, str):
        raise DeckFormatError("invalid value for {}: {!r}".format(field, value))
    return value


def _as_optional_date(value, field):
    if value is None:
        return None
    if not is_valid_date(value):
        raise DeckFormatError("invalid date format: {}".format(field))
    return value


class Card:
    """Represents a single flashcard."""

    def __init__(
        self,
        card_id,
        front,
        back,
        ef=2.5,
        interval=0,
        reps=0,
        last_review=None,
        next_review=None,
        created_at=None,
    ):
        self.card_id = card_id
        self.front = front
        self.back = back
        self.ef = ef
        self.interval = interval
        self.reps = reps
        self.last_review = last_review
        self.next_review = next_review
        self.created_at = created_at

    def to_dict(self):
        """Serialize to a JSON-compatible dict."""
        return {
            "card_id": self.card_id,
            "front": self.front,
            "back": self.back,
            "ef": self.ef,
            "interval": self.interval,
            "reps": self.reps,
            "last_review": self.last_review,
            "next_review": self.next_review,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize from a dict.

        Missing required fields, non-string values, and invalid dates raise
        :class:`~flashcard_scheduler.errors.DeckFormatError` (exit code ``2``).
        """
        if not isinstance(data, dict):
            raise DeckFormatError("card must be a JSON object")
        for field in _REQUIRED_FIELDS:
            if field not in data:
                raise DeckFormatError("missing required field: {}".format(field))
        card_id = _as_text(data["card_id"], "card_id")
        front = _as_text(data["front"], "front")
        back = _as_text(data["back"], "back")
        ef = _as_float(data.get("ef", 2.5), "ef")
        interval = _as_int(data.get("interval", 0), "interval")
        reps = _as_int(data.get("reps", 0), "reps")
        last_review = _as_optional_date(data.get("last_review"), "last_review")
        next_review = _as_optional_date(data.get("next_review"), "next_review")
        created_at = _as_optional_date(data.get("created_at"), "created_at")
        return cls(
            card_id=card_id,
            front=front,
            back=back,
            ef=ef,
            interval=interval,
            reps=reps,
            last_review=last_review,
            next_review=next_review,
            created_at=created_at,
        )

    def copy(self):
        """Return a shallow copy of the card (reviewing is functional)."""
        return Card(
            card_id=self.card_id,
            front=self.front,
            back=self.back,
            ef=self.ef,
            interval=self.interval,
            reps=self.reps,
            last_review=self.last_review,
            next_review=self.next_review,
            created_at=self.created_at,
        )

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __repr__(self):
        return "Card(card_id={!r})".format(self.card_id)
