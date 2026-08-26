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
# Model list — match on bare family name (Groq's real IDs are inconsistent
# about dashes: "llama3-70b-8192", "gemma2-9b-it", "mixtral-8x7b-32768"),
# and always fall back to a known-good static list so the dropdown is never
# empty even if the API call or filter misbehaves.
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
        chat_models = sorted({
            m.id for m in models.data
            if m.id.lower().startswith(ALLOWED_FAMILIES)
            and not any(kw in m.id.lower() for kw in EXCLUDE_KEYWORDS)
        })
        return chat_models if chat_models else FALLBACK_MODELS
    except Exception:
        return FALLBACK_MODELS

LANGUAGES = ["English", "Spanish", "French", "German", "Japanese", "Arabic", "Portuguese", "Italian"]
ACCENTS = {
    "Amber":  "#E8A33D",
    "Teal":   "#2FB6A6",
    "Violet": "#8B7FD9",
    "Rose":   "#E2657A",
}
MODES = ["Light", "Dark"]

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
    # Using selectboxes (not toggle/radio) on purpose: those two widgets
    # color their checked state with an inline style Streamlit sets from
    # its own default theme, which plain CSS can't reliably override and
    # is what caused the stray red switch/dot last time.
    mode_choice = st.selectbox(
        "Mode", options=MODES,
        index=1 if st.session_state.dark_mode else 0,
    )
    st.session_state.dark_mode = (mode_choice == "Dark")

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
    border = "#3A3A42"
else:
    bg = "#F7F7F5"
    surface = "#FFFFFF"
    surface_soft = "#EDECE8"
    text = "#1A1A1D"
    border = "#D8D7D2"

# ---------------------------------------------------------------------------
# CSS
# Strategy: for each widget, force EVERY descendant's background to
# transparent and text to one color, then paint background/border only on
# the single outer wrapper we choose. That sidesteps guessing at whichever
# nested div/class the installed Streamlit version happens to use — it
# can't leave a stray dark or off-theme box behind because nothing keeps
# its own background. Font-family is scoped to text elements only (not
# `*`), so it doesn't clobber Streamlit's icon-ligature fonts.
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, .stApp {{
    background-color: {bg} !important;
    color: {text} !important;
}}
[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"],
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"], section[data-testid="stSidebar"] {{
    background-color: {bg} !important;
}}
p, span, label, li, a, h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] {{
    color: {text} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}
button, input, textarea, select {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

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

/* Selects — nuke inner layers, paint only the outer box */
div[data-testid="stSelectbox"] * {{
    background-color: transparent !important;
    color: {text} !important;
    border-color: transparent !important;
}}
div[data-testid="stSelectbox"] > div > div {{
    background-color: {surface_soft} !important;
    border-radius: 12px !important;
    box-shadow: inset 0 0 0 1px {border} !important;
}}
div[data-baseweb="popover"] {{
    background-color: {surface} !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15), inset 0 0 0 1px {border} !important;
}}
div[data-baseweb="popover"] * {{
    background-color: transparent !important;
    color: {text} !important;
}}
li[role="option"]:hover, li[aria-selected="true"] {{
    background-color: {surface_soft} !important;
}}

/* Buttons */
[data-testid="stSidebar"] button {{
    border-radius: 999px !important;
    background-color: {surface} !important;
    color: {text} !important;
    box-shadow: inset 0 0 0 1px {border} !important;
    border: none !important;
}}
[data-testid="stSidebar"] button:hover {{
    box-shadow: inset 0 0 0 1.5px {accent} !important;
    color: {accent} !important;
}}
[data-testid="stSidebar"] button p {{ color: inherit !important; }}

/* Info / alert box — match theme instead of Streamlit's default blue */
[data-testid="stAlert"] {{
    background-color: {surface_soft} !important;
    border-radius: 14px !important;
    box-shadow: inset 0 0 0 1px {border} !important;
}}
[data-testid="stAlert"] * {{ color: {text} !important; }}

/* Chat bubbles */
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
    background-color: {surface_soft} !important;
}}
[data-testid="stChatMessageContent"] * {{ color: {text} !important; }}

/* Chat input — seamless pill */
[data-testid="stChatInput"] {{ background-color: {bg} !important; }}
[data-testid="stChatInput"] textarea {{
    border-radius: 22px !important;
    background-color: {surface_soft} !important;
    color: {text} !important;
    box-shadow: inset 0 0 0 1px {border} !important;
    transition: box-shadow 0.15s ease;
}}
[data-testid="stChatInput"] textarea:focus {{
    box-shadow: inset 0 0 0 1.5px {accent}, 0 0 0 4px {accent}22 !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color: {text} !important; opacity: 0.5; }}
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
