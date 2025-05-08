# Gemini Chat Streamlit App

A multi-page Streamlit application that provides a user-friendly interface to chat with Google's Gemini AI models. It allows for real-time configuration of model parameters, API key management, system instruction setting, and tracks token usage for the current session.

## Features

*   **Interactive Chat Interface**: Engage in conversations with a Gemini model.
*   **Model Configuration Page**:
    *   Set and update your Google API Key directly within the app.
    *   Define a System Instruction to guide the model's behavior.
    *   Adjust `temperature` and `top_p` for controlling response randomness and nucleus sampling.
    *   Set a `thinking_budget` (token limit for internal model processing).
    *   Enable/disable `grounding` with Google Search to allow the model to use external information.
    *   Changes apply to subsequent messages within the current browser session.
*   **Token Usage Tracking Page**:
    *   View cumulative `prompt_tokens`, `completion_tokens`, and `total_tokens` used during the current chat session.
    *   Option to reset the token counter.
*   **Grounding Metadata Display**: If grounding is enabled, the app displays grounding suggestions and sources alongside the model's response.
*   **Dynamic API Key Handling**: Uses API key from the Model Configuration page if set, otherwise falls back to the `GOOGLE_API_KEY` environment variable.
*   **Error Handling**: Provides feedback for API key issues and other runtime errors.

## Project Structure

```
├── app.py                     # Main chat application, API interaction
├── pages/
│   ├── 1_Token_Usage.py       # Page to display token usage statistics
│   └── 2_Model_Configuration.py # Page for configuring model parameters and API key
├── .env                       # (Optional) For storing GOOGLE_API_KEY
└── requirements.txt           # (Recommended) For listing dependencies
```

*   **`app.py`**: The main entry point for the Streamlit application. It handles:
    *   Initializing the Google AI client.
    *   Managing and displaying the chat history.
    *   Sending user prompts to the Gemini API.
    *   Processing and displaying model responses, including grounding information.
    *   Applying configurations from `st.session_state`.
*   **`pages/1_Token_Usage.py`**: A separate page that displays the token usage metrics stored in `st.session_state`.
*   **`pages/2_Model_Configuration.py`**: A separate page allowing users to modify API key, system instructions, and generation parameters, which are then stored in `st.session_state` for `app.py` to use.

## Setup and Installation

1.  **Clone the repository (if applicable) or ensure you have the files.**

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    Create a `requirements.txt` file with the following content:
    ```txt
    streamlit
    google-generativeai
    python-dotenv
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Google API Key:**
    You have two options:
    *   **Environment Variable (Recommended for local development):**
        Create a `.env` file in the root directory of the project and add your API key:
        ```
        GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```
        The application will load this key automatically.
    *   **In-App Configuration:**
        Alternatively, you can leave the environment variable unset and enter your API key directly on the "⚙️ Model Configuration" page within the running application. This key will be stored in the session state for the current browser session.

## Running the Application

Navigate to the project's root directory in your terminal and run:

```bash
streamlit run app.py
```

This will start the Streamlit development server, and the application will open in your default web browser.

## Usage

*   **💬 Chat Page (Main Page)**:
    *   Type your messages in the input box at the bottom and press Enter.
    *   The conversation history will be displayed.
    *   If grounding is enabled and used by the model, grounding suggestions and sources will appear below the assistant's message.

*   **⚙️ Model Configuration Page**:
    *   Navigate to this page using the sidebar.
    *   **API Configuration**: Enter or update your Google API Key.
    *   **System Instruction**: Provide a system-level instruction for the model (e.g., "You are a helpful pirate assistant").
    *   **Generation Parameters**: Adjust sliders for `Temperature` and `Top-P`.
    *   **Reasoning & Grounding**:
        *   Toggle "Set Thinking Budget Explicitly" and set a token budget if needed.
        *   Check "Enable Grounding with Google Search" to allow the model to use Google Search.
    *   Changes made here are applied to subsequent messages in the chat. API Key and System Instruction changes might require a page refresh or the next message to be sent to take full effect.

*   **📊 Token Usage Page**:
    *   Navigate to this page using the sidebar.
    *   View the number of prompt, completion, and total tokens used in the current session.
    *   Click "Reset Usage Counter" to reset these statistics to zero.

## Key Configuration Options Explained

*   **API Key**: Your personal key to authenticate with the Google AI services.
*   **System Instruction**: A high-level instruction given to the model that influences its behavior, persona, or task throughout the conversation.
*   **Temperature**: Controls the randomness of the model's output. Lower values (e.g., 0.1) make the output more deterministic and focused. Higher values (e.g., 0.9) make it more random and creative.
*   **Top-P (Nucleus Sampling)**: An alternative to temperature for controlling randomness. It considers only the most probable tokens whose cumulative probability mass exceeds a certain threshold (p).
*   **Thinking Budget**: (For specific models like `gemini-1.5-flash-preview-0514`) An explicit budget in tokens that the model can use for internal "thinking" or "reasoning" processes before generating a response. Setting it to 0 typically disables explicit budget allocation, letting the model decide.
*   **Use Grounding**: Allows the model to use Google Search to find and incorporate up-to-date information or verify facts, potentially improving the accuracy and relevance of its responses.

---

*This README was generated based on the provided Python files.*