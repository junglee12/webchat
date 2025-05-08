# app.py
import streamlit as st
from google import genai
# Import types for configuration objects AND Content/Part structure
from google.genai import types
import os
from dotenv import load_dotenv

# --- Configuration & Client Setup ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("🔴 Google API Key not found. Please set the GOOGLE_API_KEY environment variable.")
    st.stop()

try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"🔴 Failed to initialize the Google AI Client: {e}")
    st.stop()

MODEL_NAME = "gemini-2.5-flash-preview-04-17" # Using the requested thinking model

# --- Streamlit App ---
st.set_page_config(page_title="Gemini Chat", page_icon="💬")
st.title("💬 Simple Chat with Gemini")
st.caption(f"Using google.genai Client syntax with {MODEL_NAME}")

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "token_usage" not in st.session_state:
    st.session_state.token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "top_p" not in st.session_state:
    st.session_state.top_p = 0.95
if "thinking_budget" not in st.session_state:
    st.session_state.thinking_budget = None
if "use_grounding" not in st.session_state:
    st.session_state.use_grounding = False

# --- Display Chat History ---
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role):
        # Display main text content
        if message["parts"] and isinstance(message["parts"], list) and "text" in message["parts"][0]:
             st.markdown(message["parts"][0]["text"])
        else:
             st.markdown("*Could not display message content.*")
        # Display grounding metadata if it was stored with the message
        if message.get("grounding_html"):
            st.markdown("---")
            st.caption("ℹ️ Grounding Suggestion:")
            st.markdown(message["grounding_html"], unsafe_allow_html=True)


# --- Handle User Input ---
prompt = st.chat_input("Ask Gemini...")

if prompt:
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
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
            tools_list = []
            if st.session_state.use_grounding:
                tools_list.append(types.Tool(google_search=types.GoogleSearch()))
            if tools_list:
                 config_params["tools"] = tools_list
            final_config_obj = types.GenerateContentConfig(**config_params) if config_params else None

            # --- Call generate_content ---
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=st.session_state.messages, # Send history
                config=final_config_obj
            )

            # Extract text response
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

            # Display the main text response first
            message_placeholder.markdown(full_response)

            # --- !!! ADDED: Display Grounding Metadata !!! ---
            grounding_html_to_display = None
            if st.session_state.use_grounding: # Only check if grounding was requested
                try:
                    # Safely access the nested attribute for renderedContent
                    grounding_meta = getattr(response.candidates[0], 'grounding_metadata', None)
                    search_entry = getattr(grounding_meta, 'search_entry_point', None)
                    rendered_content = getattr(search_entry, 'rendered_content', None)

                    if rendered_content:
                        grounding_html_to_display = rendered_content # Store it temporarily
                        # Display it immediately below the main response
                        st.markdown("---")
                        st.caption("ℹ️ Grounding Suggestion:")
                        st.markdown(rendered_content, unsafe_allow_html=True)
                except IndexError:
                     # Handle cases where candidates list might be empty (e.g., blocked prompt)
                     pass
                except Exception as e:
                     # Log other potential errors during access
                     # print(f"Could not access grounding metadata: {e}")
                     pass
            # --- !!! END: Display Grounding Metadata !!! ---


            # Update Token Usage
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                st.session_state.token_usage["prompt_tokens"] += getattr(usage, 'prompt_token_count', 0)
                st.session_state.token_usage["completion_tokens"] += getattr(usage, 'candidates_token_count', 0)
                st.session_state.token_usage["total_tokens"] += getattr(usage, 'total_token_count', 0)

        # --- !!! MODIFIED: Add assistant response AND grounding to history !!! ---
        # Store both the text and the grounding HTML (if any) for redisplay
        assistant_message_data = {"role": "model", "parts": [{"text": full_response}]}
        if grounding_html_to_display:
            assistant_message_data["grounding_html"] = grounding_html_to_display
        st.session_state.messages.append(assistant_message_data)
        # --- !!! END MODIFICATION !!! ---


    except Exception as e:
        st.error(f"🔴 An error occurred during API call: {e}")
        error_message = f"Sorry, I encountered an error: {e}"
        with st.chat_message("assistant"):
             st.error(error_message)