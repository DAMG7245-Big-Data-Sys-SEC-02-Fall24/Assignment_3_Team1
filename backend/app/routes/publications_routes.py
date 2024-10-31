from fastapi import APIRouter, Depends, HTTPException, Body, Query
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional

from pydantic import BaseModel

from app.models.publication import Publication
from app.services.PublicationService import PublicationService  # Assuming the `PublicationService` is in this module
from app.services.auth_service import verify_token  # Assuming token validation is handled in auth_service
import logging

# Initialize the router for publication routes
router = APIRouter()

# Define OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Configure loggingx
logging.basicConfig(level=logging.INFO)

class PaginatedResponse(BaseModel):
    total_count: int
    total_pages: int
    current_page: int
    per_page: int
    next_page: Optional[int]
    previous_page: Optional[int]
    publications: List[dict]
# Dependency to get the service
def get_publication_service():
    return PublicationService()


# Helper to verify the token and get the user email
def get_current_user(token: str = Depends(oauth2_scheme)):
    user_email = verify_token(token)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_email


# Route to create a new publication
@router.post("/publications", tags=["Publications"])
async def create_publication(
        title: str = Body(...),
        summary: str = Body(...),
        image_url: str = Body(...),
        pdf_url: str = Body(...),
        token: str = Depends(oauth2_scheme),
        publication_service: PublicationService = Depends(get_publication_service)
):
    """Create a new publication."""
    try:
        # Verify token
        user_email = get_current_user(token)

        # Create publication
        publication_service.create_publication(title, summary, image_url, pdf_url)
        return {"message": "Publication created successfully"}

    except Exception as e:
        logging.error(f"Error while creating publication: {str(e)}")
        raise HTTPException(status_code=500, detail="Error while creating publication")


# Route to retrieve all publications with pagination
@router.get("/publications", tags=["Publications"], response_model=PaginatedResponse)
async def get_publications(
        page: int = Query(1, description="Page number"),
        per_page: int = Query(10, description="Number of publications per page"),
        token: str = Depends(oauth2_scheme),
        publication_service: PublicationService = Depends(get_publication_service)
):
    """Retrieve all publications with pagination."""
    try:
        # Verify token
        user_email = get_current_user(token)

        # Fetch publications with pagination
        logging.info(f"Fetching publications for page {page} and per_page {per_page}")
        publications = publication_service.get_all_publications(page=page, per_page=per_page)
        return publications

    except Exception as e:
        logging.error(f"Error while fetching publications: {str(e)}")
        raise HTTPException(status_code=500, detail="Error while fetching publications")


# Route to retrieve a single publication by ID
@router.get("/publications/{publication_id}", tags=["Publications"], response_model=dict)
async def get_publication_by_id(
        publication_id: int,
        token: str = Depends(oauth2_scheme),
        publication_service: PublicationService = Depends(get_publication_service)
):
    """Retrieve a publication by ID."""
    try:
        # Verify token
        user_email = get_current_user(token)

        # Fetch publication by ID
        publication = publication_service.get_publication_by_id(publication_id)
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")
        return publication

    except Exception as e:
        logging.error(f"Error while fetching publication: {str(e)}")
        raise HTTPException(status_code=500, detail="Error while fetching publication")


# Route to update an existing publication
@router.put("/publications/{publication_id}", tags=["Publications"])
async def update_publication(
        publication_id: int,
        title: Optional[str] = Body(None),
        summary: Optional[str] = Body(None),
        image_url: Optional[str] = Body(None),
        pdf_url: Optional[str] = Body(None),
        token: str = Depends(oauth2_scheme),
        publication_service: PublicationService = Depends(get_publication_service)
):
    """Update an existing publication by ID."""
    try:
        # Verify token
        user_email = get_current_user(token)

        # Fetch the publication to ensure it exists
        publication = publication_service.get_publication_by_id(publication_id)
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")

        # Update the publication
        publication_service.update_publication(publication_id, title, summary, image_url, pdf_url)
        return {"message": "Publication updated successfully"}

    except Exception as e:
        logging.error(f"Error while updating publication: {str(e)}")
        raise HTTPException(status_code=500, detail="Error while updating publication")


# Route to delete a publication by ID
@router.delete("/publications/{publication_id}", tags=["Publications"])
async def delete_publication(
        publication_id: int,
        token: str = Depends(oauth2_scheme),
        publication_service: PublicationService = Depends(get_publication_service)
):
    """Delete a publication by ID."""
    try:
        # Verify token
        user_email = get_current_user(token)

        # Fetch the publication to ensure it exists
        publication = publication_service.get_publication_by_id(publication_id)
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")

        # Delete the publication
        publication_service.delete_publication(publication_id)
        return {"message": "Publication deleted successfully"}

    except Exception as e:
        logging.error(f"Error while deleting publication: {str(e)}")
        raise HTTPException(status_code=500, detail="Error while deleting publication")

