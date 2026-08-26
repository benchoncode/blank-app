import streamlit as st
from groq import Groq

st.set_page_config(page_title="Llama Chat", page_icon="🦙", layout="centered")

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "accent" not in st.session_state:
    st.session_state.accent = "Amber"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_choice" not in st.session_state:
    st.session_state.model_choice = None
if "language_choice" not in st.session_state:
    st.session_state.language_choice = "English"

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ---------------------------------------------------------------------------
# Model list
# Bug last time: prefixes like "llama-" don't match Groq's real IDs, which
# are things like "llama3-70b-8192", "llama-3.1-8b-instant", "gemma2-9b-it",
# "mixtral-8x7b-32768" — inconsistent dash placement. Match on the bare
# family name instead, and always fall back to a known-good static list so
# the dropdown is never empty even if the API call or filter goes wrong.
# ---------------------------------------------------------------------------
ALLOWED_FAMILIES = ("llama", "mixtral", "gemma", "deepseek", "qwen")
EXCLUDE_KEYWORDS = ("whisper", "tts", "guard", "vision", "audio")
FALLBACK_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

@st.cache_data(ttl=3600)
def get_available_models():
    try:
        models = client.models.list()
        chat_models = [
            m.id for m in models.data
            if m.id.lower().startswith(ALLOWED_FAMILIES)
            and not any(kw in m.id.lower() for kw in EXCLUDE_KEYWORDS)
        ]
        chat_models = sorted(set(chat_models))
        return chat_models if chat_models else FALLBACK_MODELS
    except Exception:
        return FALLBACK_MODELS

LANGUAGES = ["English", "Spanish", "French", "German", "Japanese", "Arabic", "Portuguese", "Italian"]

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
ACCENTS = {
    "Amber":  "#E8A33D",
    "Teal":   "#2FB6A6",
    "Violet": "#8B7FD9",
    "Rose":   "#E2657A",
}

with st.sidebar:
    st.markdown("### Chat")
    available_models = get_available_models()
    default_index = (
        available_models.index(st.session_state.model_choice) + 1
        if st.session_state.model_choice in available_models else 0
    )
    model_choice = st.selectbox(
        "Model",
        options=[None] + available_models,
        format_func=lambda x: "Select a model..." if x is None else x,
        index=default_index,
    )
    st.session_state.model_choice = model_choice

    language_choice = st.selectbox(
        "Language", options=LANGUAGES,
        index=LANGUAGES.index(st.session_state.language_choice),
    )
    st.session_state.language_choice = language_choice

    st.markdown("### Design")
    st.session_state.dark_mode = st.toggle("Dark mode", value=st.session_state.dark_mode)
    accent_choice = st.selectbox(
        "Accent", options=list(ACCENTS.keys()),
        index=list(ACCENTS.keys()).index(st.session_state.accent),
    )
    st.session_state.accent = accent_choice

    st.markdown("")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

accent = ACCENTS[st.session_state.accent]

if st.session_state.dark_mode:
    bg = "#16161A"
    surface = "#1F1F24"
    surface_soft = "#26262C"
    text = "#F2F1EE"
    border = "#34343B"
else:
    bg = "#F7F7F5"
    surface = "#FFFFFF"
    surface_soft = "#EDECE8"
    text = "#1A1A1D"
    border = "#D8D7D2"

# ---------------------------------------------------------------------------
# Native theming — this is what actually keeps toggles, radios, selects,
# focus rings, etc. consistent, instead of chasing every widget's internal
# markup by hand with CSS (which breaks across Streamlit versions and is
# why the model box and switches looked disconnected from the accent last
# time). Streamlit reads these at the start of each rerun.
# ---------------------------------------------------------------------------
st.set_option("theme.base", "dark" if st.session_state.dark_mode else "light")
st.set_option("theme.primaryColor", accent)
st.set_option("theme.backgroundColor", bg)
st.set_option("theme.secondaryBackgroundColor", surface_soft)
st.set_option("theme.textColor", text)

# ---------------------------------------------------------------------------
# CSS — only for the custom chat surface. Everything else (selects, toggle,
# radio, buttons, focus states) now comes from theme.* above, so text and
# widget color stay a single consistent value in each mode.
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

* {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }}

#MainMenu, footer {{ visibility: hidden; }}

h1 {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}}

section[data-testid="stSidebar"] h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.65;
    margin-top: 1.2rem;
}}

[data-testid="stSidebar"] button {{ border-radius: 999px !important; }}

/* Chat bubbles — borderless, tinted by role instead of boxed */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 4px 0 !important;
}}
[data-testid="stChatMessageContent"] {{
    border-radius: 18px;
    padding: 10px 16px;
    max-width: 78%;
    line-height: 1.5;
    background-color: {surface_soft};
}}

/* Chat input — seamless pill, glows on focus instead of a hard border */
[data-testid="stChatInput"] textarea {{
    border-radius: 22px !important;
    background-color: {surface_soft} !important;
    box-shadow: inset 0 0 0 1px {border};
    transition: box-shadow 0.15s ease;
}}
[data-testid="stChatInput"] textarea:focus {{
    box-shadow: inset 0 0 0 1.5px {accent}, 0 0 0 4px {accent}22 !important;
}}
[data-testid="stChatInput"] button {{
    background-color: {accent} !important;
    border-radius: 999px !important;
}}

::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-thumb {{ background: {border}; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

st.title("🦙 Llama Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if model_choice is None:
    st.info("Select a model in the sidebar to start chatting.")
else:
    user_input = st.chat_input("Type your message...")
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("●●● thinking")
            try:
                system_prompt = {
                    "role": "system",
                    "content": (
                        f"Always respond only in {language_choice}, regardless of what "
                        "language the user writes in, unless they explicitly ask you to switch languages."
                    ),
                }
                api_messages = [system_prompt] + st.session_state.messages
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=api_messages,
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"Error: {e}"
            placeholder.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
