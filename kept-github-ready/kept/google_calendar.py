from datetime import datetime, timedelta

from googleapiclient.discovery import build

from kept.google_auth import get_credentials


def upcoming_events(days=7):
    service = build(
        "calendar",
        "v3",
        credentials=get_credentials(),
        cache_discovery=False,
    )

    now = datetime.now().astimezone()
    end = now + timedelta(days=days)

    response = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        maxResults=250,
    ).execute()

    return response.get("items", [])
