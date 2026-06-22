import streamlit as st

from codhem.config.settings import get_settings
from codhem.services.auth_service import require_registered_user
from codhem.services.llm_chat_service import generate_assistant_reply

PAGE_TITLE = "MCDC LLM"
PAGE_SUMMARY = "Ask questions, explore literature records, and run supported materials-model services from one chat interface."
WELCOME_MESSAGE = (
    "Welcome to MCDC LLM. Available services include literature record lookup "
    "from the materials database and RHEA-DOS-E predictions for supported alloy "
    "compositions. Ask a question to get started."
)


def initialize_session_state():
    if "mcdc_llm_messages" in st.session_state:
        return

    llm_settings = get_settings().llm
    st.session_state["mcdc_llm_messages"] = [
        {"role": "system", "content": llm_settings.system_prompt},
        {"role": "assistant", "content": WELCOME_MESSAGE},
    ]


def get_messages():
    return st.session_state["mcdc_llm_messages"]


def display_messages():
    for message in get_messages():
        if message["role"] == "system":
            continue

        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def validate_llm_settings():
    llm_settings = get_settings().llm

    if not llm_settings.api_key or llm_settings.api_key == "YOUR_RCD_LLM_KEY_HERE":
        st.error(
            "Set `llm.api_key` in `config.toml` before using the MCDC LLM page."
        )
        st.stop()

    return llm_settings


require_registered_user()

llm_settings = validate_llm_settings()
initialize_session_state()

st.title(PAGE_TITLE)
st.caption(PAGE_SUMMARY)
display_messages()

prompt = st.chat_input("Send a message")
if prompt:
    get_messages().append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                reply = generate_assistant_reply(get_messages())
        except Exception as exc:
            st.error(f"Request failed: {exc}")
        else:
            st.markdown(reply)
            get_messages().append({"role": "assistant", "content": reply})
