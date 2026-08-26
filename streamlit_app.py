import streamlit as st
from groq import Groq

st.set_page_config(page_title="Llama Chat", page_icon="💬", layout="centered")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

with st.sidebar:
    st.markdown("### Settings")
    st.session_state.dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

    model_choice = st.selectbox(
        "Model",
        options=[None, "llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
        format_func=lambda x: "Select a model..." if x is None else x,
        index=0
    )
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if st.session_state.dark_mode:
    bg_color = "#000000"
    bubble_bg = "#1c1c1e"
    text_color = "#f5f5f7"
    sidebar_bg = "#1c1c1e"
    border_color = "#3a3a3c"
    input_text = "#f5f5f7"
else:
    bg_color = "#f5f5f7"
    bubble_bg = "#ffffff"
    text_color = "#1d1d1f"
    sidebar_bg = "#ffffff"
    border_color = "#d2d2d7"
    input_text = "#1d1d1f"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: {bg_color} !important;
    }}

    [data-testid="stHeader"] {{
        background-color: {bg_color} !important;
    }}

    [data-testid="stBottom"], [data-testid="stBottomBlockContainer"], [data-testid="stBottom"] * {{
        background-color: {bg_color} !important;
    }}

    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {{
        color: {text_color} !important;
    }}

    [data-testid="stChatMessage"] {{
        background-color: {bubble_bg} !important;
        border-radius: 18px;
        padding: 12px 16px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        border: none;
    }}
    [data-testid="stChatMessage"] p {{
        color: {text_color} !important;
    }}

    [data-testid="stChatInput"] textarea {{
        border-radius: 20px !important;
        border: 1px solid {border_color} !important;
        background-color: {bubble_bg} !important;
        color: {input_text} !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border_color};
    }}
    section[data-testid="stSidebar"] * {{
        color: {text_color} !important;
    }}

    button {{ border-radius: 20px !important; }}
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] button * {{
        color: #1d1d1f !important;
    }}
</style>
""", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("💬 Llama Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if model_choice is None:
    st.info("Please select a model from the sidebar to start chatting.")
else:
    user_input = st.chat_input("Type your message...")
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=st.session_state.messages
                )
                reply = response.choices[0].message.content
                st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
