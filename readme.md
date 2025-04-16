# Gemini Chat App

A Streamlit-based web application for interacting with Google's Gemini AI models through a user-friendly chat interface.

## Features

- **Chat Interface**: Engage in conversations with AI through a simple and intuitive chat window.
- **Configurable System Prompts**: Customize the AI's behavior by setting system prompts to guide responses.
- **Model Selection**: Choose from various Gemini models like `gemini-2.0-flash-lite`, `gemini-2.0-flash`, and `gemini-2.5-pro-preview-03-25`.
- **File Upload Support**: Enhance your queries by uploading text files (txt, pdf) and images (png, jpg, jpeg) for multi-modal input.
- **Token Usage Tracking**: Monitor the number of input and output tokens used during your chat sessions.

## Installation

To set up the Gemini Chat App on your local machine, follow these steps:

1. **Clone the Repository** (if applicable) or download the source code.
2. **Install Dependencies**: Ensure you have Python installed, then run:
   ```
   pip install streamlit google-generativeai python-dotenv
   ```
3. **Set Up API Key**: You need a Google API key to access Gemini models. See the Configuration section for details.

## Configuration

1. **Environment Variables**: Create a `.env` file in the project directory with the following content:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
   Replace `your_api_key_here` with your actual Google API key.
2. **Sidebar Options**: Use the sidebar in the app to:
   - Enter a custom system prompt to guide the AI's responses.
   - Select the desired Gemini model for your chat session.
   - Upload files that can be included in your queries.

## Usage

1. **Run the Application**: Navigate to the project directory and start the Streamlit server with:
   ```
   streamlit run app.py
   ```
2. **Interact with the Chat**: Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`). Type your message in the chat input field at the bottom of the page.
3. **Upload Files**: Use the sidebar to upload files. Select the files you want to include in your next message by checking the corresponding boxes.
4. **Manage Chat History**: Clear the chat history using the "Clear Chat History" button in the sidebar if you want to start a new conversation.

## Troubleshooting

- **API Key Errors**: If you encounter an error related to the API key, ensure that it is correctly set in the `.env` file and that it has the necessary permissions to access Gemini models.
- **Model Initialization Failures**: Check if the selected model name is correct and supported. Try switching to a different model if the issue persists.
- **File Upload Issues**: Ensure the uploaded files are of supported types (txt, pdf, png, jpg, jpeg) and not corrupted.

## Contributing

Contributions to the Gemini Chat App are welcome! If you have suggestions for improvements or bug fixes, please submit a pull request or open an issue on the project repository (if applicable).

## License

The license for this project is not specified. Please contact the project owner for more information regarding usage and distribution rights.
