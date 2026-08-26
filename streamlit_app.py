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
# Model list (allowlist-driven — safer than an ever-growing exclude list)
# ---------------------------------------------------------------------------
ALLOWED_PREFIXES = ("llama-", "mixtral-", "gemma-", "deepseek-", "qwen-")
ALLOWED_KEYWORDS_EXCLUDE = ("whisper", "tts", "guard", "vision", "audio")

@st.cache_data(ttl=3600)
def get_available_models():
    try:
        models = client.models.list()
        chat_models = [
            m.id for m in models.data
            if m.id.lower().startswith(ALLOWED_PREFIXES)
            and not any(kw in m.id.lower() for kw in ALLOWED_KEYWORDS_EXCLUDE)
        ]
        return sorted(chat_models)
    except Exception:
        return ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]

LANGUAGES = ["English", "Spanish", "French", "German", "Japanese", "Arabic", "Portuguese", "Italian"]

# ---------------------------------------------------------------------------
# Design tokens — pick an accent, both modes derive from it
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
    model_choice = st.selectbox(
        "Model",
        options=[None] + available_models,
        format_func=lambda x: "Select a model..." if x is None else x,
        index=0 if st.session_state.model_choice is None else
              ([None] + available_models).index(st.session_state.model_choice)
              if st.session_state.model_choice in available_models else 0,
    )
    st.session_state.model_choice = model_choice

    language_choice = st.selectbox(
        "Language", options=LANGUAGES,
        index=LANGUAGES.index(st.session_state.language_choice),
    )
    st.session_state.language_choice = language_choice

    st.markdown("### Design")
    st.session_state.dark_mode = st.toggle("Dark mode", value=st.session_state.dark_mode)
    accent_choice = st.radio(
        "Accent", options=list(ACCENTS.keys()),
        index=list(ACCENTS.keys()).index(st.session_state.accent),
        horizontal=True,
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
    text_muted = "#9A9AA2"
    border = "#2E2E35"
else:
    bg = "#F7F7F5"
    surface = "#FFFFFF"
    surface_soft = "#EFEEEA"
    text = "#1A1A1D"
    text_muted = "#7A7A80"
    border = "#E4E3DE"

# ---------------------------------------------------------------------------
# Styling — seamless surfaces, pill input, borderless bubbles
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root, html, body {{
    --background-color: {bg} !important;
    --secondary-background-color: {surface} !important;
    --text-color: {text} !important;
    --primary-color: {accent} !important;
}}

* {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }}

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stHeader"], [data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {{
    background-color: {bg} !important;
    color: {text} !important;
}}

#MainMenu, footer {{ visibility: hidden; }}

/* Header / title */
h1 {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: {bg} !important;
    border-right: 1px solid {border};
}}
section[data-testid="stSidebar"] h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {text_muted} !important;
    margin-top: 1.2rem;
}}

/* Selects — seamless, no boxy border */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    background-color: {surface_soft} !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}}
div[data-baseweb="popover"], ul[role="listbox"] {{
    background-color: {surface} !important;
    border-radius: 12px !important;
    border: 1px solid {border} !important;
}}
ul[role="listbox"] li:hover {{ background-color: {surface_soft} !important; }}

/* Radio pills for accent picker */
[data-testid="stSidebar"] div[role="radiogroup"] {{
    gap: 6px;
}}
[data-testid="stSidebar"] div[role="radiogroup"] label {{
    background-color: {surface_soft};
    border-radius: 999px;
    padding: 2px 10px;
    border: 1px solid transparent;
}}

/* Buttons */
[data-testid="stSidebar"] button {{
    border-radius: 999px !important;
    border: 1px solid {border} !important;
    background-color: {surface} !important;
    color: {text} !important;
}}
[data-testid="stSidebar"] button:hover {{
    border-color: {accent} !important;
    color: {accent} !important;
}}

/* Chat bubbles — no card/box look, just soft tinted surfaces */
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
}}
[data-testid="stChatMessage"]:has(img[alt="user avatar"]) [data-testid="stChatMessageContent"],
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {{
    background-color: {accent}22;
    margin-left: auto;
    border-radius: 18px 18px 4px 18px;
}}
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {{
    background-color: {surface_soft};
    border-radius: 18px 18px 18px 4px;
}}
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {{
    background-color: {surface_soft} !important;
}}

/* Chat input — seamless pill, glows on focus instead of a hard border */
[data-testid="stChatInput"] {{
    background-color: {bg} !important;
    padding-bottom: 0.75rem;
}}
[data-testid="stChatInput"] textarea {{
    border-radius: 22px !important;
    border: none !important;
    background-color: {surface_soft} !important;
    color: {text} !important;
    box-shadow: inset 0 0 0 1px {border};
    transition: box-shadow 0.15s ease;
}}
[data-testid="stChatInput"] textarea:focus {{
    box-shadow: inset 0 0 0 1.5px {accent}, 0 0 0 4px {accent}22 !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {text_muted} !important;
    opacity: 1;
}}
[data-testid="stChatInput"] button {{
    background-color: {accent} !important;
    border-radius: 999px !important;
}}

/* Scrollbar */
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
            placeholder.markdown(f"<span style='color:{text_muted}'>●●● thinking</span>", unsafe_allow_html=True)
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
