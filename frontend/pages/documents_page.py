import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import logging
import os
from components.services.pdf_viewer import fetch_pdf_content, display_pdf
from services.session_store import session_store
from services.authentication import auth

# Configure logging if not already configured
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Backend API base URL
API_BASE_URL = os.getenv("API_BASE_URL")  # Ensure this is set in your environment

if not API_BASE_URL:
    st.error("API_BASE_URL is not set in the environment variables.")

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_publications(api_base_url: str, access_token: str, page: int = 1, per_page: int = 20):
    """Fetch publications from the backend with caching."""
    endpoint = f"{api_base_url}/publications"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "page": page,
        "per_page": per_page
    }
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        raise

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_all_publications(api_base_url: str, access_token: str, per_page: int = 20):
    """Fetch all publications by iterating through all pages with caching."""
    page = 1
    all_publications = []
    
    try:
        data = fetch_publications(api_base_url, access_token, page=page, per_page=per_page)
    except Exception as e:
        raise e

    if not data:
        return all_publications, 0, 0

    total_pages = data.get('total_pages', 1)
    total_count = data.get('total_count', 0)
    
    if 'publications' in data:
        all_publications.extend(data['publications'])
    else:
        logging.error("No 'publications' key found in the response.")
        return all_publications, total_pages, total_count

    for page in range(2, total_pages + 1):
        try:
            data = fetch_publications(api_base_url, access_token, page=page, per_page=per_page)
            if data and 'publications' in data:
                all_publications.extend(data['publications'])
            else:
                logging.warning(f"No publications found on page {page}.")
                break
        except Exception as e:
            logging.error(f"Failed to fetch page {page}: {e}")
            break

    return all_publications, total_pages, total_count

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_image(image_url: str):
    """Fetch and cache images."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        logging.error(f"Error loading image: {e}")
        return None

def display_documents_grid(publications):
    """Display publications in a grid view with cached images."""
    if not publications:
        st.info("No publications available.")
        return

    cols_per_row = 4
    num_rows = (len(publications) + cols_per_row - 1) // cols_per_row

    # Use a container for the grid
    grid_container = st.container()
    
    with grid_container:
        for row in range(num_rows):
            cols = st.columns(cols_per_row)
            for col_index, col in enumerate(cols):
                pub_index = row * cols_per_row + col_index
                if pub_index < len(publications):
                    pub = publications[pub_index]
                    with col:
                        # Use cached image fetch
                        image_data = fetch_image(pub['IMAGE_URL'])
                        if image_data:
                            image = Image.open(image_data)
                            st.image(image, use_column_width=True)
                        else:
                            st.image("https://via.placeholder.com/150", use_column_width=True)

                        st.caption(pub['TITLE'])

                        # Updated button handling
                        if st.button(f"View", key=f"view_{pub['ID']}"):
                            st.session_state['selected_pdf'] = pub['PDF_URL']
                            st.session_state['selected_title'] = pub['TITLE']
                            st.session_state['current_page'] = "PDF Viewer"
                            st.rerun()

def pdf_viewer_page():
    """Main function for the PDF Viewer page with navigation at the top."""
    # Create a container for the back button and title
    header_container = st.container()
    
    with header_container:
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Back to Documents"):
                st.session_state['current_page'] = "Documents"
                st.rerun()
        with col2:
            if 'selected_title' in st.session_state:
                st.header(st.session_state['selected_title'])
            else:
                st.header("PDF Viewer")

    st.markdown("---")

    pdf_url = st.session_state.get('selected_pdf')

    if not pdf_url:
        st.error("No PDF selected to view.")
        return

    with st.spinner("Loading PDF..."):
        try:
            pdf_content = fetch_pdf_content(pdf_url)
            if pdf_content:
                display_pdf(pdf_content, width=800, height=1000)
            else:
                st.error("Failed to load PDF content.")
        except Exception as e:
            st.error(f"An error occurred while fetching the PDF: {e}")

def documents_page():
    """Main function for the documents page with persistent data."""
    st.title("Documents Library")

    access_token = st.session_state.get('access_token')
    if not access_token:
        st.error("Authentication token is missing.")
        return

    # Use a container for the main content
    main_container = st.container()
    
    with main_container:
        # Only fetch publications if they're not in session state or if explicitly refreshing
        if 'publications' not in st.session_state or st.button("Refresh Publications"):
            with st.spinner("Fetching publications..."):
                try:
                    all_publications, total_pages, total_count = fetch_all_publications(API_BASE_URL, access_token)
                    st.session_state['publications'] = all_publications
                    st.session_state['publications_total_pages'] = total_pages
                    st.session_state['publications_total_count'] = total_count
                except Exception as e:
                    st.error(f"Failed to fetch publications: {e}")
                    return

        # Display statistics
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"Total Publications: {st.session_state.get('publications_total_count', 0)}")
        with col2:
            st.success(f"Total Pages: {st.session_state.get('publications_total_pages', 0)}")

        st.markdown("---")  # Separator before search and grid

        # ### Added Search Functionality Start ###
        # Add a search input for filtering publications by title
        search_query = st.text_input("🔍 Search Publications", placeholder="Enter title to search...")

        if search_query:
            # Filter publications based on the search query (case-insensitive)
            filtered_publications = [
                pub for pub in st.session_state['publications']
                if search_query.lower() in pub.get('TITLE', '').lower()
            ]
            st.info(f"Showing results for '{search_query}': {len(filtered_publications)} found.")
        else:
            # If no search query, display all publications
            filtered_publications = st.session_state['publications']
        # ### Added Search Functionality End ###

        # Display the publications grid
        if filtered_publications:
            display_documents_grid(filtered_publications)
        else:
            st.info("No publications match your search.")
    

def home_page():
    """Main function for the Home page."""
    st.header("Welcome to the Home Page")
    st.write("This is the home page of your application.")

def profile_page():
    """Main function for the Profile page."""
    st.header("User Profile")
    st.write("This is the profile page. User details and settings can be managed here.")

def main():
    # Ensure the user is authenticated
    if not session_store.is_authenticated():
        st.warning("Please log in to view the documents.")
        return

    # Initialize session state
    if 'selected_pdf' not in st.session_state:
        st.session_state['selected_pdf'] = None
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = "Home"

    # Render PDF Viewer or main navigation
    if st.session_state['current_page'] == "PDF Viewer":
        pdf_viewer_page()
    else:
        # Sidebar navigation
        st.sidebar.title("Navigation")
        sidebar_pages = ["Home", "Documents", "Profile"]

        # Create radio buttons for navigation
        selected_sidebar_page = st.sidebar.radio(
            "Go to",
            sidebar_pages,
            index=sidebar_pages.index(st.session_state['current_page']) if st.session_state['current_page'] in sidebar_pages else 0
        )

        # Update current_page based on sidebar selection
        if selected_sidebar_page != st.session_state['current_page']:
            st.session_state['current_page'] = selected_sidebar_page
            st.rerun()

        # Render the appropriate page
        if st.session_state['current_page'] == "Home":
            home_page()
        elif st.session_state['current_page'] == "Documents":
            documents_page()
        elif st.session_state['current_page'] == "Profile":
            profile_page()
        else:
            st.error("Unknown page selected.")

    # Logout button in sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        session_store.logout()
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()
