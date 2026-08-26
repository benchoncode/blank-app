import re
import streamlit as st
from groq import Groq

st.set_page_config(page_title="BENAITEST", layout="centered")

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
if "mode_choice" not in st.session_state:
    st.session_state.mode_choice = "Light"
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


def strip_think(text: str) -> str:
    """Remove <think>...</think> reasoning blocks some models (e.g. Qwen3)
    emit before their actual answer — the user only wants the answer."""
    if "</think>" in text:
        # Drop everything up to and including the closing tag.
        text = text.split("</think>", 1)[1]
    else:
        # No closing tag found (rare/truncated) — just drop the opening tag
        # itself rather than showing raw reasoning markup.
        text = text.replace("<think>", "")
    return text.strip()


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
    # Options list can shift between reruns (cache expiry, API change) —
    # if the saved model_choice has fallen out of it, reset before the
    # widget reads session_state, so a stale key value can't raise.
    if st.session_state.model_choice not in [None] + available_models:
        st.session_state.model_choice = None
    model_choice = st.selectbox(
        "Model",
        options=[None] + available_models,
        format_func=lambda x: "Select a model..." if x is None else x,
        key="model_choice",
    )

    language_choice = st.selectbox(
        "Language", options=LANGUAGES, key="language_choice",
    )

    st.markdown("### Design")
    mode_choice = st.selectbox(
        "Mode", options=MODES, key="mode_choice",
    )
    accent_choice = st.selectbox(
        "Accent", options=list(ACCENTS.keys()), key="accent",
    )

    st.markdown("")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

accent = ACCENTS[st.session_state.accent]

if st.session_state.mode_choice == "Dark":
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
# ---------------------------------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Chewy&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
html, body, .stApp {{
    background-color: {bg} !important;
    color: {text} !important;
}}

/* Streamlit's own layout wrappers (the padding/column divs around the
   sticky bottom input, in particular) can carry a dark background from
   Streamlit's built-in stylesheet that our earlier, narrower selector
   list didn't reach — which is what left those black boxes flanking the
   chat input. Blanking every div/section back to transparent first, then
   repainting only the specific surfaces we want colored below, removes
   the guesswork about which exact wrapper is responsible. */
[data-testid="stApp"] div, [data-testid="stApp"] section {{
    background-color: transparent !important;
}}
[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"],
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"], section[data-testid="stSidebar"] {{
    background-color: {bg} !important;
}}

/* Text color + font — explicitly excludes icon-glyph spans so material
   icons (sidebar collapse arrow, select chevrons) keep rendering as icons
   instead of showing their raw name as text. */
p, span:not([data-testid="stIconMaterial"]), label, li, a,
h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] {{
    color: {text} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}
button, input, textarea, select {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}
span[data-testid="stIconMaterial"] {{ color: {text} !important; }}

#MainMenu, footer {{ visibility: hidden; }}

h1, [data-testid="stHeading"] h1, [data-testid="stMarkdownContainer"] h1 {{
    font-family: 'Chewy', cursive !important;
    font-weight: 400 !important;
    color: {accent} !important;
    letter-spacing: 0.01em;
}}
section[data-testid="stSidebar"] h3 {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.65;
    margin-top: 1.2rem;
}}

/* Sidebar collapse control — style it as a visible, labeled button
   instead of a bare (and previously broken) icon */
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"] {{
    background-color: {surface_soft} !important;
    border-radius: 10px !important;
    box-shadow: inset 0 0 0 1px {border} !important;
    padding: 4px 8px !important;
}}
[data-testid="stSidebarCollapseButton"] *, [data-testid="stSidebarCollapsedControl"] * {{
    color: {text} !important;
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

/* Info / alert box */
[data-testid="stAlert"] {{
    background-color: {surface_soft} !important;
    border-radius: 14px !important;
    box-shadow: inset 0 0 0 1px {border} !important;
}}
[data-testid="stAlert"] * {{ color: {text} !important; }}

/* Chat messages — no avatars; role is shown via alignment + tint instead.
   Messages always alternate user, assistant in the order we append them,
   so nth-of-type is a reliable way to tell them apart without needing an
   avatar element to key off of. */
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {{
    display: none !important;
}}
[data-testid="stChatMessage"] {{
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 4px 0 !important;
    width: 100% !important;
    display: flex !important;
    gap: 0 !important;
}}
[data-testid="stChatMessageContent"] {{
    border-radius: 18px;
    padding: 10px 16px;
    max-width: 78%;
    line-height: 1.5;
}}
[data-testid="stChatMessageContent"] * {{ color: {text} !important; }}

[data-testid="stChatMessage"]:nth-of-type(odd) {{ justify-content: flex-end; }}
[data-testid="stChatMessage"]:nth-of-type(odd) [data-testid="stChatMessageContent"] {{
    background-color: {accent}22 !important;
    border-radius: 18px 18px 4px 18px;
}}
[data-testid="stChatMessage"]:nth-of-type(even) {{ justify-content: flex-start; }}
[data-testid="stChatMessage"]:nth-of-type(even) [data-testid="stChatMessageContent"] {{
    background-color: {surface_soft} !important;
    border-radius: 18px 18px 18px 4px;
}}

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

st.title("BENAITEST")

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
            placeholder.markdown("···")
            try:
                system_prompt = {
                    "role": "system",
                    "content": (
                        f"Always respond only in {language_choice}, regardless of what "
                        "language the user writes in, unless they explicitly ask you to switch languages. "
                        "Do not show your reasoning or thinking process — reply with only the final answer."
                    ),
                }
                api_messages = [system_prompt] + st.session_state.messages
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=api_messages,
                )
                raw_reply = response.choices[0].message.content
                reply = strip_think(raw_reply)
            except Exception as e:
                reply = f"Error: {e}"
            placeholder.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
