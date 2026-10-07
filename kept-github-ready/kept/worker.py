import base64
import os
import re
import ssl
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from dotenv import load_dotenv
from googleapiclient.discovery import build

from kept.google_auth import get_credentials
from kept.settings import Settings

load_dotenv()

settings = Settings()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
seen = set()


def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials are not configured.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = urllib.parse.urlencode(
        {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    ).encode()

    try:
        request = urllib.request.Request(url, data=data)
        context = ssl.create_default_context()
        urllib.request.urlopen(request, context=context, timeout=20)
        print("Telegram alert sent.")
        return True
    except Exception as exc:
        print(f"Telegram failed: {exc}")
        return False


def decode_body(payload):
    data = payload.get("body", {}).get("data")
    if data:
        return base64.urlsafe_b64decode(data).decode(
            "utf-8", errors="ignore"
        )

    for part in payload.get("parts", []):
        body = decode_body(part)
        if body:
            return body
    return ""


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def deadline_from(text, received):
    lower = text.lower()

    if "within one hour" in lower or "within the hour" in lower:
        return received + timedelta(hours=1)
    if "within two hours" in lower:
        return received + timedelta(hours=2)
    if "within 30 minutes" in lower:
        return received + timedelta(minutes=30)
    if "tomorrow" in lower:
        return (received + timedelta(days=1)).replace(
            hour=18, minute=0, second=0, microsecond=0
        )
    if "today" in lower:
        return received.replace(
            hour=18, minute=0, second=0, microsecond=0
        )
    return None


def action_from(text):
    lower = text.lower()

    if "group list" in lower:
        return "Send the group list"
    if "assignment" in lower:
        match = re.search(r"assignment\s*\d+", lower)
        return (
            f"Submit {match.group(0).title()}"
            if match else "Submit the assignment"
        )
    if "registration" in lower:
        return "Complete the registration"
    if "form" in lower:
        return "Complete the form"
    return "Complete the requested action"


def analyse(message, now):
    headers = {
        h["name"].lower(): h["value"]
        for h in message["payload"].get("headers", [])
    }

    try:
        received = parsedate_to_datetime(
            headers.get("date", "")
        ).astimezone(now.tzinfo)
    except Exception:
        received = now

    subject = headers.get("subject", "")
    body = decode_body(message["payload"])
    text = clean(f"{subject} {body}")

    if not any(
        word in text.lower()
        for word in (
            "must", "required", "deadline", "due", "submit",
            "complete", "send", "fill", "register",
            "within one hour", "within the hour",
            "within two hours", "within 30 minutes",
        )
    ):
        return None

    deadline = deadline_from(text, received)
    if not deadline:
        return None

    if deadline < now:
        level, priority, reason = (
            "⚠️ KEPT — OVERDUE",
            "Critical",
            "The deadline has already passed.",
        )
    elif deadline <= now + timedelta(hours=1):
        level, priority, reason = (
            "🚨 KEPT — URGENT",
            "Critical",
            "Deadline is within 1 hour.",
        )
    elif deadline <= now + timedelta(hours=2):
        level, priority, reason = (
            "⏰ KEPT — T-2H REMINDER",
            "High",
            "Deadline is within 2 hours.",
        )
    elif deadline <= now + timedelta(hours=24):
        level, priority, reason = (
            "🔔 KEPT — T-1 REMINDER",
            "High",
            "Deadline is within 24 hours.",
        )
    else:
        return None

    return {
        "id": message["id"],
        "level": level,
        "action": action_from(text),
        "deadline": deadline,
        "priority": priority,
        "reason": reason,
    }


def main():
    print("Kept decision-based worker started.")
    print(f"Polling Gmail every {settings.poll_minutes} minutes.")
    print("Press Ctrl + C to stop.\n")

    service = build(
        "gmail",
        "v1",
        credentials=get_credentials(),
        cache_discovery=False,
    )

    while True:
        now = datetime.now(settings.tz)
        print(f"[{now:%H:%M:%S}] Checking Gmail...")

        try:
            result = service.users().messages().list(
                userId="me",
                q="in:inbox newer_than:2d",
                maxResults=15,
            ).execute()

            alerts = 0

            for item in result.get("messages", []):
                if item["id"] in seen:
                    continue

                message = service.users().messages().get(
                    userId="me",
                    id=item["id"],
                    format="full",
                ).execute()

                alert = analyse(message, now)
                seen.add(item["id"])

                if not alert:
                    continue

                text = (
                    f"{alert['level']}\n\n"
                    f"Action: {alert['action']}\n"
                    f"Deadline: {alert['deadline']:%d %b %Y, %I:%M %p}\n"
                    f"Priority: {alert['priority']}\n"
                    f"Reason: {alert['reason']}"
                )

                print(text)
                if send_telegram(text):
                    alerts += 1

            print(f"[{now:%H:%M:%S}] {alerts} alert(s) sent.\n")

        except Exception as exc:
            print(f"Gmail check failed: {exc}\n")

        time.sleep(settings.poll_minutes * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKept worker stopped.")
