# Chatty - A Gemini Flash Powered Chat Application

Chatty is a Streamlit web application that provides an interactive chat interface with Google's Gemini Flash model. It supports text-based conversations, file uploads (images, videos, audio, documents, code), and configurable model parameters.

## Features

*   **Interactive Chat:** Engage in conversations with the Gemini Flash model.
*   **File Uploads:** Upload various file types (images, videos, audio, PDFs, text, code, etc.) to provide context for your prompts.
*   **Streaming Responses:** Get real-time, streaming responses from the model.
*   **Configurable Settings (Password Protected):**
    *   Set your Google API Key.
    *   Define a System Instruction to guide the model's behavior.
    *   Adjust model parameters: Temperature and Top P.
*   **Chat History:** View the history of your conversation.
*   **Clear Chat History:** Option to clear the current conversation and uploaded files.
*   **Token Usage Display:** See the token count (prompt, candidate, total, cached) for each model interaction in the sidebar.

## Project Structure

your-project-directory/
├── app.py                   # Main Streamlit application for the chat interface.
├── pages/
│   └── settings.py          # Streamlit page for application settings.
├── utils.py                 # Common utility functions, like session state initialization.
├── requirements.txt         # Python dependencies for the project.
├── .env                     # Optional: For local environment variables (e.g., API keys, passwords). Not version controlled.
└── readme.md                # This file, providing information about the project.

## Setup and Installation

### Prerequisites

*   Python 3.8 or higher
*   pip (Python package installer)

### 1. Clone the Repository (Optional)

If you have this project in a Git repository, clone it:
```bash
git clone <your-repository-url>
cd tutor1
```
If you just have the files, navigate to the directory containing `app.py`.

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Create a `requirements.txt` file (see content below) in your project's root directory. Then install the dependencies:

```bash
pip install -r requirements.txt
```

**Content for `requirements.txt`:**
```
streamlit
google-generativeai
python-dotenv
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```env
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
STREAMLIT_PASSWORD="YOUR_CHOSEN_PASSWORD_FOR_SETTINGS"
```

*   Replace `"YOUR_GOOGLE_API_KEY"` with your actual Google API key for Gemini.
*   Replace `"YOUR_CHOSEN_PASSWORD_FOR_SETTINGS"` with a password you want to use to protect the settings page.

The application will load your `GOOGLE_API_KEY` from this file when you unlock the settings page for the first time.

## Running the Application

Once the setup is complete, you can run the Streamlit application from your project's root directory:

```bash
streamlit run app.py
```

This will start the application, and you can access it in your web browser, usually at `http://localhost:8501`.

## Usage

1.  **Access Settings:**
    *   Navigate to the "Settings" page from the sidebar.
    *   Enter the `STREAMLIT_PASSWORD` you set in your `.env` file to unlock the settings.
    *   If a `GOOGLE_API_KEY` is found in your `.env` file, it will be pre-filled. Otherwise, you can enter it manually.
    *   Configure the System Instruction, Temperature, and Top P as desired.
    *   Click "Save Settings". Settings will be locked again after saving.

2.  **Chat Interface (`Chatty` - Main Page):**
    *   Once the API key is set, you can start chatting with the model.
    *   Type your message in the input box at the bottom and press Enter.
    *   **File Uploads:** Use the "Upload Files" section in the sidebar to upload files. These files will be included with your next message to the model. Uploaded files are cleared after each message is sent.
    *   The chat history will be displayed on the main page.
    *   Token usage for the last interaction will appear in the sidebar.

3.  **Clear Chat History:**
    *   On the "Settings" page, you can click "Clear Chat History" to remove all messages and reset the file uploader.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.