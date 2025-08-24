#### Objective
Implement a two-way synchronization between the user's SolOS journal and their personal Notion page.

#### User Story
As a app user, I want to connect my journal to my Notion page so that my entries are automatically backed up and accessible in my personal Notion workspace.

#### Technical Requirements
1.  **API Selection:** Use the official Notion API.
2.  **Authentication:** The system must use a secure method (like an internal integration token) to authenticate with the user's Notion workspace. The user should be able to grant or revoke access.
3.  **Permissions:** The integration will require permission to both **read** and **write** to a specific Notion database or page that the user provides.
4.  **Data Sync:** When a new journal entry is created in app, it should be automatically pushed to the designated Notion page. The system should also check for updates to the Notion page and sync them back to the app.
5.  **Secure Credentials:** Store the Notion API key and other credentials securely in your environment variables (`.env.ecosystem`).