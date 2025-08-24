Objective
Build a two-way synchronization system between the SolOS calendar and the user's personal Google Calendar.

User Story
I want to connect my Google Calendar so that I can see my events in my project and have any events I create in my project show up in my Google Calendar. This will allow me to manage my schedule from a single place.

Technical Requirements
Authentication: The system must use OAuth 2.0 to securely connect to the user's Google Calendar account. The user should be able to grant or revoke access at any time.

Permissions (Scopes): The system will require the following permissions from the user:

Read access to their calendar events.

Write access to create, update, and delete events.

Two-Way Synchronization:

From Google Calendar to project: Events created or updated in the user's Google Calendar should automatically appear in the project destination calendar. This should happen in near real-time.

From project to Google Calendar: Events created or updated in the project app must automatically sync to the user's Google Calendar.

Data to Sync: The system should sync the following event data:

Event Title

Start and End Times

Location (if applicable)

Description

Reminders/Notifications

Error Handling: The system should handle common API errors, such as:

Loss of internet connection.

API rate limits.

User revoking access to their calendar.

Environment Variables: The system will need to store the Google API key and other credentials securely. The integration-helper should use environment variables (likely in your .env.ecosystem file) to store these secrets.