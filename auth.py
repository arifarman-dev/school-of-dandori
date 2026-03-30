import hashlib
import streamlit as st

def check_credentials(username: str, password: str) -> bool:
    correct_user = username == st.secrets["ADMIN_USERNAME"]
    correct_hash = hashlib.sha256(password.encode()).hexdigest() == st.secrets["ADMIN_PASSWORD"]
    return correct_user and correct_hash  # both must pass

def login_form():
    st.subheader("Admin login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid username or password")

def require_auth():
    if not st.session_state.get("authenticated"):
        login_form()
        st.stop()