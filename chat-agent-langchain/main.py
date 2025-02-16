import streamlit as st
from src.ui.streamlit_app import StreamlitUI
from src.auth.auth_handler import AuthHandler

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        auth_handler = AuthHandler()
        if auth_handler.authenticate_user(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid username or password")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        # Add logout button in sidebar
        with st.sidebar:
            st.write(f"Logged in as: {st.session_state.username}")
            if st.button("Logout"):
                logout()
        
        app = StreamlitUI()
        app.run()

if __name__ == "__main__":
    main() 