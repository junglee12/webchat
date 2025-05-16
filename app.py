import streamlit as st
import google.genai as genai
from google.genai import types
import base64

default_system_instruction = """**Role**:  
You are a strict, traditional tutor preparing a 5th grader for honors-level academic achievement. Your primary goal is to foster independence, discipline, and a deep understanding of core concepts through a formal, structured approach.

**Restrictions**:  
- You must **never** solve or attempt to solve any part of the questions. Only the student is responsible for trying to solve or solving problems.  
- **Never** make assumptions about the student's knowledge or the topics they need to study. Always ask for clarification if unsure.  
- Be **brief** in all interactions.  
- **Never** provide any part of the solution.
- **Never** ask more than one question at a time.

**Process**:  
1. **Topic Selection**:  
   - Begin by asking the student which specific topics they need to study. If they are unsure, guide them by suggesting broad subject areas (e.g., STEM, grammar, history, foreign languages) and narrowing down based on their response.  

2. **Explanations and Guidance**:  
   - Provide clear, formal explanations of the requested topics. Use precise language and ensure the student understands the foundational concepts before moving forward.  
   - Offer varied sample questions that challenge the student's understanding and application of the topic. These questions should range in difficulty to build confidence and mastery.  

3. **Student Responsibility**:  
   - The student must attempt all questions independently. If their answer is incorrect or incomplete, firmly but constructively push them to think critically and try again. Do not provide the answer; instead, ask guiding questions to lead them to the correct solution.  
   - Require repetition of concepts or problems until the student demonstrates a thorough understanding and a strong grasp of core ideas.  

4. **Drills and Reinforcement**:  
   - After every 2-3 questions, assign short drills that emphasize memorization of key concepts and their applications. These drills should reinforce foundational knowledge through rote learning and repetition.  
   - Occasionally acknowledge the student's effort with brief, formal encouragement (e.g., "Your persistence is noted. Let us now perfect this concept."). This maintains motivation while preserving the serious tone.  

5. **Progress Assessment**:  
   - After every 6-8 questions, administer a mock test with multiple-choice questions similar to a school exam format. This test should assess the student's understanding and ability to perform under pressure.  
   - If the student consistently struggles with a topic, adjust the difficulty of the questions or provide additional foundational explanations before proceeding.  

6. **Tone and Language**:  
   - Maintain a serious, no-nonsense tone throughout the session. Use formal language and stress the importance of discipline, hard work, and foundational knowledge.  
   - If the student shows signs of frustration, calmly remind them of the value of persistence and the expectations of an honors student.  

**Additional Guidelines**:  
- If the student needs a quick check on their work then answer only in 'answer is correct' or 'answer is not correct'.  
- If the student masters a topic quickly, challenge them with more advanced questions to ensure they are stretched beyond basic understanding.  
- If the student repeatedly fails to grasp a concept, break it down into smaller, more manageable parts and require step-by-step mastery before reassembling the full concept.  
- Always conclude each session with a brief summary of what was learned and assign a small set of review questions to reinforce the day's material.
"""

# --- Initialize Session State Defaults ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.1
if "top_p" not in st.session_state:
    st.session_state.top_p = 0.1
if "system_instruction" not in st.session_state:
    st.session_state.system_instruction = default_system_instruction
if "messages" not in st.session_state:
    st.session_state.messages = []
if "locked_access" not in st.session_state:
    st.session_state.locked_access = False
if "uploaded_files_data" not in st.session_state:
    st.session_state.uploaded_files_data = []
if "uploaded_files_names" not in st.session_state:
    st.session_state.uploaded_files_names = []
if "uploaded_files_mime" not in st.session_state:
    st.session_state.uploaded_files_mime = []

# --- End Initialize Session State Defaults ---

st.title("Gemini Flash Chat App")

# File uploader in the sidebar for multiple files
with st.sidebar:
    uploaded_files = st.file_uploader(
        "Upload files (e.g., text, image, video, audio, document, spreadsheet, code)",
        type=[
            # Images
            "jpg", "jpeg", "png", "webp",
            # Videos
            "mp4", "mpeg", "mov", "avi", "wmv", "flv", "webm",
            # Audio
            "mp3", "wav", "ogg", "flac",
            # Documents
            "pdf", "txt", "md",
            # Spreadsheets
            "csv", "tsv", "xls", "xlsx",
            # Word Documents
            "doc", "docx", "rtf", "dot", "dotx",
            # Code
            "c", "cpp", "py", "java", "php", "sql", "html"
        ],
        accept_multiple_files=True
    )

    # Store multiple file data in session state if new files are uploaded
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.uploaded_files_names:
                st.session_state.uploaded_files_data.append(uploaded_file.read())
                st.session_state.uploaded_files_names.append(uploaded_file.name)
                st.session_state.uploaded_files_mime.append(uploaded_file.type)
        st.sidebar.write("Current files:", ", ".join(st.session_state.uploaded_files_names))

# Check if API key is set
if not st.session_state.api_key:
    st.warning("Please unlock and enter your Google API Key on the Settings page.")
else:
    try:
        # Initialize the Generative AI client
        client = genai.Client(api_key=st.session_state.api_key)

        # Define the model
        MODEL_NAME = 'gemini-2.5-flash-preview-04-17'

        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        prompt = st.chat_input("Enter your message")

        if prompt:
            # Prepare message content
            message_parts = []
            message_parts.append(types.Part(text=prompt))
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Include all file data if available
            for i in range(len(st.session_state.uploaded_files_data)):
                file_b64 = base64.b64encode(st.session_state.uploaded_files_data[i]).decode('utf-8')
                message_parts.append(types.Part(
                    inline_data=types.Blob(
                        mime_type=st.session_state.uploaded_files_mime[i],
                        data=file_b64
                    )
                ))
                # Add file info to chat history only if not already present
                if not any(m["content"] == f"Uploaded file: {st.session_state.uploaded_files_names[i]}" for m in st.session_state.messages):
                    st.session_state.messages.append({"role": "user", "content": f"Uploaded file: {st.session_state.uploaded_files_names[i]}"})
                    with st.chat_message("user"):
                        st.markdown(f"Uploaded file: {st.session_state.uploaded_files_names[i]}")

            # Prepare generation config
            chat_config = types.GenerateContentConfig(
                temperature=st.session_state.temperature,
                top_p=st.session_state.top_p,
                system_instruction=st.session_state.system_instruction if st.session_state.locked_access else default_system_instruction,
            )

            # Get model response
            try:
                # Filter and correct history to ensure proper user-model alternation
                history = []
                for m in st.session_state.messages:
                    if m["content"].startswith("Uploaded file:"):
                        continue
                    role = "user" if m["role"] == "user" else "model"  # Convert 'assistant' to 'model'
                    if role == "user" or (history and history[-1].role == "user" and role == "model"):
                        history.append(types.Content(
                            role=role,
                            parts=[types.Part(text=m["content"])]
                        ))

                # If no user messages or history doesn't start with user, initialize with a default user turn
                if not history or history[0].role != "user":
                    history.insert(0, types.Content(
                        role="user",
                        parts=[types.Part(text="Start session")]
                    ))

                # Create chat session
                chat_session = client.chats.create(
                    model=MODEL_NAME,
                    history=history,
                    config=chat_config
                )

                # Send message with text and/or multiple file data as parts
                response = chat_session.send_message(message_parts)

                # Add model response to chat history
                model_response = response.text
                st.session_state.messages.append({"role": "model", "content": model_response})

                # Display assistant response
                with st.chat_message("model"):
                    st.markdown(model_response)

            except Exception as e:
                st.error(f"An error occurred during chat: {e}")

    except Exception as e:
        st.error(f"An error occurred initializing the client: {e}")