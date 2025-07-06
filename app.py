# app.py
import streamlit as st
from google import genai # Correct import for the top-level genai object
from google.genai import types # Correct import for types
import os
import base64 # Although types.Part.from_bytes takes bytes directly, base64 encoding is often used for display/storage
from utils import initialize_app_session_state

# --- Session State Initialization ---
initialize_app_session_state()

# --- Constants ---
MODEL_NAME = 'gemini-2.5-flash-preview-04-17'
ALLOWED_MIME_TYPES = [
    "image/jpeg", "image/jpg", "image/png", "image/webp",
    "video/mp4", "video/mpeg", "video/quicktime", "video/avi", "video/x-ms-wmv", "video/x-flv", "video/webm",
    "audio/mp3", "audio/wav", "audio/ogg", "audio/flac",
    "application/pdf", "text/plain", "text/markdown",
    "text/csv", "text/tab-separated-values", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/rtf", "application/vnd.dot", "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
    "text/x-csrc", "text/x-c++src", "text/x-python", "text/x-java-source", "text/x-php", "text/x-sql", "text/html"
]

# --- App Title ---
st.title("Chatty")

# --- Sidebar File Uploader ---
st.sidebar.header("Upload Files")

# Streamlit's file uploader uses extensions, so we provide a list of extensions
# We need to map extensions back to MIME types when creating Part objects
uploaded_files = st.sidebar.file_uploader(
    "Choose files...",
    type=[mime.split('/')[-1] for mime in ALLOWED_MIME_TYPES if '/' in mime] + [mime for mime in ALLOWED_MIME_TYPES if '/' not in mime], # Handle cases like 'txt', 'csv' etc. if needed, though standard types are usually fine
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.file_uploader_key}" # Use key to reset
)

def process_uploaded_files(uploaded_files_list):
    """
    Processes uploaded files, updating session state if new files are uploaded.
    """
    if not uploaded_files_list:
        return

    current_uploaded_names = [f.name for f in uploaded_files_list]
    # Check if the list of uploaded files has changed or if there are new files when previously none
    if current_uploaded_names != st.session_state.get('uploaded_files_names', []):
        st.session_state.uploaded_files_data = []
        st.session_state.uploaded_files_names = []
        st.session_state.uploaded_files_mime = []

        for uploaded_file in uploaded_files_list:
            bytes_data = uploaded_file.getvalue()
            st.session_state.uploaded_files_data.append(bytes_data)
            st.session_state.uploaded_files_names.append(uploaded_file.name)
            st.session_state.uploaded_files_mime.append(uploaded_file.type) # Streamlit provides the MIME type

# Process uploaded files
process_uploaded_files(uploaded_files)

# Display list of uploaded files in sidebar
if st.session_state.get('uploaded_files_names'):
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

def display_chat_message_content(content, is_inline_upload_display=False):
    """
    Displays chat message content, handling text, and inline data parts.
    'is_inline_upload_display' is True when displaying uploads with the user's prompt.
    """
    if isinstance(content, list): # List of parts
        for part in content:
            if isinstance(part, types.Part):
                if part.text:
                    st.markdown(part.text)
                elif part.inline_data:
                    mime_type = part.inline_data.mime_type
                    data = part.inline_data.data
                    caption_prefix = "Uploaded" if is_inline_upload_display else "File"
                    # For history display, we don't have original file names easily here.
                    # If we need specific names, the data structure for messages might need adjustment.
                    # For now, using mime_type as part of the caption.
                    caption = f"{caption_prefix}: {mime_type}"

                    if mime_type.startswith("image/"):
                        st.image(data, caption=caption)
                    elif mime_type.startswith("video/"):
                        st.video(data, format=mime_type) # Caption not directly supported by st.video
                        if caption: st.caption(caption) # Add caption below if needed
                    elif mime_type.startswith("audio/"):
                        st.audio(data, format=mime_type) # Caption not directly supported by st.audio
                        if caption: st.caption(caption) # Add caption below if needed
                    else:
                        st.write(f"Uploaded file ({mime_type}): Cannot display inline.")
            else: # Should be simple text if not a Part (e.g. old string content)
                st.markdown(str(part)) # Ensure it's a string
    else: # Simple text content
        st.markdown(str(content)) # Ensure it's a string


# --- Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        display_chat_message_content(message["content"])


# --- Chat Input and Content Generation ---
if prompt := st.chat_input("Ask Gemini Flash..."):
    # Add user message to history
    def prepare_file_parts_for_prompt():
        """
        Creates a list of google.generativeai.types.Part objects from files in session state.
        """
        file_parts = []
        if st.session_state.get('uploaded_files_data'): # Check if there's anything to process
            for data, name, mime_type in zip(st.session_state.uploaded_files_data,
                                             st.session_state.uploaded_files_names,
                                             st.session_state.uploaded_files_mime):
                try:
                    file_parts.append(types.Part.from_bytes(data=data, mime_type=mime_type))
                except Exception as e:
                    st.warning(f"Could not process file {name} ({mime_type}): {e}")
        return file_parts

    # Prepare file parts for the current turn
    file_parts = prepare_file_parts_for_prompt()

    # Combine text prompt and file parts for the current turn's content
    current_turn_content_parts = [types.Part.from_text(text=prompt)] + file_parts
    # current_turn_content = types.Content(role="user", parts=current_turn_content_parts) # This variable is not used

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
                     st.video(data, format=mime_type)
                     st.caption(f"Uploaded: {name}")
                 elif mime_type.startswith("audio/"):
                     st.audio(data, format=mime_type)
                     st.caption(f"Uploaded: {name}")
                 else:
                     st.write(f"Uploaded file ({name}, {mime_type})")


    # Clear uploaded files after they are sent with the prompt
    st.session_state.uploaded_files_data = []
    st.session_state.uploaded_files_names = []
    st.session_state.uploaded_files_mime = []
    st.session_state.file_uploader_key += 1 # Increment key to reset uploader
    # st.rerun() # Rerun to clear the file uploader widget and process the prompt
    # The script will naturally rerun due to chat_input interaction and session state changes.


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
        def get_model_response(client_instance, model_name_str, history, temp, tp, sys_instruction):
            """Generates content stream from the model."""
            return client_instance.models.generate_content_stream(
                model=model_name_str,
                contents=history,
                config=types.GenerateContentConfig(
                    temperature=temp,
                    top_p=tp,
                    system_instruction=sys_instruction
                ),
            )

        response_stream = get_model_response(
            client,
            MODEL_NAME,
            conversation_history_for_model,
            st.session_state.temperature,
            st.session_state.top_p,
            st.session_state.system_instruction
        )

        # --- Start of Token Usage Logging Section (Moved to process first chunk) ---
        # Attempt to get the first chunk to extract usage metadata
        def handle_token_usage_display(usage_metadata):
            """Displays token usage information in the sidebar."""
            if usage_metadata:
                st.sidebar.subheader("Token Usage:")
                st.sidebar.write(f"Prompt Tokens: {usage_metadata.prompt_token_count}")
                st.sidebar.write(f"Candidate Tokens: {usage_metadata.candidates_token_count}")
                st.sidebar.write(f"Total Tokens: {usage_metadata.total_token_count}")
                if usage_metadata.cached_content_token_count is not None:
                    st.sidebar.write(f"Cached Content Tokens: {usage_metadata.cached_content_token_count}")

        def stream_and_display_response(response_stream_iter):
            """
            Streams the response, displays it, and handles token usage.
            Returns the full response text.
            """
            full_response_text = ""
            first_chunk_processed = False
            message_placeholder = None

            with st.chat_message("model"):
                message_placeholder = st.empty()
                try:
                    for chunk in response_stream_iter:
                        if not first_chunk_processed:
                            if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
                                handle_token_usage_display(chunk.usage_metadata)
                            first_chunk_processed = True

                        if chunk.text:
                            full_response_text += chunk.text
                            message_placeholder.markdown(full_response_text + "▌")

                    if not first_chunk_processed: # Handle empty stream (e.g. safety filters)
                        st.warning("The model returned an empty response.")
                        # No usage metadata to display if stream is empty before first chunk

                    message_placeholder.markdown(full_response_text) # Final response

                except StopIteration: # Should be caught by the loop, but as a safeguard
                    if not first_chunk_processed:
                        st.warning("The model returned an empty response (StopIteration).")
                    if message_placeholder: # Ensure placeholder exists
                        message_placeholder.markdown(full_response_text) # Final response
                except Exception as e:
                    st.error(f"Error during response streaming: {e}")
                    if message_placeholder: # Ensure placeholder exists
                         message_placeholder.markdown(full_response_text + "\n\nError processing stream.")


            return full_response_text

        full_response = stream_and_display_response(response_stream)

        # Add model response to history
        st.session_state.messages.append({"role": "model", "content": full_response})


    except Exception as e:
        st.error(f"An error occurred: {e}")
        # Remove the last user message if generation failed to avoid sending it again
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
             st.session_state.messages.pop()