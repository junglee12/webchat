import streamlit as st
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize session state
if "locked_access" not in st.session_state:
    st.session_state.locked_access = False

st.title("Settings")
st.markdown("Adjust the model parameters and API key here.")

# Locked fields (API key and system instruction)
if not st.session_state.locked_access:
    password = st.text_input("Enter Password to Unlock", type="password")
    if password == os.getenv("STREAMLIT_PASSWORD"):
        st.session_state.locked_access = True
        st.session_state.api_key = API_KEY  # Load from .env
        st.rerun()
    elif password:
        st.error("Incorrect password")
    api_key = st.text_input("Google API Key", value="****", disabled=True)
    system_instruction = st.text_area("System Instruction", value="****", disabled=True)
else:
    api_key = st.text_input(
        "Google API Key",
        value=st.session_state.get("api_key", API_KEY),
        type="password",
        help="Enter your Google Generative AI API Key. You can get one from https://makersuite.google.com/."
    )
    system_instruction = st.text_area(
        "System Instruction",
        value=st.session_state.get("system_instruction", ""),
        help="Instructions for the model to steer it toward better performance. E.g., 'Answer as concisely as possible'."
    )

# Unlocked settings
temperature = st.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state.get("temperature", 0.7),
    step=0.01,
    help="Controls the degree of randomness in token selection. Lower values are good for prompts that require a less open-ended or creative response, while higher values can lead to more diverse or creative results."
)

top_p = st.slider(
    "Top P",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state.get("top_p", 0.95),
    step=0.01,
    help="Tokens are selected from the most to least probable until the sum of their probabilities equals this value. Use a lower value for less random responses and a higher value for more random responses."
)

# Save button to store settings and re-lock
if st.button("Save"):
    st.session_state.api_key = api_key
    st.session_state.temperature = temperature
    st.session_state.top_p = top_p
    st.session_state.system_instruction = system_instruction
    st.session_state.locked_access = False
    st.success("Settings saved!")
    st.rerun()

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()