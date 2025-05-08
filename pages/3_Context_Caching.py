# pages/3_Context_Caching.py
import streamlit as st
from google import genai
from google.genai import types
import os
import time
from dotenv import load_dotenv
import pandas as pd # Import pandas for better table display
from datetime import datetime # To display timestamps nicely

st.set_page_config(page_title="Context Caching", page_icon="💾")
st.title("💾 Context Caching for Large Files")
st.caption("Upload a large file (>20MB), cache it, and query against it.")

# --- Configuration & Client Setup ---
load_dotenv()
API_KEY_TO_USE = st.session_state.get("api_key") or os.getenv("GOOGLE_API_KEY")

if not API_KEY_TO_USE:
    st.error("🔴 Google API Key not found. Please set it on the Model Configuration page or as an environment variable (GOOGLE_API_KEY).")
    st.stop()

try:
    client = genai.Client(api_key=API_KEY_TO_USE)
except Exception as e:
    st.error(f"🔴 Failed to initialize the Google AI Client: {e}")
    st.stop()

MODEL_FOR_CACHING = "gemini-2.5-flash-preview-04-17"

st.info(f"Using model: `{MODEL_FOR_CACHING}` for caching operations.")

# --- Session State Initialization ---
st.session_state.setdefault("uploaded_file_ref", None)
st.session_state.setdefault("cached_content_name", None)
st.session_state.setdefault("file_processing_status", "Not started")
st.session_state.setdefault("listed_caches", None) # To store the list of caches

# --- File Upload ---
st.subheader("1. Upload Large Media File")
uploaded_file = st.file_uploader(
    "Choose a file (PDF, Image, Audio, Video, Text - >20MB recommended)",
    type=["pdf", "jpg", "jpeg", "png", "mp3", "wav", "mp4", "mov", "txt", "py", "js", "html", "css"],
    key="cache_file_uploader"
)

# --- Cache Creation ---
st.subheader("2. Create Context Cache")
cache_ttl_options = {
    "5 Minutes": "300s", "1 Hour": "1h", "6 Hours": "6h",
    "12 Hours": "12h", "1 Day": "1d",
}
selected_ttl_label = st.selectbox(
    "Cache Time-To-Live (TTL)", options=list(cache_ttl_options.keys()),
    index=1, key="cache_ttl_select"
)
cache_ttl_value = cache_ttl_options[selected_ttl_label]
system_instruction_cache = st.text_area(
    "Optional System Instruction for Cache:", height=100,
    key="cache_system_instruction",
    help="Instructions applied when the cache is created."
)

if uploaded_file is not None:
    if st.button("Create Cache from Uploaded File", key="create_cache_button"):
        st.session_state.cached_content_name = None
        st.session_state.uploaded_file_ref = None
        st.session_state.file_processing_status = "Uploading..."
        with st.spinner(f"Uploading `{uploaded_file.name}`..."):
            try:
                google_file = client.files.upload(file=uploaded_file, mime_type=uploaded_file.type)
                st.session_state.uploaded_file_ref = google_file
                st.success(f"File `{uploaded_file.name}` uploaded! (Name: {google_file.name})")
                st.session_state.file_processing_status = "Processing..."
            except Exception as e:
                st.error(f"🔴 File Upload Failed: {e}")
                st.session_state.file_processing_status = f"Upload Error: {e}"
                st.stop()

        if st.session_state.uploaded_file_ref:
            with st.spinner(f"Processing file `{st.session_state.uploaded_file_ref.name}`..."):
                file_ref = st.session_state.uploaded_file_ref
                polling_interval_seconds = 10
                max_wait_seconds = 600
                start_time = time.time()
                while file_ref.state.name == "PROCESSING" and (time.time() - start_time) < max_wait_seconds :
                    time.sleep(polling_interval_seconds)
                    file_ref = client.files.get(name=file_ref.name)
                if file_ref.state.name == "ACTIVE":
                    st.success(f"File `{file_ref.name}` processed!")
                    st.session_state.file_processing_status = "Processed (Active)"
                    with st.spinner(f"Creating context cache (TTL: {selected_ttl_label})..."):
                        try:
                            create_cache_config = {"contents": [file_ref], "ttl": cache_ttl_value}
                            if system_instruction_cache:
                                create_cache_config["system_instruction"] = system_instruction_cache
                            cache = client.caches.create(
                                model=MODEL_FOR_CACHING,
                                config=types.CreateCachedContentConfig(**create_cache_config)
                            )
                            st.session_state.cached_content_name = cache.name
                            st.success(f"Context Cache created! Name: `{cache.name}`")
                            st.session_state.listed_caches = None # Clear list cache after creating new one
                        except Exception as e:
                            st.error(f"🔴 Cache Creation Failed: {e}")
                            st.session_state.cached_content_name = None
                elif file_ref.state.name == "FAILED":
                     st.error(f"🔴 File Processing Failed for `{file_ref.name}`.")
                     st.session_state.file_processing_status = "Processing Failed"
                else: # Timeout
                     st.warning(f"File processing timed out for `{file_ref.name}`. State: {file_ref.state.name}")
                     st.session_state.file_processing_status = f"Processing Timeout ({file_ref.state.name})"
else:
    st.info("Upload a file above to enable cache creation.")

# --- Query Using Cache ---
st.subheader("3. Query Using the Cache")
if st.session_state.cached_content_name:
    st.success(f"Active Cache for Querying: `{st.session_state.cached_content_name}`")
    prompt_cache = st.text_input("Enter prompt to query the cached content:", key="cache_prompt")
    if st.button("Generate Response using Cache", key="generate_cache_button"):
        if not prompt_cache:
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Generating response using cached content..."):
                try:
                    gen_config_params = {}
                    if st.session_state.get("temperature") is not None:
                        gen_config_params["temperature"] = st.session_state.temperature
                    if st.session_state.get("top_p") is not None:
                        gen_config_params["top_p"] = st.session_state.top_p
                    gen_config_params["cached_content"] = st.session_state.cached_content_name
                    generation_config_obj = types.GenerateContentConfig(**gen_config_params)
                    response = client.models.generate_content(
                        model=MODEL_FOR_CACHING,
                        contents=[prompt_cache],
                        config=generation_config_obj
                    )
                    st.markdown("**Response:**")
                    full_response = ""
                    if response.candidates and response.candidates[0].content.parts:
                         full_response = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
                    else: # Handle blocked/empty
                         block_reason = None
                         prompt_feedback = getattr(response, 'prompt_feedback', None)
                         if prompt_feedback and getattr(prompt_feedback, 'block_reason', None): block_reason = prompt_feedback.block_reason.name
                         elif response.candidates and getattr(response.candidates[0], 'finish_reason', None) and response.candidates[0].finish_reason.name != 'STOP': block_reason = response.candidates[0].finish_reason.name
                         if block_reason: full_response = f"*Response blocked: {block_reason}*"
                         else: full_response = "*No text content received.*"
                    st.markdown(full_response)
                    if hasattr(response, 'usage_metadata'):
                        st.divider()
                        st.caption("Token Usage for this Query:")
                        usage = response.usage_metadata
                        st.json({
                            "prompt_token_count": getattr(usage, 'prompt_token_count', 'N/A'),
                            "cached_content_token_count": getattr(usage, 'cached_content_token_count', 'N/A'),
                            "completion_token_count": getattr(usage, 'candidates_token_count', 'N/A'),
                            "total_token_count": getattr(usage, 'total_token_count', 'N/A'),
                        })
                except Exception as e:
                    st.error(f"🔴 Failed to generate response using cache: {e}")
else:
    st.info("Create a cache first to enable querying.")


# --- !!! ADDED: Manage Caches Section !!! ---
st.divider()
st.subheader("4. Manage Existing Caches")

# Button to trigger listing caches
if st.button("List Existing Caches", key="list_caches_button"):
    with st.spinner("Fetching cache list..."):
        try:
            st.session_state.listed_caches = list(client.caches.list()) # Convert iterator to list
        except Exception as e:
            st.error(f"🔴 Failed to list caches: {e}")
            st.session_state.listed_caches = [] # Set empty list on error

# Display the list if it exists in session state
if st.session_state.listed_caches is not None:
    if not st.session_state.listed_caches:
        st.info("No caches found for this API key.")
    else:
        st.write("Found Caches:")
        # Prepare data for display (e.g., in a table)
        cache_data = []
        cache_names = ["-- Select Cache to Delete --"] # For selectbox
        for cache in st.session_state.listed_caches:
             cache_names.append(cache.name)
             # Format timestamps nicely if they exist
             create_time_str = cache.create_time.strftime('%Y-%m-%d %H:%M:%S %Z') if isinstance(cache.create_time, datetime) else str(cache.create_time)
             expire_time_str = cache.expire_time.strftime('%Y-%m-%d %H:%M:%S %Z') if isinstance(cache.expire_time, datetime) else str(cache.expire_time)
             cache_data.append({
                 "Name": cache.name,
                 "Display Name": cache.display_name,
                 "Model": cache.model,
                 "Create Time": create_time_str,
                 "Expire Time": expire_time_str,
                 "TTL": str(cache.ttl),
             })
        st.dataframe(pd.DataFrame(cache_data), use_container_width=True)

        # --- Deletion UI ---
        st.write("---")
        selected_cache_name = st.selectbox(
            "Select Cache to Delete:",
            options=cache_names,
            key="delete_cache_select"
        )

        if selected_cache_name != "-- Select Cache to Delete --":
            if st.button(f"Delete Cache `{selected_cache_name}`", key="delete_cache_button", type="primary"):
                with st.spinner(f"Deleting cache `{selected_cache_name}`..."):
                    try:
                        client.caches.delete(name=selected_cache_name)
                        st.success(f"Cache `{selected_cache_name}` deleted successfully!")
                        # Clear the stored list and selection to force refresh on next list click
                        st.session_state.listed_caches = None
                        st.session_state.delete_cache_select = "-- Select Cache to Delete --"
                        # Rerun to update the UI immediately
                        st.rerun()
                    except Exception as e:
                        st.error(f"🔴 Failed to delete cache `{selected_cache_name}`: {e}")

# --- !!! END: Manage Caches Section !!! ---