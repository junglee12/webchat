import streamlit as st

DEFAULT_SESSION_STATE = {
    'api_key': '',
    'temperature': 0.1, # Default from app.py
    'top_p': 0.1,       # Default from app.py
    'system_instruction': '',
    'messages': [],
    'locked_access': False,
    'uploaded_files_data': [],
    'uploaded_files_names': [],
    'uploaded_files_mime': [],
    'file_uploader_key': 0
}

# Specific defaults for settings.py if they differ, otherwise, they can use the same.
# For this case, temperature and top_p have different defaults in settings.py
# when it initializes its own state, if we want to keep that distinction,
# we might need a slightly more complex setup or ensure settings.py calls this
# with its specific defaults if it's meant to be independent.
# However, the current plan implies a unified initialization.
# Let's assume app.py's defaults are the primary ones for now.
# If settings.py needs different initial defaults before user interaction,
# that page can override them after calling this function.

DEFAULT_SETTINGS_SPECIFIC_STATE = {
    'temperature': 0.7, # Default from settings.py description
    'top_p': 0.95,      # Default from settings.py description
}

def initialize_session_state(defaults=None):
    """
    Initializes Streamlit session state variables if they don't exist.
    Uses DEFAULT_SESSION_STATE and optionally updates with page-specific defaults.
    """
    # Start with general defaults
    current_defaults = DEFAULT_SESSION_STATE.copy()

    # If page-specific defaults are provided, merge them.
    # Page-specific values will override general defaults.
    if defaults:
        current_defaults.update(defaults)

    for key, value in current_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def initialize_app_session_state():
    """Initializes session state for the main app."""
    # app.py uses the main DEFAULT_SESSION_STATE directly
    initialize_session_state()

def initialize_settings_session_state():
    """Initializes session state for the settings page."""
    # settings.py has different initial defaults for temperature and top_p
    # We pass these as overrides to the general defaults.
    settings_defaults = {
        'api_key': '', # Ensure all keys from DEFAULT_SESSION_STATE are considered
        'temperature': DEFAULT_SETTINGS_SPECIFIC_STATE.get('temperature', DEFAULT_SESSION_STATE['temperature']),
        'top_p': DEFAULT_SETTINGS_SPECIFIC_STATE.get('top_p', DEFAULT_SESSION_STATE['top_p']),
        'system_instruction': '',
        'messages': [],
        'locked_access': False, # This is False in settings.py too if not yet unlocked
        'uploaded_files_data': [],
        'uploaded_files_names': [],
        'uploaded_files_mime': [],
        'file_uploader_key': 0
    }
    initialize_session_state(defaults=settings_defaults)
