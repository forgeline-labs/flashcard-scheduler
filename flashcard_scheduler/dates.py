"""Explicit-date helpers.

The tool never reads the system clock: every date is supplied by the caller as
an ISO 8601 ``YYYY-MM-DD`` string.  Dates are stored and compared as strings
(lexicographic ordering is chronological for this format) and converted to
``datetime.date`` only when day arithmetic is required.
"""

import datetime
import re

from .errors import InvalidDateError, ScheduleError

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_date(value):
    """Return a :class:`datetime.date` for a strict ``YYYY-MM-DD`` string.

    Raises :class:`InvalidDateError` for malformed or impossible dates such as
    ``2026-02-30`` or ``not-a-date``.
    """
    if not isinstance(value, str) or not _DATE_RE.match(value):
        raise InvalidDateError(value)
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise InvalidDateError(value) from None


def is_valid_date(value):
    """Return ``True`` when *value* is a valid ``YYYY-MM-DD`` string."""
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return False
    try:
        datetime.datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def add_days(value, days):
    """Return ``value + days`` as a ``YYYY-MM-DD`` string.

    Raises :class:`ScheduleError` (exit ``2``) when the result falls outside
    the calendar supported by :mod:`datetime`.
    """
    try:
        return (parse_date(value) + datetime.timedelta(days=days)).isoformat()
    except OverflowError:
        raise ScheduleError(
            "date out of range: {} + {} days".format(value, days)
        ) from None
