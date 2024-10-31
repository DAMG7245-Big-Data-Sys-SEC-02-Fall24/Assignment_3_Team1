from fastapi import APIRouter, Depends, HTTPException, Body, Path, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.services.database_service import get_db
from app.services.auth_service import verify_token
from app.services.document_service import DocumentService
import logging

# Initialize the router for API v1 document routes
router = APIRouter()

# Define OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Configure logging
logging.basicConfig(level=logging.INFO)


# POST /api/v1/documents/process
@router.post("/documents/process", tags=["Documents"])
async def process_documents(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Process new documents from Snowflake. This is an asynchronous operation with status tracking.
    """
    try:
        # Verify the JWT token
        await auth_verify(token)

        # Call the document service to process documents asynchronously
        response = DocumentService.process_new_documents()
        return {"status": "Processing initiated", "details": response}

    except Exception as e:
        logging.error(f"Error while processing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Error while processing documents")


async def auth_verify(token):
    user_email = verify_token(token)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# GET /api/v1/documents
@router.get("/documents", tags=["Documents"])
async def list_documents(
        token: str = Depends(oauth2_scheme),
        page: int = Query(1, description="Page number for pagination"),
        limit: int = Query(10, description="Number of documents per page"),
        filter: Optional[str] = Query(None, description="Optional filter criteria"),
        db: Session = Depends(get_db)
):
    """
    List available documents with pagination and optional filtering.
    """
    try:
        # Verify the JWT token
        await auth_verify(token)

        # Calculate the offset for pagination
        offset = (page - 1) * limit

        # Call the publication service to get a paginated list of publications
        publications, total_count = PublicationService.list_publications(db, offset, limit, filter)

        # Return the paginated response
        return {
            "publications": publications,
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": (total_count + limit - 1) // limit  # Calculate total pages
        }

    except Exception as e:
        logging.error(f"Error listing publications: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing publications")

# POST /api/v1/query
@router.post("/query", tags=["Query"])
async def general_rag_query(
        query_request: Dict[str, str] = Body(...),
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    General RAG query endpoint that returns responses with source citations.
    """
    try:
        # Verify the JWT token
        user_email = verify_token(token)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract query parameters
        query_text = query_request.get("query_text")
        gpt_model = query_request.get("gpt_model")

        if not query_text or not gpt_model:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        # Call the document service to process the query
        response = DocumentService.general_rag_query(query_text, gpt_model)
        return {"response": response}

    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing query")


# POST /api/v1/documents/{document_id}/query
@router.post("/documents/{document_id}/query", tags=["Query"])
async def document_specific_query(
        document_id: str = Path(..., description="ID of the document to query"),
        query_request: Dict[str, str] = Body(...),
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Document-specific query endpoint that constrains context to a single document.
    """
    try:
        # Verify the JWT token
        user_email = verify_token(token)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract query parameters
        query_text = query_request.get("query_text")
        gpt_model = query_request.get("gpt_model")

        if not query_text or not gpt_model:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        # Call the document service to query the specific document
        response = DocumentService.document_specific_query(document_id, query_text, gpt_model)
        return {"response": response}

    except Exception as e:
        logging.error(f"Error processing document-specific query: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing document-specific query")


# GET /api/v1/conversations
@router.get("/conversations", tags=["Conversations"])
async def list_conversations(
        token: str = Depends(oauth2_scheme),
        document_id: Optional[str] = Query(None, description="Filter by document ID"),
        db: Session = Depends(get_db)
):
    """
    List conversation history, with optional filtering by document.
    """
    try:
        # Verify the JWT token
        user_email = verify_token(token)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Call the document service to list conversations
        conversations = DocumentService.list_conversations(document_id)
        return {"conversations": conversations}

    except Exception as e:
        logging.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing conversations")


# POST /api/v1/conversations/{conversation_id}/notes
@router.post("/conversations/{conversation_id}/notes", tags=["Conversations"])
async def generate_notes_from_conversation(
        conversation_id: str = Path(..., description="ID of the conversation"),
        notes_request: Dict[str, str] = Body(...),
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Generate PDF notes from a conversation with custom formatting.
    """
    try:
        # Verify the JWT token
        user_email = verify_token(token)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract custom formatting parameters
        formatting_options = notes_request.get("formatting_options")

        # Call the document service to generate notes from the conversation
        response = DocumentService.generate_notes_from_conversation(conversation_id, formatting_options)
        return {"notes": response}

    except Exception as e:
        logging.error(f"Error generating notes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating notes")