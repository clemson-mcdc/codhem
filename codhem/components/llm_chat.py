import streamlit as st

from codhem.config.settings import get_settings
from codhem.services.auth_service import require_registered_user
from codhem.services.llm_chat_service import (
    build_system_prompt,
    generate_assistant_reply,
)


def render_llm_chat(
    *,
    page_id,
    title,
    summary,
    welcome_message,
    page_instructions,
    tools,
):
    require_registered_user()

    llm_settings = get_settings().llm
    if not llm_settings.api_key or llm_settings.api_key == "YOUR_RCD_LLM_KEY_HERE":
        st.error("Set `llm.api_key` in `config.toml` before using the LLM page.")
        st.stop()

    messages_key = f"llm_messages_{page_id}"
    if messages_key not in st.session_state:
        st.session_state[messages_key] = [
            {
                "role": "system",
                "content": build_system_prompt(
                    llm_settings.system_prompt,
                    page_instructions,
                ),
            },
            {"role": "assistant", "content": welcome_message},
        ]

    messages = st.session_state[messages_key]

    st.title(title)
    st.caption(summary)
    for message in messages:
        if message["role"] == "system":
            continue

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Send a message", key=f"llm_input_{page_id}")
    if prompt:
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    reply = generate_assistant_reply(messages, tools)
            except Exception as exc:
                st.error(f"Request failed: {exc}")
            else:
                st.markdown(reply)
                messages.append({"role": "assistant", "content": reply})
