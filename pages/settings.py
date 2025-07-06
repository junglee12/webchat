# pages/settings.py
import streamlit as st
import os
from dotenv import load_dotenv
from google import genai # Correct import for the top-level genai object

# Load environment variables from .env file
load_dotenv()
from utils import initialize_settings_session_state

# --- Session State Initialization (ensure consistency with app.py) ---
initialize_settings_session_state()


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
            # st.rerun() # Rerun will occur naturally due to session_state change & widget interaction
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

    st.subheader("Advanced Settings")
    enable_grounding_input = st.checkbox(
        "Enable Grounding with Google Search",
        value=st.session_state.get('enable_google_search_grounding', False),
        help="Allows the model to use Google Search to inform its responses. May improve relevance for recent topics or specific information."
    )

    # --- Save Button ---
    if st.button("Save Settings"):
        st.session_state.api_key = api_key_input
        st.session_state.temperature = temperature_input
        st.session_state.top_p = top_p_input
        st.session_state.system_instruction = system_instruction_input
        st.session_state.enable_google_search_grounding = enable_grounding_input
        st.session_state.locked_access = False # Lock settings after saving
        st.success("Settings saved!")
        # st.rerun() # Rerun will occur naturally due to button click and session_state changes

# --- Clear Chat History Button ---
st.subheader("Chat Management")
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.session_state.uploaded_files_data = []
    st.session_state.uploaded_files_names = []
    st.session_state.uploaded_files_mime = []
    st.session_state.file_uploader_key += 1 # Increment key to reset file uploader in app.py
    st.success("Chat history cleared!")
    # st.rerun() # Rerun will occur naturally due to button click and session_state changes