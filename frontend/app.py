# app.py
import streamlit as st
from app_pages.home import home_page
from app_pages.pdf_gallery import pdf_gallery_page


# Configure the Streamlit page
st.set_page_config(
    page_title="Multimodal RAG App",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
def load_css():
    with open("styles/styles.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Sidebar Navigation with icons
st.sidebar.title("📱 Navigation")
page = st.sidebar.radio("", ["🏠 Home", "📚 PDF Gallery"])

if page == "🏠 Home":
    home_page()
elif page == "📚 PDF Gallery":
    pdf_gallery_page()
