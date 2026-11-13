"""Flashcard Scheduler -- SM-2 spaced repetition for JSON flashcard decks."""

__version__ = "0.1.0"

from .card import Card
from .deck import Deck, deck_stats, get_due_cards, load_deck, save_deck
from .errors import (
    ArgumentError,
    CardNotFoundError,
    DeckFormatError,
    DuplicateCardIdError,
    FlashcardError,
    InvalidDateError,
    InvalidGradeError,
    StorageError,
)
from .sm2 import review_card

__all__ = [
    "ArgumentError",
    "Card",
    "CardNotFoundError",
    "Deck",
    "DeckFormatError",
    "DuplicateCardIdError",
    "FlashcardError",
    "InvalidDateError",
    "InvalidGradeError",
    "StorageError",
    "__version__",
    "deck_stats",
    "get_due_cards",
    "load_deck",
    "review_card",
    "save_deck",
]
