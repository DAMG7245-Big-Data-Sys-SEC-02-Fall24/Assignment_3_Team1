# document_actions_page.py
import streamlit as st
import logging
from components.services.pdf_viewer import fetch_pdf_content, display_pdf

def process_document_action(action, doc_content):
    if action == "Summarize":
        with st.spinner("Generating summary..."):
            # Implement actual summarization logic here
            return "Document summary will be displayed here..."
            
    elif action == "Query":
        query = st.text_input("Enter your query about the document:")
        if query:
            with st.spinner("Processing query..."):
                # Implement actual query logic here
                return f"Query results for: {query}"
                
    elif action == "Generate Report":
        report_type = st.selectbox(
            "Select report type:", 
            ["Executive Summary", "Detailed Analysis", "Key Findings"]
        )
        if st.button("Generate"):
            with st.spinner(f"Generating {report_type}..."):
                # Implement actual report generation logic here
                return f"{report_type} will be generated..."
    return None

def display_document_actions(doc_title, doc_content):
    """Handle actions for a selected document"""
    st.subheader(f"Selected Document: {doc_title}")
    
    action = st.selectbox(
        "Choose an action:",
        ["Select an action...", "Summarize", "View", "Query", "Generate Report"]
    )
    
    if action != "Select an action...":
        if action == "View":
            st.session_state['current_page'] = "PDF Viewer"
            st.rerun()
        else:
            result = process_document_action(action, doc_content)
            if result:
                st.markdown("### Results")
                st.write(result)

def document_actions_page():
    st.title("Document Actions")
    
    # Check if a document is selected
    selected_title = st.session_state.get('selected_title')
    selected_pdf = st.session_state.get('selected_pdf')
    
    # Conditional rendering: Only display dropdown if a document is selected
    if not selected_title:
        st.warning("Please select a document from the Documents page.")
        
        # Button to redirect to Documents page if no document is selected
        if st.button("Go to Documents Page", key="go_to_docs"):
            st.session_state['current_page'] = "Documents"
            st.rerun()
        return  # Exit the function early if no document is selected
    
    # Display actions for the selected document
    display_document_actions(selected_title, selected_pdf)
    
    # Option to clear the selection
    if st.button("Clear Selection", key="clear_selection"):
        st.session_state.pop('selected_title', None)
        st.session_state.pop('selected_pdf', None)
        st.rerun()
