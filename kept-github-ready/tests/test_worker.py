from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from kept.worker import deadline_from


def test_within_one_hour():
    tz = ZoneInfo("Asia/Kolkata")
    received = datetime(2026, 10, 7, 14, 0, tzinfo=tz)
    assert deadline_from("must be done within one hour", received) == (
        received + timedelta(hours=1)
    )


def test_tomorrow():
    tz = ZoneInfo("Asia/Kolkata")
    received = datetime(2026, 10, 7, 14, 0, tzinfo=tz)
    deadline = deadline_from("submit tomorrow", received)
    assert deadline.hour == 18
    assert deadline.day == 8
