
import streamlit as st
from services.session_store import session_store
from services.authentication import auth
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Session state defaults related to authentication
session_defaults = {
    'display_login': True,
    'display_register': False,
}

def initialize_session_state():
    for key, default in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

def clear_session_storage():
    logging.info("Clearing session storage")
    for key, default in session_defaults.items():
        st.session_state[key] = default

def main():
    # Initialize session state
    logging.info("Initializing session state")
    initialize_session_state()

    # Authentication handling
    if not session_store.is_authenticated():
        logging.info("User not authenticated, showing login page")
        login_page()
    else:
        logging.info("User authenticated")
        authenticated_page()

def login_page():
    st.markdown(
        """
        <style>
        .container {
            text-align: center;            
            font-family: Arial, sans-serif;
        }
        .title {
            font-size: 2.5em;
            color: #2E86C1;
            margin-bottom: 10px;
        }
        .features {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .features h3 {
            color: #1A5276;
        }
        .features ul {
            list-style-type: none;
            padding-left: 0;
        }
        .features ul li {
            font-size: 1.1em;
            color: #333;
            margin-bottom: 10px;
            padding-left: 1.5em;
            text-indent: -1.5em;
        }
        .features ul li:before {
            content: '✓';
            margin-right: 10px;
            color: #1ABC9C;
        }
        </style>
        <div class="container">
            <div class="title">Document Query Platform</div>            
            <div class="features">
                <h3>Features available:</h3>
                <ul>
                    <li>Secure Document Summarization and Querying</li>
                    <li>Access to Multiple Document Extractors (Open Source & Enterprise)</li>
                    <li>Seamless Integration with GPT Models for Text Extraction</li>
                    <li>View and Interact with Pre-Processed Documents</li>
                </ul>
            </div>            
        </div>
        """,
        unsafe_allow_html=True
    )

    if session_store.get_value('display_login'):
        display_login_form()
    elif session_store.get_value('display_register'):
        display_register_form()

def display_login_form():
    st.subheader("Login")
    logging.info("Displaying login form")
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submit = st.form_submit_button("Login")

    if submit:
        try:
            logging.info(f"Attempting login for user: {email}")
            auth.login(email, password)
            st.success("Logged in successfully!")
            st.experimental_rerun()
        except Exception as e:
            logging.error(f"Login failed for user {email}: {e}")
            st.error(f"Login failed: {e}")

    st.write("Don't have an account?")
    if st.button("Register"):
        show_register_form()

def display_register_form():
    st.subheader("Register")
    logging.info("Displaying register form")
    with st.form("register_form"):
        username = st.text_input("Username", key="register_username")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        submit = st.form_submit_button("Register")

    if submit:
        try:
            logging.info(f"Attempting registration for user: {email}")
            auth.register(username, email, password)
            st.success("Registered successfully! Please log in.")
            show_login_form()
        except Exception as e:
            logging.error(f"Registration failed for user {email}: {e}")
            st.error(f"Registration failed: {e}")

    st.write("Already have an account?")
    if st.button("Back to Login"):
        show_login_form()

def show_register_form():
    logging.info("Switching to register form")
    session_store.set_value('display_login', False)
    session_store.set_value('display_register', True)
    st.experimental_rerun()

def show_login_form():
    logging.info("Switching to login form")
    session_store.set_value('display_login', True)
    session_store.set_value('display_register', False)
    st.experimental_rerun()

def authenticated_page():
    st.title("Welcome!")
    st.write("You are successfully authenticated.")
    if st.button("Logout"):
        logging.info("Logging out user")
        auth.logout()
        clear_session_storage()
        st.experimental_rerun()

if __name__ == "__main__":
    main()
