# app.py
import streamlit as st
from google import genai # Correct import for the top-level genai object
from google.genai import types # Correct import for types
import os
import base64 # Although types.Part.from_bytes takes bytes directly, base64 encoding is often used for display/storage

# --- Session State Initialization ---
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.7 # Default from settings description
if 'top_p' not in st.session_state:
    st.session_state.top_p = 0.95 # Default from settings description
if 'system_instruction' not in st.session_state:
    st.session_state.system_instruction = ''
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'locked_access' not in st.session_state:
    st.session_state.locked_access = False # Default to locked
if 'uploaded_files_data' not in st.session_state:
    st.session_state.uploaded_files_data = []
if 'uploaded_files_names' not in st.session_state:
    st.session_state.uploaded_files_names = []
if 'uploaded_files_mime' not in st.session_state:
    st.session_state.uploaded_files_mime = []
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0 # Key to reset file uploader

# --- App Title ---
st.title("Chatty")

# --- Sidebar File Uploader ---
st.sidebar.header("Upload Files")

# Allowed MIME types based on prompt description
allowed_types = [
    "image/jpeg", "image/jpg", "image/png", "image/webp",
    "video/mp4", "video/mpeg", "video/quicktime", "video/avi", "video/x-ms-wmv", "video/x-flv", "video/webm",
    "audio/mp3", "audio/wav", "audio/ogg", "audio/flac",
    "application/pdf", "text/plain", "text/markdown",
    "text/csv", "text/tab-separated-values", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/rtf", "application/vnd.dot", "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
    "text/x-csrc", "text/x-c++src", "text/x-python", "text/x-java-source", "text/x-php", "text/x-sql", "text/html"
]

# Streamlit's file uploader uses extensions, so we provide a list of extensions
# We need to map extensions back to MIME types when creating Part objects
uploaded_files = st.sidebar.file_uploader(
    "Choose files...",
    type=[mime.split('/')[-1] for mime in allowed_types if '/' in mime] + [mime for mime in allowed_types if '/' not in mime], # Handle cases like 'txt', 'csv' etc. if needed, though standard types are usually fine
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.file_uploader_key}" # Use key to reset
)

# Process uploaded files if any
if uploaded_files:
    # Check if the list of uploaded files has changed
    # This prevents reprocessing if the user just interacts with other widgets
    current_uploaded_names = [f.name for f in uploaded_files]
    if current_uploaded_names != st.session_state.uploaded_files_names:
        st.session_state.uploaded_files_data = []
        st.session_state.uploaded_files_names = []
        st.session_state.uploaded_files_mime = []

        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.getvalue()
            st.session_state.uploaded_files_data.append(bytes_data)
            st.session_state.uploaded_files_names.append(uploaded_file.name)
            st.session_state.uploaded_files_mime.append(uploaded_file.type) # Streamlit provides the MIME type

# Display list of uploaded files in sidebar
if st.session_state.uploaded_files_names:
    st.sidebar.subheader("Uploaded Files:")
    for name in st.session_state.uploaded_files_names:
        st.sidebar.write(f"- {name}")

# --- API Key Check ---
if not st.session_state.api_key:
    st.warning("Please enter your Google API Key in the Settings page.")
    st.stop()

# --- Set Environment Variable for genai ---
# This is the correct way to provide the API key to the library in a Streamlit app
os.environ["GOOGLE_API_KEY"] = st.session_state.api_key

# --- Client Initialization ---
try:
    # Initialize the client using the API key from the environment variable
    client = genai.Client()
except Exception as e:
    st.error(f"Error initializing client: {e}")
    st.stop()


# --- Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Handle displaying parts if message is complex (e.g., includes files)
        if isinstance(message["content"], list):
            for part in message["content"]:
                if isinstance(part, types.Part):
                    if part.text:
                        st.markdown(part.text)
                    elif part.inline_data:
                        # Display image/video/audio based on mime type
                        mime_type = part.inline_data.mime_type
                        data = part.inline_data.data
                        if mime_type.startswith("image/"):
                            st.image(data, caption=f"Uploaded: {mime_type}")
                        elif mime_type.startswith("video/"):
                             st.video(data, format=mime_type, caption=f"Uploaded: {mime_type}")
                        elif mime_type.startswith("audio/"):
                             st.audio(data, format=mime_type, caption=f"Uploaded: {mime_type}")
                        else:
                             st.write(f"Uploaded file ({mime_type}): Cannot display inline.")
                else:
                     st.write(part) # Should be text if not a Part
        else:
            st.markdown(message["content"])


# --- Chat Input and Content Generation ---
if prompt := st.chat_input("Ask Gemini Flash..."):
    # Add user message to history
    # Prepare file parts for the current turn
    file_parts = []
    for data, name, mime_type in zip(st.session_state.uploaded_files_data, st.session_state.uploaded_files_names, st.session_state.uploaded_files_mime):
        try:
            file_parts.append(types.Part.from_bytes(data=data, mime_type=mime_type))
        except Exception as e:
            st.warning(f"Could not process file {name} ({mime_type}): {e}")
            # Optionally skip this file or handle differently

    # Combine text prompt and file parts for the current turn's content
    current_turn_content_parts = [types.Part.from_text(text=prompt)] + file_parts
    current_turn_content = types.Content(role="user", parts=current_turn_content_parts)

    # Append the user's full content (text + files) to the session history for display
    st.session_state.messages.append({"role": "user", "content": current_turn_content_parts})

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
        if st.session_state.uploaded_files_names:
             st.write("Including uploaded files:")
             for name, mime_type, data in zip(st.session_state.uploaded_files_names, st.session_state.uploaded_files_mime, st.session_state.uploaded_files_data):
                 if mime_type.startswith("image/"):
                     st.image(data, caption=f"Uploaded: {name}")
                 elif mime_type.startswith("video/"):
                     st.video(data, format=mime_type, caption=f"Uploaded: {name}")
                 elif mime_type.startswith("audio/"):
                     st.audio(data, format=mime_type, caption=f"Uploaded: {name}")
                 else:
                     st.write(f"Uploaded file ({name}, {mime_type})")


    # Clear uploaded files after they are sent with the prompt
    st.session_state.uploaded_files_data = []
    st.session_state.uploaded_files_names = []
    st.session_state.uploaded_files_mime = []
    st.session_state.file_uploader_key += 1 # Increment key to reset uploader
    st.rerun() # Rerun to clear the file uploader widget and process the prompt


# This block runs after the rerun triggered by chat_input
# Check if the last message was from the user and needs a model response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    # Get the full conversation history including the last user message
    # The history needs to be in the format expected by generate_content, which is a list of Content objects
    # We stored the content parts, so we need to reconstruct the Content objects for the history
    conversation_history_for_model = []
    for msg in st.session_state.messages:
        # Ensure content is a list of parts (as stored) and create a Content object
        if isinstance(msg["content"], list):
             conversation_history_for_model.append(types.Content(role=msg["role"], parts=msg["content"]))
        else:
             # Handle cases where content might not be a list of parts (e.g., older text-only messages)
             conversation_history_for_model.append(types.Content(role=msg["role"], parts=[types.Part.from_text(text=msg["content"])]))


    try:
        # Generate response using the full conversation history via the client
        response_stream = client.models.generate_content_stream(
            model='gemini-2.5-flash-preview-04-17', # Specify the model name here
            contents=conversation_history_for_model, # Pass the full history as a list of Content objects
            config=types.GenerateContentConfig( # Use 'config' argument for GenerateContentConfig
                temperature=st.session_state.temperature,
                top_p=st.session_state.top_p,
                system_instruction=st.session_state.system_instruction # Pass system instruction in config
            ),
        )

        # --- Start of Token Usage Logging Section (Moved to process first chunk) ---
        # Attempt to get the first chunk to extract usage metadata
        try:
            first_chunk = next(response_stream)
            if hasattr(first_chunk, 'usage_metadata') and first_chunk.usage_metadata:
                usage = first_chunk.usage_metadata
                st.sidebar.subheader("Token Usage:")
                st.sidebar.write(f"Prompt Tokens: {usage.prompt_token_count}")
                st.sidebar.write(f"Candidate Tokens: {usage.candidates_token_count}")
                st.sidebar.write(f"Total Tokens: {usage.total_token_count}")
                if usage.cached_content_token_count is not None:
                     st.sidebar.write(f"Cached Content Tokens: {usage.cached_content_token_count}")
                # Logging details might be too verbose for sidebar, print to console or log file
                # print(f"Prompt Token Details: {usage.prompt_tokens_details}")
                # print(f"Candidate Token Details: {usage.candidates_tokens_details}")
            # If the first chunk has text, start building the response with it
            full_response = first_chunk.text if hasattr(first_chunk, 'text') and first_chunk.text else ""

        except StopIteration:
            # Handle case where the stream is empty (e.g., blocked by safety filters)
            st.warning("The model returned an empty response.")
            full_response = ""
            # No usage metadata to display if stream is empty

        # --- End of Token Usage Logging Section ---


        # Display streaming response (starting from the first chunk's text if any, then remaining chunks)
        with st.chat_message("model"):
            message_placeholder = st.empty()
            message_placeholder.markdown(full_response + "▌") # Display initial text + typing cursor

            # Process remaining chunks
            for chunk in response_stream: # Continue iterating from the second chunk
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌") # Show typing cursor
            message_placeholder.markdown(full_response) # Final response without cursor


        # Add model response to history
        st.session_state.messages.append({"role": "model", "content": full_response})


    except Exception as e:
        st.error(f"An error occurred: {e}")
        # Remove the last user message if generation failed to avoid sending it again
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
             st.session_state.messages.pop()