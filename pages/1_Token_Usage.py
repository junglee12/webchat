# pages/1_Token_Usage.py
import streamlit as st
# No need for genai client here unless you add other API calls
# from google import genai
# import os
# from dotenv import load_dotenv

# --- Streamlit Page ---
st.set_page_config(page_title="Token Usage", page_icon="📊") # Updated title/icon
st.title("📊 Chat Session Token Usage")
st.caption("Tracks cumulative token usage for the current chat session.")

st.markdown("""
This page shows the total number of tokens used for prompts and responses
during your current chat session on the main 'App' page. The counts reset
if you refresh the browser tab or close it.
""")

# --- Display Token Usage ---

# Check if usage data exists in session state (it should be initialized in app.py)
if "token_usage" in st.session_state:
    usage_data = st.session_state.token_usage

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Prompt Tokens Used", value=f"{usage_data.get('prompt_tokens', 0)}")
    with col2:
        st.metric(label="Completion Tokens Used", value=f"{usage_data.get('completion_tokens', 0)}")
    with col3:
        st.metric(label="Total Tokens Used", value=f"{usage_data.get('total_tokens', 0)}")

else:
    st.warning("Token usage data not found. Please start a chat on the main 'App' page first.")

# --- Optional: Reset Button ---
if st.button("Reset Usage Counter", key="reset_usage_button"):
    if "token_usage" in st.session_state:
        st.session_state.token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        st.success("Token usage counter reset!")
        # Use st.rerun() to immediately update the displayed metrics after reset
        st.rerun()
    else:
        st.warning("Usage data not yet initialized.")