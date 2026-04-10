# streamlit_app.py

import streamlit as st
import requests
import uuid

API_URL = "http://127.0.0.1:8003/chat"

st.set_page_config(page_title="AI Agent Chatbot", layout="centered")

st.title("🤖 AI Agent Chatbot")
st.caption("Powered by FastAPI + Azure OpenAI + Tools")

# -------------------------
# Session Management (Frontend)
# -------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------
# Display chat history
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# User Input
# -------------------------
user_input = st.chat_input("Type your message...")

if user_input:

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Call FastAPI
    try:
        response = requests.post(
            API_URL,
            json={
                "session_id": st.session_state.session_id,
                "message": user_input
            },
            timeout=30
        )

        if response.status_code == 200:
            bot_reply = response.json()["response"]
        else:
            bot_reply = f"Error: {response.text}"

    except Exception as e:
        bot_reply = f"Connection error: {str(e)}"

    # Show assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })

    with st.chat_message("assistant"):
        st.markdown(bot_reply)