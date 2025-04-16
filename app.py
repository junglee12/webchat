# --- START OF FILE app.py ---

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# --- Configuration and Initialization ---

st.set_page_config(page_title="Gemini Chat App", layout="wide")

st.markdown("""
    <style>
        /* (Keep existing CSS rules here) */
        .block-container { padding-top: 2rem; padding-bottom: 1rem; padding-left: 1rem; padding-right: 1rem; }
        .stSidebar { background-color: #f8f9fa; }
        .stButton > button { width: 100%; }
        .stFileUploader > div > div { border: 1px solid #ddd; }
        .main { display: flex; flex-direction: column; }
        .chat-history-container {
            max-height: 70vh; overflow-y: auto;
            padding: 1rem; margin-bottom: 1rem;
        }
        .stChatMessage { word-wrap: break-word; overflow-wrap: break-word; }
        h1 { text-align: center; }
        .file-selection-label { font-weight: bold; margin-top: 0.5rem; margin-bottom: 0.2rem; }
        div[data-testid="stCheckbox"] { margin-bottom: -0.5rem; }
        div.stButton button[kind="secondary"] { }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
# (Keep existing initializations)
if "messages" not in st.session_state: st.session_state.messages = []
if "gemini_model" not in st.session_state: st.session_state.gemini_model = None
if "total_input_tokens" not in st.session_state: st.session_state.total_input_tokens = 0
if "total_output_tokens" not in st.session_state: st.session_state.total_output_tokens = 0
if "uploaded_file_objects" not in st.session_state: st.session_state.uploaded_file_objects = {}
# --- NEW: Flag to signal checkbox reset ---
if "reset_selections_on_next_run" not in st.session_state:
    st.session_state.reset_selections_on_next_run = False


# --- Helper Function to Update Stored Files ---
# (Keep existing helper function)
def update_uploaded_files():
    if "sidebar_file_uploader" in st.session_state:
        newly_uploaded = st.session_state.sidebar_file_uploader
        if newly_uploaded:
            for file_obj in newly_uploaded:
                if file_obj.file_id not in st.session_state.uploaded_file_objects:
                    st.session_state.uploaded_file_objects[file_obj.file_id] = file_obj

# --- Sidebar Setup ---
with st.sidebar:
    st.header("Configuration")
    # (Keep System Prompt and Model Selector)
    system_prompt = st.text_area("Enter System Prompt", value="You are a helpful AI assistant...", height=150)
    model_choice = st.selectbox("Select Model", ["gemini-2.0-flash-lite", "gemini-2.0-flash", " gemini-2.5-pro-preview-03-25", "imagen-3.0-generate-002"])
    st.markdown("---")

    # (Keep File Management Expander)
    with st.expander("📁 File Management", expanded=True):
        st.file_uploader("Upload New Files", accept_multiple_files=True, type=["txt", "pdf", "png", "jpg", "jpeg"], key="sidebar_file_uploader", on_change=update_uploaded_files)
        st.markdown("---")

        # --- MODIFIED: Check and perform reset BEFORE drawing checkboxes ---
        if st.session_state.reset_selections_on_next_run:
            # print("DEBUG: Resetting checkboxes now") # Optional debug print
            for key in list(st.session_state.keys()): # Iterate over a copy
                 if key.startswith("select_file_"):
                      st.session_state[key] = False # Reset state value
            st.session_state.reset_selections_on_next_run = False # Consume the flag
        # --- END Reset Check ---

        st.markdown("<div class='file-selection-label'>Select files for next message:</div>", unsafe_allow_html=True)
        if not st.session_state.uploaded_file_objects:
            st.caption("No files uploaded yet.")
        else:
            files_to_display = list(st.session_state.uploaded_file_objects.items())
            for file_id, file_object in files_to_display:
                checkbox_key = f"select_file_{file_id}"
                # Checkbox now reads the potentially reset state
                is_checked = st.session_state.get(checkbox_key, False)
                st.checkbox(f"{file_object.name} ({file_object.size // 1024} KB)", key=checkbox_key, value=is_checked)

            if st.button("Clear All Uploaded Files", key="clear_files_button"):
                 st.session_state.uploaded_file_objects = {}
                 # Also clear checkbox states when clearing all files
                 for key in list(st.session_state.keys()):
                      if key.startswith("select_file_"): del st.session_state[key]
                 st.session_state.reset_selections_on_next_run = False # Ensure reset flag is off
                 st.rerun()

    st.markdown("---")
    st.subheader("Token Usage (Session Total)")
    token_info_placeholder = st.empty()
    token_info_placeholder.markdown(f"Input Tokens: {st.session_state.total_input_tokens}\n\nOutput Tokens: {st.session_state.total_output_tokens}")
    st.markdown("---")

    # (Keep Clear Chat Button - its logic is fine)
    if st.button("🧹 Clear Chat History", key="clear_chat", type="secondary"):
        st.session_state.messages = []
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.session_state.uploaded_file_objects = {}
        for key in list(st.session_state.keys()):
             if key.startswith("select_file_"): del st.session_state[key]
        st.session_state.reset_selections_on_next_run = False # Ensure reset flag is off
        st.toast("Chat history cleared!", icon="🗑️")
        st.rerun()


# --- API Key Check and Configuration ---
# (Keep this section as is)
if not api_key: st.error("⚠️ GOOGLE_API_KEY not set."); st.stop()
else:
    try: genai.configure(api_key=api_key)
    except Exception as e: st.error(f"🚨 Error configuring Google AI: {e}"); st.stop()

# --- Main Chat Interface ---
# (Keep this section as is)
st.title("💬 Gemini Chat")
current_model_name = st.session_state.gemini_model.model_name if st.session_state.gemini_model else None
if current_model_name != model_choice:
     try: st.session_state.gemini_model = genai.GenerativeModel(model_choice, system_instruction=system_prompt)
     except Exception as e: st.error(f"🚨 Error initializing model '{model_choice}'. Details: {e}"); st.stop()

st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
chat_display_area = st.container()
with chat_display_area:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)


# --- Handle User Input and AI Response ---
# (Keep Input processing and API call logic as is)
if prompt := st.chat_input("Your message..."):

    # Determine selected files
    selected_file_ids = []
    for key, value in st.session_state.items():
         if key.startswith("select_file_") and value:
             file_id = key.split("select_file_")[1]
             if file_id in st.session_state.uploaded_file_objects:
                  selected_file_ids.append(file_id)

    # Prepare message content and API parts
    user_message_content = prompt; processed_files_info = []; current_parts = [{"text": prompt}]
    if selected_file_ids:
        for file_id in selected_file_ids:
            file_object = st.session_state.uploaded_file_objects[file_id]
            try:
                bytes_data = file_object.getvalue(); current_parts.append({"mime_type": file_object.type, "data": bytes_data})
                processed_files_info.append(f"`{file_object.name}`")
            except Exception as e: st.error(f"Error reading file {file_object.name}: {e}")
    if processed_files_info: user_message_content += "\n*Attached: " + ", ".join(processed_files_info) + "*"
    st.session_state.messages.append({"role": "user", "content": user_message_content})
    with chat_display_area:
        with st.chat_message("user"): st.markdown(user_message_content)

    # Format history
    api_history = [];
    for msg in st.session_state.messages[:-1]: api_history.append({"role": "user" if msg["role"] == "user" else "model", "parts": [{"text": msg["content"]}]})
    api_history.append({"role": "user", "parts": current_parts})

    # Generate response & handle tokens/display
    try:
        model = st.session_state.gemini_model
        response_stream = model.generate_content(api_history, stream=True)
        # (Streaming display logic...)
        with chat_display_area:
            with st.chat_message("assistant"):
                response_placeholder = st.empty(); full_response_text = ""
                current_input_tokens = 0; current_output_tokens = 0
                for chunk in response_stream:
                    if hasattr(chunk, 'text'): full_response_text += chunk.text; response_placeholder.markdown(full_response_text + "▌")
                    elif chunk.prompt_feedback: st.warning(f"Content blocked: {chunk.prompt_feedback}")
                    if hasattr(chunk, 'usage_metadata'): current_input_tokens = chunk.usage_metadata.prompt_token_count; current_output_tokens = chunk.usage_metadata.candidates_token_count
                response_placeholder.markdown(full_response_text)
        st.session_state.messages.append({"role": "assistant", "content": full_response_text})
        # (Token update logic...)
        if current_input_tokens == 0 and current_output_tokens == 0:
             try:
                 final_response_metadata = response_stream._result
                 if hasattr(final_response_metadata, 'usage_metadata'): current_input_tokens = final_response_metadata.usage_metadata.prompt_token_count; current_output_tokens = final_response_metadata.usage_metadata.candidates_token_count
             except Exception: pass
        if current_input_tokens > 0 or current_output_tokens > 0:
            st.session_state.total_input_tokens += current_input_tokens; st.session_state.total_output_tokens += current_output_tokens
            token_info_placeholder.markdown(f"Input Tokens: {st.session_state.total_input_tokens}\n\nOutput Tokens: {st.session_state.total_output_tokens}")

    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")
        st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
        # Don't set reset flag on error
        st.rerun()
    # --- MODIFIED: Set flag instead of direct reset ---
    else: # Reset checkboxes on success using the flag mechanism
        # print("DEBUG: Setting reset flag") # Optional debug print
        st.session_state.reset_selections_on_next_run = True # Signal reset needed
        st.rerun() # Trigger the next run where the reset will happen
    # --- END MODIFICATION ---

# --- End of File app.py ---