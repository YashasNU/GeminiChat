# AI Chat Assistant

This Streamlit application provides an AI chat assistant powered by Google's Gemini Flash model. It allows users to have conversations with the AI, view chat history, and save/load previous chat sessions.

## Features

*   **AI Chat:** Uses the `gemini-2.0-flash` model to generate responses.
*   **User-Friendly Interface:** Employs Streamlit components for a clean and intuitive chat experience.
*   **Chat History:** Displays messages with roles (user/assistant) and timestamps.
*   **Save/Load Chats:** Automatically saves chat sessions to JSON files and provides a sidebar interface to load previous conversations.

## Setup

1.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **API Key:**

    *   Obtain a Google Generative AI API key.
    *   Configure the API key within `app.py` by replacing `"YOUR_API_KEY"` with your actual key:
    *   Create your api key from the google's gemini platform.

        ```python
        genai.configure(api_key="YOUR_API_KEY")
        ```

## Usage

1.  **Run the Application:**

    ```bash
    streamlit run app.py
    ```

2.  **Chat:** Enter your messages in the chat input field and press "Send".

3.  **New Chat:** Click "Start New Chat" in the sidebar to begin a new conversation. The current chat will be automatically saved.

4.  **Load Previous Chats:** Select a chat from the "Previous Chats" list in the sidebar to load and view a past conversation.

## File Structure

*   `app.py`: The main Streamlit application file.
*   `requirements.txt`: Lists the required Python libraries.
*   `chat_histories/`: (Automatically created) Contains saved chat sessions as JSON files.

## Dependencies

*   streamlit
*   google-generativeai

## Notes

*   The Google Generative AI API key is configured directly within the `app.py` file for simplicity. In a production environment, it's recommended to use `st.secrets` or environment variables for secure API key management.
*   The application saves chat history as JSON files in the `chat_histories/` directory.
