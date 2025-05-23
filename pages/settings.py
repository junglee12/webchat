# pages/settings.py
import streamlit as st
import os
from dotenv import load_dotenv
from google import genai # Correct import for the top-level genai object

# Load environment variables from .env file
load_dotenv()

# --- Session State Initialization (ensure consistency with app.py) ---
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.7
if 'top_p' not in st.session_state:
    st.session_state.top_p = 0.95
if 'system_instruction' not in st.session_state:
    st.session_state.system_instruction = ''
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'locked_access' not in st.session_state:
    st.session_state.locked_access = False
if 'uploaded_files_data' not in st.session_state:
    st.session_state.uploaded_files_data = []
if 'uploaded_files_names' not in st.session_state:
    st.session_state.uploaded_files_names = []
if 'uploaded_files_mime' not in st.session_state:
    st.session_state.uploaded_files_mime = []
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0


# --- Settings Title and Description ---
st.title("Settings")
st.write("Configure your Gemini Flash Chat App settings.")

# --- Access Control (Password) ---
STREAMLIT_PASSWORD = os.getenv("STREAMLIT_PASSWORD")

if not st.session_state.locked_access:
    st.write("Enter password to unlock settings.")
    password_input = st.text_input("Password", type="password")
    if password_input:
        if STREAMLIT_PASSWORD and password_input == STREAMLIT_PASSWORD:
            st.session_state.locked_access = True
            # Load API key from .env if available, otherwise keep current session state value
            if os.getenv("GOOGLE_API_KEY"):
                 st.session_state.api_key = os.getenv("GOOGLE_API_KEY")
            st.success("Settings unlocked!")
            st.rerun()
        else:
            st.error("Incorrect password.")

    # Display locked inputs
    st.text_input("Google API Key", value="****************", type="password", disabled=True)
    st.text_area("System Instruction", value="****", disabled=True)

else: # locked_access is True
    st.write("Settings unlocked.")
    # Editable API Key input
    api_key_input = st.text_input(
        "Google API Key",
        value=st.session_state.api_key,
        type="password",
        help="Enter your Google API Key here."
    )

    # Editable System Instruction input
    system_instruction_input = st.text_area(
        "System Instruction",
        value=st.session_state.system_instruction,
        help="Provide a system instruction to guide the model's behavior."
    )

    # --- Model Parameter Sliders ---
    st.subheader("Model Parameters")
    temperature_input = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.01,
        help="Controls the randomness of predictions. Lower values (closer to 0) make the model more deterministic, while higher values (closer to 1) make it more creative."
    )

    top_p_input = st.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.top_p,
        step=0.01,
        help="Controls the diversity of predictions. The model considers tokens whose probability sums up to the top_p value. Lower values restrict the model to more likely tokens."
    )

    # --- Save Button ---
    if st.button("Save Settings"):
        st.session_state.api_key = api_key_input
        st.session_state.temperature = temperature_input
        st.session_state.top_p = top_p_input
        st.session_state.system_instruction = system_instruction_input
        st.session_state.locked_access = False # Lock settings after saving
        st.success("Settings saved!")
        st.rerun()

# --- Clear Chat History Button ---
st.subheader("Chat Management")
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.session_state.uploaded_files_data = []
    st.session_state.uploaded_files_names = []
    st.session_state.uploaded_files_mime = []
    st.session_state.file_uploader_key += 1 # Increment key to reset file uploader in app.py
    st.success("Chat history cleared!")
    st.rerun()