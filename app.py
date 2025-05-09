# app.py
import streamlit as st
from google import genai
# Import types for configuration objects AND Content/Part structure
from google.genai import types
import os
from dotenv import load_dotenv

# --- Configuration & Client Setup ---
load_dotenv()
st.session_state.setdefault("api_key", None)
API_KEY_TO_USE = st.session_state.api_key or os.getenv("GOOGLE_API_KEY")

if not API_KEY_TO_USE:
    st.error("🔴 Google API Key not found. Please set it on the Model Configuration page or as an environment variable (GOOGLE_API_KEY).")
    st.stop()

try:
    client = genai.Client(api_key=API_KEY_TO_USE)
except Exception as e:
    st.error(f"🔴 Failed to initialize the Google AI Client: {e}")
    st.stop()

MODEL_NAME = "gemini-2.5-flash-preview-04-17" # Using the requested thinking model

# --- Streamlit App ---
st.set_page_config(page_title="Gemini Chat", page_icon="💬")
st.title("💬 Simple Chat with Gemini")
st.caption(f"Using google.genai Client syntax with {MODEL_NAME}")

# --- !!! Define Default System Instruction !!! ---
DEFAULT_SYSTEM_INSTRUCTION = """You are a knowledgeable assistant. Answer user questions clearly and concisely, using a friendly and professional tone. If you need more information, ask clarifying questions. Limit your response to three paragraphs and cite your sources if available."""
# --- !!! END Define Default System Instruction !!! ---


# --- Session State Initialization ---
if "messages_for_display" not in st.session_state:
    st.session_state.messages_for_display = []
if "token_usage" not in st.session_state:
    st.session_state.token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
st.session_state.setdefault("temperature", 0.1)
st.session_state.setdefault("top_p", 0.2)
st.session_state.setdefault("thinking_budget", 0)
st.session_state.setdefault("use_grounding", False)
# --- !!! Use Defined Default for System Instruction !!! ---
st.session_state.setdefault("system_instruction", DEFAULT_SYSTEM_INSTRUCTION)
# --- !!! END Use Defined Default !!! ---


# --- Display Chat History ---
# (Display logic remains the same)
for message in st.session_state.messages_for_display:
    role = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role):
        if message["parts"] and isinstance(message["parts"], list) and "text" in message["parts"][0]:
             st.markdown(message["parts"][0]["text"])
        else:
             st.markdown("*Could not display message content.*")
        if message.get("grounding_html"):
            st.markdown("---")
            st.caption("ℹ️ Grounding Suggestion:")
            st.markdown(message["grounding_html"], unsafe_allow_html=True)
        if message.get("grounding_sources"):
            st.caption("🔗 Grounding Sources:")
            for i, source in enumerate(message["grounding_sources"]):
                st.markdown(f"{i+1}. [{source.get('title', 'N/A')}]({source.get('uri', '#')})")


# --- Handle User Input ---
prompt = st.chat_input("Ask Gemini...")

if prompt:
    # Append user message (correct format)
    st.session_state.messages_for_display.append({"role": "user", "parts": [{"text": prompt}]})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Prepare API Call ---
    try:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")

            # Prepare config
            config_params = {}
            if st.session_state.temperature is not None:
                config_params["temperature"] = st.session_state.temperature
            if st.session_state.top_p is not None:
                config_params["top_p"] = st.session_state.top_p
            if st.session_state.thinking_budget is not None:
                 config_params["thinking_config"] = types.ThinkingConfig(
                     thinking_budget=st.session_state.thinking_budget
                 )
            # --- !!! Use Updated Default for System Instruction !!! ---
            # Add system instruction to config_params if it's set (will use default if not changed)
            if st.session_state.system_instruction:
                 config_params["system_instruction"] = st.session_state.system_instruction
            # --- !!! END Use Updated Default !!! ---

            # Prepare tools list
            tools_list = []
            if st.session_state.use_grounding:
                tools_list.append(types.Tool(google_search=types.GoogleSearch()))
            if tools_list:
                 config_params["tools"] = tools_list
            final_config_obj = types.GenerateContentConfig(**config_params) if config_params else None

            # Prepare history for API call
            api_history = [
                {"role": msg["role"], "parts": msg["parts"]}
                for msg in st.session_state.messages_for_display
            ]

            # --- Call generate_content ---
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=api_history,
                config=final_config_obj
            )

            # (Rest of the response handling and token update code remains the same)
            full_response = ""
            try:
                 if response.candidates and response.candidates[0].content.parts:
                      full_response = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
                 else:
                      block_reason = None
                      prompt_feedback = getattr(response, 'prompt_feedback', None)
                      if prompt_feedback and getattr(prompt_feedback, 'block_reason', None):
                          block_reason = prompt_feedback.block_reason.name
                      elif response.candidates and getattr(response.candidates[0], 'finish_reason', None) and response.candidates[0].finish_reason.name != 'STOP':
                           block_reason = response.candidates[0].finish_reason.name
                      if block_reason:
                           full_response = f"*Response blocked due to: {block_reason}*"
                      else:
                           full_response = "*No text content received or response blocked.*"
            except Exception as text_extract_error:
                 st.error(f"Error extracting text from response: {text_extract_error}")
                 st.write("Raw Response:", response)
                 full_response = "*Error processing response.*"

            message_placeholder.markdown(full_response)

            # Extract and display grounding metadata
            grounding_html_to_display = None
            grounding_sources_to_store = []
            if st.session_state.use_grounding:
                try:
                    grounding_meta = getattr(response.candidates[0], 'grounding_metadata', None)
                    search_entry = getattr(grounding_meta, 'search_entry_point', None)
                    rendered_content = getattr(search_entry, 'rendered_content', None)
                    if rendered_content:
                        grounding_html_to_display = rendered_content
                        st.markdown("---")
                        st.caption("ℹ️ Grounding Suggestion:")
                        st.markdown(rendered_content, unsafe_allow_html=True)
                    grounding_chunks = getattr(grounding_meta, 'grounding_chunks', None)
                    if grounding_chunks:
                        st.caption("🔗 Grounding Sources:")
                        for i, chunk in enumerate(grounding_chunks):
                            web_info = getattr(chunk, 'web', None)
                            if web_info:
                                title = getattr(web_info, 'title', 'N/A')
                                uri = getattr(web_info, 'uri', '#')
                                grounding_sources_to_store.append({"title": title, "uri": uri})
                                st.markdown(f"{i+1}. [{title}]({uri})")
                except IndexError: pass
                except Exception as e: pass

            # Update Token Usage
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                st.session_state.token_usage["prompt_tokens"] += getattr(usage, 'prompt_token_count', 0)
                st.session_state.token_usage["completion_tokens"] += getattr(usage, 'candidates_token_count', 0)
                st.session_state.token_usage["total_tokens"] += getattr(usage, 'total_token_count', 0)

        # Add assistant response AND grounding info to the DISPLAY history
        assistant_message_data = {"role": "model", "parts": [{"text": full_response}]}
        if grounding_html_to_display:
            assistant_message_data["grounding_html"] = grounding_html_to_display
        if grounding_sources_to_store:
            assistant_message_data["grounding_sources"] = grounding_sources_to_store
        st.session_state.messages_for_display.append(assistant_message_data)


    except Exception as e:
        st.error(f"🔴 An error occurred during API call: {e}")
        error_message = f"Sorry, I encountered an error: {e}"
        with st.chat_message("assistant"):
             st.error(error_message)