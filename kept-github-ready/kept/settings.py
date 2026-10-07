import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    timezone: str = os.getenv("KEPT_TIMEZONE", "Asia/Kolkata")
    poll_minutes: int = int(os.getenv("KEPT_POLL_MINUTES", "10"))

    @property
    def tz(self):
        return ZoneInfo(self.timezone)
