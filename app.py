# app.py

import streamlit as st
from agent import run_agent

st.set_page_config(page_title="Memory AI", layout="wide")

st.title("🧠 Memory AI Agent")
st.caption("AI that remembers and evolves")

# ---------------- SESSION STATE ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "memory" not in st.session_state:
    st.session_state.memory = None

if "fact" not in st.session_state:
    st.session_state.fact = None

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([2, 1])

# ---------------- CHAT ----------------
with col1:
    user_input = st.chat_input("Ask something...")

    if user_input:
        st.session_state.chat.append(("user", user_input))

        answer, fact, memory = run_agent(user_input)

        st.session_state.chat.append(("assistant", answer))
        st.session_state.memory = memory
        st.session_state.fact = fact

    for role, msg in st.session_state.chat:
        st.chat_message(role).write(msg)

# ---------------- MEMORY PANEL ----------------
with col2:
    st.subheader("🧠 Memory")

    if st.session_state.memory:
        st.write("### Retrieved")

        facts = st.session_state.memory.get("interpreted", {}).get("key_facts", [])

        if not facts:
            st.info("No memory stored yet.")

        for i, fact in enumerate(facts):
            st.write(f"🧠 {fact}")

            col_edit, col_delete = st.columns(2)

            # ✏️ EDIT
            with col_edit:
                new_text = st.text_input("Edit", key=f"edit_{i}")
                if st.button("Update", key=f"update_{i}"):
                    from membrain_client import update_memory
                    update_memory(i, content=new_text)
                    st.success("Updated!")

            # 🗑️ DELETE
            with col_delete:
                if st.button("Delete", key=f"delete_{i}"):
                    from membrain_client import delete_memory
                    delete_memory(i)
                    st.warning("Deleted!")

    # ---------------- STORED FACT ----------------
    if st.session_state.fact:
        st.write("### Stored")
        st.success(st.session_state.fact)
