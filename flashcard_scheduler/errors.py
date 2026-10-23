"""Error types used across the flashcard scheduler.

Every error carries the process exit code mandated by the specification:

* ``2`` -- I/O, parse, argument, or format error.
* ``1`` -- logical error (card not found, duplicate card id, ...).

``ValueError`` is part of the public contract of :func:`review_card`, so the
argument-level errors multiply inherit from it as well as from
:class:`FlashcardError`.
"""


class FlashcardError(Exception):
    """Base class for errors that map to a CLI exit code."""

    exit_code = 2

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ArgumentError(FlashcardError):
    """Invalid command line arguments."""

    exit_code = 2


class DeckFormatError(FlashcardError):
    """The deck payload does not match the documented JSON format."""

    exit_code = 2


class InvalidDateError(ValueError, FlashcardError):
    """A date string is not a valid ``YYYY-MM-DD`` value."""

    exit_code = 2

    def __init__(self, value=None):
        message = "invalid date format"
        super().__init__(message)
        self.value = value
        self.message = message


class InvalidGradeError(ValueError, FlashcardError):
    """A grade is not an integer in ``[0, 5]``."""

    exit_code = 2

    def __init__(self, value):
        message = "invalid grade: {}".format(value)
        super().__init__(message)
        self.value = value
        self.message = message


class StorageError(FlashcardError):
    """Reading or writing a deck file failed."""

    exit_code = 2


class DuplicateCardIdError(FlashcardError):
    """A deck contains two cards with the same ``card_id``."""

    exit_code = 1

    def __init__(self, card_id):
        super().__init__("duplicate card_id: {}".format(card_id))
        self.card_id = card_id


class CardNotFoundError(FlashcardError):
    """The requested card does not exist in the deck."""

    exit_code = 1

    def __init__(self, card_id):
        super().__init__("card not found: {}".format(card_id))
        self.card_id = card_id
