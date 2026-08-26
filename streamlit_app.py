import streamlit as st
import ollama

st.set_page_config(page_title="Llama Chat", page_icon="💬", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp { background-color: #f5f5f7; }
    h1 { font-weight: 600; color: #1d1d1f; letter-spacing: -0.02em; }
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 12px 16px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: none;
    }
    [data-testid="stChatInput"] textarea {
        border-radius: 20px !important;
        border: 1px solid #d2d2d7 !important;
        background-color: #ffffff !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e5ea;
    }
    button { border-radius: 20px !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Settings")
    model_choice = st.selectbox(
        "Model",
        options=[None, "llama3.1", "codellama", "qwen2.5-coder"],
        format_func=lambda x: "Select a model..." if x is None else x,
        index=0
    )
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

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
                response = ollama.chat(
                    model=model_choice,
                    messages=st.session_state.messages
                )
                reply = response['message']['content']
                st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
