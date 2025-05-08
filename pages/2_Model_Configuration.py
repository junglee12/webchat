# pages/2_Model_Configuration.py
import streamlit as st

st.set_page_config(page_title="Model Config", page_icon="⚙️")
st.title("⚙️ Model Configuration")
st.caption("Adjust Gemini model parameters, API Key, and System Instruction.")

st.markdown("""
Changes made here will be applied to subsequent messages sent in the main 'Chat' page **within this browser session**.
**API Key and System Instruction changes require the app page to be refreshed or the next message to be sent.**
""")

# --- !!! Define Default System Instruction !!! ---
DEFAULT_SYSTEM_INSTRUCTION = """You are a knowledgeable assistant. Answer user questions clearly and concisely, using a friendly and professional tone. If you need more information, ask clarifying questions. Limit your response to three paragraphs and cite your sources if available."""
# --- !!! END Define Default System Instruction !!! ---


# --- Initialize Session State (if not already done in app.py - defensive check) ---
st.session_state.setdefault("temperature", 0.1)
st.session_state.setdefault("top_p", 0.2)
st.session_state.setdefault("thinking_budget", 0)
st.session_state.setdefault("use_grounding", False)
st.session_state.setdefault("api_key", None)
# --- !!! Use Defined Default for System Instruction !!! ---
st.session_state.setdefault("system_instruction", DEFAULT_SYSTEM_INSTRUCTION)
# --- !!! END Use Defined Default !!! ---


# --- API Key Configuration ---
# (API Key input remains the same)
st.subheader("API Configuration")
def update_api_key():
    st.session_state.api_key = st.session_state.api_key_input
api_key_input = st.text_input(
    "Google API Key", type="password", key="api_key_input",
    value=st.session_state.api_key or "", on_change=update_api_key,
    help="Enter your Google API Key. Get one from Google AI Studio."
)
if st.session_state.api_key:
    st.success("API Key is set in session state.")
else:
    st.warning("API Key not set in session state. Will try environment variable.")


# --- System Instruction Input ---
st.subheader("System Instruction")
def update_system_instruction():
     st.session_state.system_instruction = st.session_state.system_instruction_input
# --- !!! Use Defined Default for System Instruction Value !!! ---
system_instruction_input = st.text_area(
    "System Instruction",
    key="system_instruction_input",
    value=st.session_state.system_instruction, # Reads the new default
    on_change=update_system_instruction,
    height=150,
    help="Provide instructions for the model's behavior throughout the conversation. Leave blank for default behavior."
)
# --- !!! END Use Defined Default !!! ---


# --- Generation Parameters ---
st.subheader("Generation Parameters")
# (Temperature and Top-P sliders remain the same, reading their defaults)
temp = st.slider(
    "Temperature", min_value=0.0, max_value=1.0,
    value=st.session_state.temperature, step=0.05, key="temperature_slider",
    help="Controls randomness. Lower values are more deterministic.",
    on_change=lambda: st.session_state.update(temperature=st.session_state.temperature_slider)
)
top_p = st.slider(
    "Top-P", min_value=0.0, max_value=1.0,
    value=st.session_state.top_p, step=0.05, key="top_p_slider",
    help="Controls nucleus sampling.",
     on_change=lambda: st.session_state.update(top_p=st.session_state.top_p_slider)
)

# --- Reasoning & Grounding ---
st.subheader("Reasoning & Grounding")
# (Thinking Budget and Grounding controls remain the same, reading their defaults)
enable_thinking_budget = st.toggle(
    "Set Thinking Budget Explicitly", value=(st.session_state.thinking_budget is not None),
    key="enable_thinking_budget_toggle", help="Enable to manually set the thinking token budget (0-24576)."
)
thinking_budget_value = None
if enable_thinking_budget:
    thinking_budget_value = st.number_input(
        "Thinking Budget (Tokens)", min_value=0, max_value=24576,
        value=st.session_state.thinking_budget if st.session_state.thinking_budget is not None else 0,
        step=64, key="thinking_budget_input", help="Max tokens for internal thinking process (0 disables).",
    )
st.session_state.thinking_budget = thinking_budget_value if enable_thinking_budget else None
use_grounding = st.checkbox(
    "Enable Grounding with Google Search", value=st.session_state.use_grounding,
    key="use_grounding_checkbox", help="Allows the model to use Google Search.",
    on_change=lambda: st.session_state.update(use_grounding=st.session_state.use_grounding_checkbox)
)

# --- Display Current Settings ---
st.divider()
st.write("Current Settings Applied on Next Message:")
api_key_status = "Set (Hidden)" if st.session_state.api_key else "Not Set (Using Environment Fallback)"
# --- !!! Display Updated Default System Instruction !!! ---
st.json({
    "api_key_status": api_key_status,
    "system_instruction": st.session_state.system_instruction if st.session_state.system_instruction else "None Set", # Show current value
    "temperature": st.session_state.temperature,
    "top_p": st.session_state.top_p,
    "thinking_budget": st.session_state.thinking_budget if st.session_state.thinking_budget is not None else "Model Default",
    "use_grounding": st.session_state.use_grounding
})
# --- !!! END Display Updated Default !!! ---