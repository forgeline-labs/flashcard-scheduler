"""The SM-2 spaced repetition algorithm.

Only the SuperMemo 2 algorithm is implemented.  No sub-day intervals, custom
spacing, or alternative schedulers exist in v0.1.
"""

import math

from .dates import add_days, parse_date
from .errors import InvalidGradeError

MIN_EF = 1.3
INITIAL_EF = 2.5

# Keeps binary floating point noise (e.g. 2.2799999999999994) out of the
# serialized state while retaining far more precision than the algorithm needs.
_EF_PRECISION = 10


def _validate_grade(grade):
    if isinstance(grade, bool) or not isinstance(grade, int):
        raise InvalidGradeError(grade)
    if grade < 0 or grade > 5:
        raise InvalidGradeError(grade)
    return grade


def _validate_reference_date(reference_date):
    return parse_date(reference_date)


def review_card(card, grade, reference_date):
    """Apply SM-2 to *card* for *grade* on *reference_date*.

    Returns a new :class:`Card`; the input card is never modified.

    Interval rules (as pinned by the acceptance criteria):

    * ``n' == 0`` or ``n == 0`` -> 1 day (restart / first review)
    * ``n' == 1`` -> 1 day
    * ``n' == 2`` -> 6 days
    * otherwise -> ``ceil(I * EF)`` using the card's ease factor before this
      review.  This mirrors AC-3 (``ceil(6 * 2.6) == 16``) and AC-21
      (``ceil(100 * 2.8) == 280``).

    Raises :class:`ValueError` when the grade is outside ``[0, 5]`` or the
    reference date is not a valid ``YYYY-MM-DD`` string.
    """
    grade = _validate_grade(grade)
    _validate_reference_date(reference_date)

    old_reps = card.reps
    old_interval = card.interval
    old_ef = float(card.ef)

    if grade >= 3:
        new_reps = old_reps + 1
    else:
        new_reps = 0

    new_ef = old_ef + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    new_ef = max(MIN_EF, round(new_ef, _EF_PRECISION))

    if new_reps == 0 or old_reps == 0:
        new_interval = 1
    elif new_reps == 1:
        new_interval = 1
    elif new_reps == 2:
        new_interval = 6
    else:
        new_interval = max(1, int(math.ceil(old_interval * old_ef)))

    updated = card.copy()
    updated.ef = new_ef
    updated.interval = new_interval
    updated.reps = new_reps
    updated.last_review = reference_date
    updated.next_review = add_days(reference_date, new_interval)
    return updated
