# Gemini Tutor Chat App

This is a Streamlit-based chat application that leverages Google's Gemini Flash AI model. It's designed with a default "strict, traditional tutor" persona to assist 5th graders in their academic pursuits. The application allows for text-based chat, file uploads (multimodal input), and configuration of AI model parameters.

## Features

*   **Interactive AI Chat**: Engage in conversations with the Gemini Flash AI.
*   **Default Tutor Persona**: The AI defaults to a "strict, traditional tutor" mode, with detailed system instructions to guide its behavior (see `app.py` for the full default prompt).
*   **Multimodal Inputs**: Upload various file types (images, videos, audio, documents, code) to supplement your chat messages.
*   **Configurable Settings**:
    *   Adjust AI model parameters: Temperature and Top P.
    *   Set your Google Generative AI API Key.
    *   Customize the System Instruction for the AI (Note: Custom system instruction from settings is active when settings are unlocked. After saving, the app defaults to the system instruction in `app.py` unless `locked_access` remains true).
*   **Secure Settings Page**: API Key and System Instruction fields are password-protected.
*   **Chat History**: View past messages in the current session.
*   **Clear Chat History**: Option to clear the current session's chat history.

## Project Structure

```
tutor/
├── app.py                   # Main Streamlit application
├── pages/
│   └── settings.py          # Settings page for API key and model parameters
├── .env                     # For environment variables (create this file)
└── README.md                # This file
```

## Prerequisites

*   Python 3.7+
*   pip (Python package installer)
*   A Google Generative AI API Key. You can get one from Google AI Studio.

## Setup and Installation

1.  **Clone the repository (if applicable) or ensure you have the project files.**
    If this project is in a Git repository, clone it:
    ```bash
    git clone <repository-url>
    cd tutor
    ```
    Otherwise, navigate to the project directory `tutor/`.

2.  **Install dependencies:**
    ```bash
    pip install streamlit google-generativeai python-dotenv
    ```

3.  **Create a `.env` file:**
    In the root directory of the project (`tutor/`), create a file named `.env` and add your Google API Key and a password for the settings page:
    ```env
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    STREAMLIT_PASSWORD="YOUR_CHOSEN_PASSWORD"
    ```
    Replace `"YOUR_GOOGLE_API_KEY"` with your actual API key and `"YOUR_CHOSEN_PASSWORD"` with a password you'll use to unlock the settings.

## Running the Application

1.  Open your terminal and navigate to the project directory:
    ```bash
    cd tutor/
    ```

2.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```

3.  The application will open in your web browser.

## Usage

1.  **Settings Configuration**:
    *   Upon first launch, or if the API key is not set, you might see a warning.
    *   Navigate to the "Settings" page from the sidebar.
    *   Enter the password you set in the `.env` file (`STREAMLIT_PASSWORD`) to unlock the API Key and System Instruction fields.
    *   Your `GOOGLE_API_KEY` from the `.env` file should be pre-filled if `STREAMLIT_PASSWORD` was correct. You can modify it if needed.
    *   Adjust the `Temperature` and `Top P` sliders as desired.
    *   You can modify the `System Instruction` here.
        *   **Important Note on System Instruction**: The system instruction configured on the Settings page is used by the AI model if the `locked_access` state is `True` (i.e., after entering the password but *before* clicking "Save"). After clicking "Save", `locked_access` becomes `False`, and the chat model in `app.py` will use the `default_system_instruction` hardcoded in `app.py`.
    *   Click "Save" to apply changes. This will also re-lock the sensitive settings.

2.  **Chatting with the AI**:
    *   Go to the main chat page (usually the default page when the app starts).
    *   Type your message in the input box at the bottom and press Enter.
    *   You can also upload files using the "Upload a file" widget. The file will be sent along with your next text prompt.

3.  **Clearing Chat History**:
    *   On the "Settings" page, click the "Clear Chat History" button to remove all messages from the current session.

## How System Instruction Works

The application has two main system instructions:

1.  **`default_system_instruction`**: Defined in `app.py`. This is the primary instruction set used by the AI, detailing the "strict, traditional tutor" persona. This instruction is used when `locked_access` (a session state variable) is `False`.
2.  **Custom System Instruction**: Can be set on the "Settings" page. This instruction is stored in `st.session_state.system_instruction`.

The chat model (`app.py`) decides which system instruction to use based on the `locked_access` state:
```python
# From app.py
chat_config = types.GenerateContentConfig(
    # ...
    system_instruction=st.session_state.system_instruction if st.session_state.locked_access else default_system_instruction,
)
```
When you save settings on the `settings.py` page, `st.session_state.locked_access` is set to `False`. Therefore, after saving, the `default_system_instruction` from `app.py` will be used for subsequent chat interactions. The custom system instruction from the settings page is primarily active if you unlock the settings and then navigate to the chat page *without* saving (which also means other settings like API key might not be persisted from that edit session if changed).

## File Uploads

The application supports uploading a wide variety of file types, including:
*   **Images**: jpg, jpeg, png, webp
*   **Videos**: mp4, mpeg, mov, avi, wmv, flv, webm
*   **Audio**: mp3, wav, ogg, flac
*   **Documents**: pdf, txt, md
*   **Spreadsheets**: csv, tsv, xls, xlsx
*   **Word Documents**: doc, docx, rtf, dot, dotx
*   **Code**: c, cpp, py, java, php, sql, html

Uploaded files are sent to the Gemini model along with your text prompt for multimodal understanding.