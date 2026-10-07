**About the Project**

**Why I built it**

As a student, I receive a large number of emails, calendar events, announcements, and requests every day. The difficult part is not receiving this information — it is remembering what actually requires action, when it is due, and how urgent it is.
I built Kept to solve this problem for my own daily workflow. Instead of expecting me to constantly check my inbox and calendar, Kept acts as a lightweight personal assistant that surfaces commitments when they actually need my attention.
What I built
Kept connects to Gmail and Google Calendar and looks for actionable commitments, deadlines, and important tasks. It then determines how close each deadline is and assigns an urgency level.
For example, an email saying:
“The group list must reach my email within one hour.”

is transformed into a clear notification:
🚨 KEPT - URGENT

Action: Send the group list
Deadline: Within 1 hour
Priority: Critical
Reason: Deadline is approaching

The notification is sent to my phone through Telegram, so I don't have to continuously monitor my inbox.
How I built it
I built Kept using Python, with:
- Gmail API to retrieve emails
- Google Calendar API to access upcoming events
- Rule-based deadline and commitment extraction to identify actionable information
- T-minus logic to determine urgency as deadlines approach
- Telegram Bot API to deliver notifications to my phone
- Google OAuth 2.0 to securely access my own Gmail and Calendar
- pytest for basic testing
The overall workflow is:
Gmail + Calendar
       ↓
Retrieve information
       ↓
Identify commitments & deadlines
       ↓
Determine urgency
       ↓
T-minus reminder logic
       ↓
Telegram notification
       ↓
Action taken

**The idea behind Kept is simple**
I don't need another place that shows me all my information. I need something that tells me what I need to do, by when, and when I should care about it.
