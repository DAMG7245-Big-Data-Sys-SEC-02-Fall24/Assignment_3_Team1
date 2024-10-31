from fastapi import APIRouter, Depends, Form, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Dict
from app.services.database_service import get_db
from app.services.auth_service import verify_token  # Assuming token validation is handled in auth_service
from app.services.document_service import DocumentService  # Import the service layer
import logging

# Initialize the router for document routes
router = APIRouter()

# Define OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_collection_name(model_type: str):
    """
    Helper function to get the collection name based on model type and GPT model. ["Open Source Extractor", "Closed Source Extractor"],
    """
    if model_type == "Open Source Extractor":
        return f"pdf_collection_pymupdf"
    elif model_type == "Closed Source Extractor":
        return f"pdf_collection_pdfco_fi"
    else:
        raise HTTPException(status_code=400, detail="Invalid model type")

# Route to query document based on a user-provided query
@router.post("/documents/query", tags=["Query"])
async def query_endpoint(
        query: Dict[str, str] = Body(...),
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Endpoint to query a document and pass it for evaluation.
    """
    try:
        # Verify the JWT token
        user_email = verify_token(token)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract query parameters from the request body
        document_name = query.get("document_name")
        query_text = query.get("query_text")
        model_type = query.get("model_type")
        gpt_model = query.get("gpt_model")

        if not document_name or not query_text or not model_type or not gpt_model:
            raise HTTPException(status_code=400, detail="Missing required parameters in request body")

        collection_name = get_collection_name(model_type)

        # Call the document service to retrieve and evaluate the document
        response = DocumentService.query_and_evaluate_document(
            collection_name, document_name, query_text, gpt_model, "Query"
        )

        return {"response": response}

    except Exception as e:
        logging.error(f"An error occurred during the query process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while querying the document: {str(e)}")


# Route to summarize a document and pass it to evaluation service
@router.post("/summarize", tags=["Summary"])
async def summarize_endpoint(
        publication_id: int,
        summary_request: Dict[str, str] = Body(...),
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Endpoint to summarize a document.
    """
    try:
        # Verify the JWT token
        user_email = verify_token(token)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract summary parameters from the request body
        document_name = summary_request.get("document_id")
        model_type = summary_request.get("model_type")
        gpt_model = summary_request.get("gpt_model")

        if not document_name or not model_type or not gpt_model:
            raise HTTPException(status_code=400, detail="Missing required parameters in request body")

        collection_name = get_collection_name(model_type)

        # Call the document service to retrieve and summarize the document
        response = DocumentService.query_and_evaluate_document(
            collection_name, document_name, "", gpt_model, "Summarize"
        )

        return {"summary": response}

    except Exception as e:
        logging.error(f"An error occurred during the summarization process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while summarizing the document: {str(e)}")