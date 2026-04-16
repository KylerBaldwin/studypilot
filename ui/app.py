import os
import httpx
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.title("StudyPilot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

CANNED = [
    "What courses am I enrolled in?",
    "What assignments do I have coming up?"
]

prompt = None

if not st.session_state.messages:
    cols = st.columns(2)
    for i, question in enumerate(CANNED):
        if cols[i % 3].button(question, use_container_width=True):
            prompt = question

prompt = st.chat_input("Ask about your courses, assignments, or grades...") or prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_box = st.empty()
        response_box = st.empty()
        try:
            with httpx.stream(
                "POST",
                f"{API_URL}/chat",
                json={
                    "message": prompt,
                    "history": st.session_state.messages[:-1],
                },
                timeout=60,
            ) as r:
                r.raise_for_status()
                response = ""
                for chunk in r.iter_text():
                    if chunk.startswith("__status__") and chunk.endswith("__\n"):
                        label = chunk[10:-3]
                        status_box.status(label, state="running")
                    else:
                        status_box.empty()
                        response += chunk
                        response_box.markdown(response)
        except Exception as e:
            response = f"Error: {e}"
            response_box.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
