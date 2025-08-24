#### Objective

Integrate a third-party API to analyze daily journal entries and conversations for emotional tone, providing objective data to supplement mood logging.

#### User Story

As a SolOS user, I want my journal entries to be automatically analyzed for emotion so that I can gain a deeper, data-driven understanding of my feelings and identify hidden patterns.*

#### Technical Requirements

1.  **API Selection:** Use a public API for emotion detection and sentiment analysis.
2.  **Authentication:** The system must securely use an API key to authenticate with the service. This key should be stored in your environment variables (e.g., in `.env.ecosystem`) and never committed to the code.
3.  **Data Flow:** When a user saves a journal entry or a conversation snippet, send the text to the API.
4.  **Data to Capture:** The system should parse the API's response and save the following to the database:
      * Overall sentiment score (e.g., positive, negative, or neutral).
      * Specific emotion labels (e.g., joy, anger, sadness, fear).
      * Confidence scores for each emotion.
5.  **Error Handling:** The system should handle API-specific errors, such as rate limits or invalid API keys.