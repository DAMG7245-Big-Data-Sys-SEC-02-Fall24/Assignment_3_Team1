# pages/home.py
import streamlit as st
from components.ui.card import pdf_card

def home_page():
    st.title("🚀 Multimodal RAG App")
    
    # Modern card layout for features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pdf_card(
            title="📥 Data Retrieval",
            description="Seamlessly fetch and manage data from various sources with advanced integration capabilities."
        )
    
    with col2:
        pdf_card(
            title="🎯 Interactive UI",
            description="Modern and intuitive interface designed for enhanced user experience and productivity."
        )
    
    with col3:
        pdf_card(
            title="⚡ Scalable Architecture",
            description="Built with FastAPI and Streamlit for optimal performance and future scalability."
        )
