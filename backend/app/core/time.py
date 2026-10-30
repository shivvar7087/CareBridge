from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return a UTC timestamp without tzinfo for the current naive SQL columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
